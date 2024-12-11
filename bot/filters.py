from typing import Any

from aiogram.filters import BaseFilter
from aiogram.types import Message
from peewee import DoesNotExist

from config import logger
from db import User
from text import BOT_MESSAGES, ADMIN_MESSAGES


class IsAdminFilter(BaseFilter):
    async def __call__(
        self,
        event: Message,
    ) -> Any:
        try:
            user = User.get(User.tg_user_id == str(event.from_user.id))
            if user.is_admin:
                return True
            else:
                await event.answer(text=f"{ADMIN_MESSAGES.get('not_admin')}")
                logger.warning(f'Admin access denied - {user}')
                return False
        except DoesNotExist:
            logger.warning(f'Admin access warning - {event.from_user.id}')
            await event.answer(text=f"{BOT_MESSAGES.get('unknown_user')}")
