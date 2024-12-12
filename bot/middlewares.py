from aiogram import BaseMiddleware, Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, TelegramObject
from typing import Callable, Dict, Any, Awaitable, Union
from peewee import DoesNotExist

from config import logger, parser_config
from db import User, Task
from bot.text import BOT_MESSAGES


class AllowedUsersMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot, *args, **kwargs):
        self.bot = bot
        super().__init__(*args, **kwargs)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        try:
            if isinstance(event, (Message, CallbackQuery)):
                user_id = str(event.from_user.id) if event.from_user else None
                if user_id:
                    User.get(User.tg_user_id == user_id)
                    return await handler(event, data)
            return await handler(event, data)
        except DoesNotExist:
            logger.warning(f'Unknown user - {event.from_user.id}')
            if isinstance(event, (Message, CallbackQuery)):
                await self.bot.send_message(
                    chat_id=parser_config.SUPERADMIN,
                    text=f'Login attempt blocked\n'
                         f'id: {event.from_user.id},\n'
                         f'username: @{event.from_user.username}\n'
                         f'name: {event.from_user.first_name} {event.from_user.last_name}'
                )
                await event.answer(BOT_MESSAGES.get('unknown_user'))
            return


class TaskCheckMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data: dict):
        if isinstance(event, CallbackQuery) and event.data in {'parse', 'run'}:
            active_task = Task.select().where(Task.status == 'running').first()
            if active_task:
                await event.answer(
                    BOT_MESSAGES.get('task_in_progress'),
                    show_alert=True
                )
                return
        return await handler(event, data)


def setup_middlewares(dp: Dispatcher, bot: Bot):
    dp.message.outer_middleware(AllowedUsersMiddleware(bot=bot))
    dp.callback_query.outer_middleware(AllowedUsersMiddleware(bot=bot))
    dp.callback_query.middleware(TaskCheckMiddleware())
