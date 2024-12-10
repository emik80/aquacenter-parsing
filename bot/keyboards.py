from aiogram import Bot
from aiogram.types import BotCommand
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from text import MENU_COMMANDS


# Menu Button
async def set_main_menu(bot: Bot):
    main_menu_commands = [BotCommand(
                                command=command,
                                description=description
                          ) for command, description in MENU_COMMANDS.items()]
    await bot.set_my_commands(main_menu_commands)


def create_inline_kb(width: int = 1, **kwargs: str) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []

    if kwargs:
        for button, text in kwargs.items():
            buttons.append(InlineKeyboardButton(
                text=text,
                callback_data=button))

    kb_builder.row(*buttons, width=width)

    return kb_builder.as_markup()
