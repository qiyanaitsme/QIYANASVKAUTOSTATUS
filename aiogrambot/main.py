from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import json
from handlers import status_manager, vk_auth

def main():
    with open('config.json', 'r') as f:
        config = json.load(f)

    bot = Bot(token=config['telegram_token'])
    dp = Dispatcher(bot, storage=MemoryStorage())

    status_manager.vk = vk_auth(config['vk_token'])

    from handlers import register_handlers
    register_handlers(dp)

    executor.start_polling(dp, skip_updates=True)

if __name__ == '__main__':
    main()
