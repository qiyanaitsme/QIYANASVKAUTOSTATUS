import telebot
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
import json
import asyncio
import threading
import time
from keyboards import get_main_keyboard, get_settings_keyboard, get_templates_keyboard
from vk_service import vk_auth, create_status

state_storage = StateMemoryStorage()

class Settings(StatesGroup):
    waiting_for_vk_token = State()
    waiting_for_interval = State()

class StatusManager:
    def __init__(self):
        self.is_status_running = False
        self.current_thread = None
        self.vk = None

status_manager = StatusManager()

def status_updater(template_id):
    print(f"[DEBUG] Starting status updater with template {template_id}")
    while status_manager.is_status_running:
        try:
            if status_manager.vk:
                status = create_status(status_manager.vk, template_id)
                print(f"[INFO] Status successfully updated: {status}")
            else:
                print("[ERROR] VK API not initialized")
                break

            with open('config.json', 'r') as f:
                config = json.load(f)
            time.sleep(config['status_update_interval'])
        except Exception as e:
            print(f"[ERROR] Status update failed: {e}")
            break

def register_handlers(bot):
    @bot.message_handler(commands=['start'])
    def start_command(message):
        with open('config.json', 'r') as f:
            config = json.load(f)
        if message.from_user.id != config['allowed_user_id']:
            return
        bot.send_message(message.chat.id, "🌟 Добро пожаловать в Auto Status Bot! 🌟", 
                        reply_markup=get_main_keyboard())

    @bot.callback_query_handler(func=lambda call: call.data == "settings")
    def settings_menu(call):
        bot.edit_message_text("⚙️ Настройки", 
                            call.message.chat.id, 
                            call.message.message_id,
                            reply_markup=get_settings_keyboard())

    @bot.callback_query_handler(func=lambda call: call.data == "change_vk_token")
    def change_vk_token(call):
        bot.set_state(call.from_user.id, Settings.waiting_for_vk_token, call.message.chat.id)
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main"))
        bot.edit_message_text("📝 Отправьте новый токен VK:", 
                            call.message.chat.id,
                            call.message.message_id,
                            reply_markup=keyboard)

    @bot.message_handler(state=Settings.waiting_for_vk_token)
    def process_vk_token(message):
        with open('config.json', 'r') as f:
            config = json.load(f)
        if message.from_user.id != config['allowed_user_id']:
            return

        new_token = message.text
        status_manager.vk = vk_auth(new_token)

        if status_manager.vk:
            config['vk_token'] = new_token
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)
            bot.send_message(message.chat.id, "✅ Токен VK успешно обновлен!")
        else:
            bot.send_message(message.chat.id, "❌ Неверный токен VK!")

        bot.delete_state(message.from_user.id, message.chat.id)

    @bot.callback_query_handler(func=lambda call: call.data == "change_interval")
    def change_interval(call):
        bot.set_state(call.from_user.id, Settings.waiting_for_interval, call.message.chat.id)
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main"))
        bot.edit_message_text("⏱ Введите новый интервал обновления в секундах:",
                            call.message.chat.id,
                            call.message.message_id,
                            reply_markup=keyboard)

    @bot.message_handler(state=Settings.waiting_for_interval)
    def process_interval(message):
        with open('config.json', 'r') as f:
            config = json.load(f)
        if message.from_user.id != config['allowed_user_id']:
            return

        try:
            new_interval = int(message.text)
            if new_interval < 30:
                bot.send_message(message.chat.id, "⚠️ Интервал не может быть меньше 30 секунд!")
                return

            config['status_update_interval'] = new_interval
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)
            bot.send_message(message.chat.id, f"✅ Интервал обновления установлен на {new_interval} секунд!")
        except ValueError:
            bot.send_message(message.chat.id, "❌ Пожалуйста, введите число!")

        bot.delete_state(message.from_user.id, message.chat.id)

    @bot.callback_query_handler(func=lambda call: call.data == "start_status")
    def start_status_menu(call):
        bot.edit_message_text("Выберите шаблон статуса:",
                            call.message.chat.id,
                            call.message.message_id,
                            reply_markup=get_templates_keyboard())

    @bot.callback_query_handler(func=lambda call: call.data.startswith("template_"))
    def process_template(call):
        template_id = int(call.data.split("_")[1])

        if not status_manager.vk:
            bot.edit_message_text("❌ Сначала установите токен VK в настройках!",
                                call.message.chat.id,
                                call.message.message_id)
            return

        status_manager.is_status_running = True
        if status_manager.current_thread:
            status_manager.is_status_running = False
            status_manager.current_thread.join()

        status_manager.current_thread = threading.Thread(target=status_updater, args=(template_id,))
        status_manager.current_thread.start()

        with open('config.json', 'r') as f:
            config = json.load(f)

        test_status = create_status(status_manager.vk, template_id)
        if test_status:
            bot.edit_message_text(
                f"✅ Автостатус запущен с шаблоном {template_id}\nОбновление каждые {config['status_update_interval']} секунд",
                call.message.chat.id,
                call.message.message_id
            )
        else:
            bot.edit_message_text("❌ Ошибка при обновлении статуса. Проверьте токен VK.",
                                call.message.chat.id,
                                call.message.message_id)

    @bot.callback_query_handler(func=lambda call: call.data == "stop_status")
    def stop_status(call):
        status_manager.is_status_running = False
        if status_manager.current_thread:
            status_manager.current_thread.join()
            status_manager.current_thread = None
        bot.edit_message_text("❌ Автостатус остановлен",
                            call.message.chat.id,
                            call.message.message_id)

    @bot.callback_query_handler(func=lambda call: call.data == "back_to_main")
    def back_to_main(call):
        bot.edit_message_text("Главное меню",
                            call.message.chat.id,
                            call.message.message_id,
                            reply_markup=get_main_keyboard())