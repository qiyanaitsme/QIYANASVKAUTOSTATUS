from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import json
import asyncio
from keyboards import get_main_keyboard, get_settings_keyboard, get_templates_keyboard
from vk_service import vk_auth, create_status


class Settings(StatesGroup):
    waiting_for_vk_token = State()
    waiting_for_interval = State()


class StatusManager:
    def __init__(self):
        self.is_status_running = False
        self.current_task = None
        self.vk = None


status_manager = StatusManager()


async def status_updater(template_id):
    print(f"[DEBUG] Starting status updater with template {template_id}")
    while status_manager.is_status_running:
        try:
            if status_manager.vk:
                status = await create_status(status_manager.vk, template_id)
                print(f"[INFO] Status successfully updated: {status}")
            else:
                print("[ERROR] VK API not initialized")
                break

            with open('config.json', 'r') as f:
                config = json.load(f)
            await asyncio.sleep(config['status_update_interval'])
        except Exception as e:
            print(f"[ERROR] Status update failed: {e}")
            break


async def start_command(message: types.Message):
    with open('config.json', 'r') as f:
        config = json.load(f)
    if message.from_user.id != config['allowed_user_id']:
        return
    await message.answer("🌟 Добро пожаловать в Auto Status Bot! 🌟", reply_markup=get_main_keyboard())


async def settings_menu(call: types.CallbackQuery):
    await call.message.edit_text("⚙️ Настройки", reply_markup=get_settings_keyboard())


async def change_vk_token(call: types.CallbackQuery):
    await Settings.waiting_for_vk_token.set()
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main"))
    await call.message.edit_text("📝 Отправьте новый токен VK:", reply_markup=keyboard)


async def process_vk_token(message: types.Message, state: FSMContext):
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
        await message.answer("✅ Токен VK успешно обновлен!")
    else:
        await message.answer("❌ Неверный токен VK!")

    await state.finish()


async def change_interval(call: types.CallbackQuery):
    await Settings.waiting_for_interval.set()
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main"))
    await call.message.edit_text("⏱ Введите новый интервал обновления в секундах:", reply_markup=keyboard)


async def process_interval(message: types.Message, state: FSMContext):
    with open('config.json', 'r') as f:
        config = json.load(f)
    if message.from_user.id != config['allowed_user_id']:
        return

    try:
        new_interval = int(message.text)
        if new_interval < 30:
            await message.answer("⚠️ Интервал не может быть меньше 30 секунд!")
            return

        config['status_update_interval'] = new_interval
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)
        await message.answer(f"✅ Интервал обновления установлен на {new_interval} секунд!")
    except ValueError:
        await message.answer("❌ Пожалуйста, введите число!")

    await state.finish()


async def start_status_menu(call: types.CallbackQuery):
    await call.message.edit_text("Выберите шаблон статуса:", reply_markup=get_templates_keyboard())


async def process_template(call: types.CallbackQuery):
    template_id = int(call.data.split("_")[1])

    if not status_manager.vk:
        await call.message.edit_text("❌ Сначала установите токен VK в настройках!")
        return

    status_manager.is_status_running = True
    if status_manager.current_task:
        status_manager.current_task.cancel()

    status_manager.current_task = asyncio.create_task(status_updater(template_id))

    with open('config.json', 'r') as f:
        config = json.load(f)

    test_status = await create_status(status_manager.vk, template_id)
    if test_status:
        await call.message.edit_text(
            f"✅ Автостатус запущен с шаблоном {template_id}\nОбновление каждые {config['status_update_interval']} секунд"
        )
    else:
        await call.message.edit_text("❌ Ошибка при обновлении статуса. Проверьте токен VK.")


async def stop_status(call: types.CallbackQuery):
    status_manager.is_status_running = False
    if status_manager.current_task:
        status_manager.current_task.cancel()
        status_manager.current_task = None
    await call.message.edit_text("❌ Автостатус остановлен")


async def back_to_main(call: types.CallbackQuery):
    await call.message.edit_text("Главное меню", reply_markup=get_main_keyboard())


def register_handlers(dp):
    dp.register_message_handler(start_command, commands=['start'])
    dp.register_callback_query_handler(settings_menu, lambda c: c.data == "settings")
    dp.register_callback_query_handler(change_vk_token, lambda c: c.data == "change_vk_token")
    dp.register_callback_query_handler(change_interval, lambda c: c.data == "change_interval")
    dp.register_callback_query_handler(start_status_menu, lambda c: c.data == "start_status")
    dp.register_callback_query_handler(process_template, lambda c: c.data.startswith("template_"))
    dp.register_callback_query_handler(stop_status, lambda c: c.data == "stop_status")
    dp.register_callback_query_handler(back_to_main, lambda c: c.data == "back_to_main")
    dp.register_message_handler(process_vk_token, state=Settings.waiting_for_vk_token)
    dp.register_message_handler(process_interval, state=Settings.waiting_for_interval)
