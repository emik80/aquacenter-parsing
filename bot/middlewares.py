from aiogram import BaseMiddleware, Bot
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable
from peewee import DoesNotExist

from config import logger, parser_config
from db import User
from text import BOT_MESSAGES


class AllowedUsersMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot, *args, **kwargs):
        self.bot = bot
        super().__init__(*args, **kwargs)

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        try:
            User.get(User.tg_user_id == str(event.from_user.id))
            return await handler(event, data)
        except DoesNotExist:
            logger.warning(f'Unknown user - {event.from_user.id}')
            await self.bot.send_message(chat_id=parser_config.SUPERADMIN,
                                        text=f'Login attempt blocked\n'
                                             f'id: {event.from_user.id},\n'
                                             f'username: @{event.from_user.username}\n'
                                             f'name: {event.from_user.first_name} {event.from_user.last_name}')
            await event.answer(BOT_MESSAGES['unknown_user'])
