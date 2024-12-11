import asyncio

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramNetworkError
from aiogram.fsm.storage.redis import RedisStorage, Redis

import bot.handlers as user_handlers
import bot.admin as admin
from bot.middlewares import setup_middlewares
from bot.keyboards import set_main_menu
from config import logger, parser_config
from db import db, initialize_database


@logger.catch
async def main():
    logger.info('Starting bot')
    initialize_database(db)
    bot = Bot(token=parser_config.BOT_TOKEN)
    redis = Redis(host=parser_config.REDIS_HOST)
    storage = RedisStorage(redis=redis)
    dp = Dispatcher(storage=storage)

    await set_main_menu(bot)
    setup_middlewares(dp, bot)
    dp.include_router(admin.router)
    dp.include_router(user_handlers.router)
    logger.info('READY')

    while True:
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)
        except TelegramNetworkError as ex:
            logger.exception(f'[BOT EXCEPTION]: Error occurred: {ex}. Restarting the bot...')
            await asyncio.sleep(5)
        except Exception as ex:
            logger.exception(f'[BOT EXCEPTION]: Unexpected error occurred: {ex}. Exiting...')
            break


if __name__ == '__main__':
    asyncio.run(main())
