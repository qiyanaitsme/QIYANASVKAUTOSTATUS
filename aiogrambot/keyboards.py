from aiogram import types

def get_main_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("🔄 Запустить автостатус", callback_data="start_status"))
    keyboard.add(types.InlineKeyboardButton("⚙️ Настройки", callback_data="settings"))
    keyboard.add(types.InlineKeyboardButton("❌ Остановить", callback_data="stop_status"))
    return keyboard

def get_settings_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("🔑 Изменить токен VK", callback_data="change_vk_token"))
    keyboard.add(types.InlineKeyboardButton("⏱ Изменить интервал", callback_data="change_interval"))
    keyboard.add(types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main"))
    return keyboard

def get_templates_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(f"Шаблон {i}", callback_data=f"template_{i}")
        for i in range(1, 7)
    ]
    keyboard.add(*buttons)
    keyboard.add(types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main"))
    return keyboard
