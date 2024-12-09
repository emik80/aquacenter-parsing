import asyncio

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramNetworkError

import handlers
from middlewares import AllowedUsersMiddleware
from config import logger, parser_config
from db import db, initialize_database


@logger.catch
async def main():
    logger.info('Starting bot')
    initialize_database(db)
    bot = Bot(token=parser_config.BOT_TOKEN)
    logger.info('Bot initialized')

    dp = Dispatcher()
    logger.info('Dispatcher initialized')

    # Set Menu Button
    # await set_main_menu(bot)
    # logger.info('Main menu set')

    # Middlewares registration
    dp.message.outer_middleware(AllowedUsersMiddleware(bot=bot))
    logger.info('Middlewares registered')

    # Routers registration
    # dp.include_router(admin.router)
    dp.include_router(handlers.router)
    logger.info('Routers registered')

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
