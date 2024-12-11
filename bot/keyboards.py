from aiogram import Bot
from aiogram.types import BotCommand, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.text import MENU_COMMANDS


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


def reply_kb_builder(buttons, width=2):
    kb_builder = ReplyKeyboardBuilder()
    kb_builder.row(*buttons, width=width)
    return kb_builder


# Buttons
add_user_btn = KeyboardButton(text='Add User')
del_user_btn = KeyboardButton(text='Del User')
set_admin_btn = KeyboardButton(text='Set as Admin')
del_admin_btn = KeyboardButton(text='Remove Admin')
get_user_list_btn = KeyboardButton(text='User List')
get_admin_list_btn = KeyboardButton(text='Admin List')
exit_btn = KeyboardButton(text='Exit')

# Keyboards
admin_kb = reply_kb_builder(buttons=[add_user_btn, del_user_btn, set_admin_btn, del_admin_btn,
                                     get_user_list_btn, get_admin_list_btn, exit_btn],
                            width=2).as_markup(resize_keyboard=True,)