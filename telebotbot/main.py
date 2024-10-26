import telebot
import json
from handlers import status_manager, vk_auth

def main():
    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)

    bot = telebot.TeleBot(config['telegram_token'])

    status_manager.vk = vk_auth(config['vk_token'])

    from handlers import register_handlers
    register_handlers(bot)

    bot.infinity_polling(skip_pending=True)

if __name__ == '__main__':
    main()
