import time
from typing import Union

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.filters import CommandStart, Command, StateFilter

from config import logger, parser_config
from text import BOT_MESSAGES
from keyboards import create_inline_kb
from states import FSMCommon, FSMAdmin


router = Router()
router.message.filter(F.chat.type.in_({"private"}))
router.callback_query.filter(F.message.chat.type.in_({"private"}))


# Help
@router.message(Command(commands='help'))
async def process_command_help(message: Message):
    await message.answer(text=BOT_MESSAGES['help'])


# Start
@router.message(CommandStart())
async def process_command_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(FSMCommon.active)
    await state.update_data(user_id=message.from_user.id,
                            username=message.from_user.username)
    kb = create_inline_kb(
        parse='✅ Парсер'
    )
    await message.answer(text=BOT_MESSAGES.get('start'),
                         reply_markup=kb)


# Cancel
@router.message(F.text.in_({'/cancel'}))
@router.callback_query(F.data == 'cancel')
async def process_command_cancel(event: Union[Message, CallbackQuery], state: FSMContext):
    text = BOT_MESSAGES.get('cancel_selected')
    kb = create_inline_kb(
        parse='✅ Парсер'
    )
    if isinstance(event, Message):
        message = event
        await message.answer(text=text,
                             reply_markup=kb)
    else:  # CallbackQuery
        message = event.message
        await event.message.edit_text(text=text, reply_markup=kb)
        await event.answer()
    await state.clear()
    await state.update_data(
        user_id=message.from_user.id,
        username=message.from_user.username
    )
    await state.set_state(FSMCommon.active)


# Parsing
@router.callback_query(F.data == 'parse', StateFilter(FSMCommon.active))
async def process_command_parsing(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await state.set_state(FSMCommon.enter_url)
    text = BOT_MESSAGES.get('source url')
    await callback.message.answer(text=text)


# Enter URL
@router.message(StateFilter(FSMCommon.enter_url))
async def process_url(message: Message, state: FSMContext):
    category_url = message.text
    await state.update_data(category_url=category_url)
    text = BOT_MESSAGES.get('target category')
    await state.set_state(FSMCommon.enter_category)
    await message.answer(text=text)


# Enter category
@router.message(StateFilter(FSMCommon.enter_category))
async def process_category(message: Message, state: FSMContext):
    target_category = message.text
    await state.update_data(target_category=target_category)
    user_data = await state.get_data()
    text = (f'Введені дані:\n'
            f'URL: {user_data.get("category_url")}\n'
            f'Категорія для додавання товарів:\n{user_data.get("target_category")}')
    await state.set_state(FSMCommon.run)
    kb = create_inline_kb(
        2,
        run='✅ Почати',
        cancel='❌ Скасувати'
    )
    await message.answer(text=text, reply_markup=kb)


@router.callback_query(F.data == 'run', StateFilter(FSMCommon.run))
async def process_command_run(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    print('RUN')
    message = await callback.message.answer(text='Парсинг запущено')
    ...
    await state.clear()
    await state.update_data(user_id=callback.message.from_user.id,
                            username=callback.message.from_user.username)
    await state.set_state(FSMCommon.active)
    kb = create_inline_kb(
        parse='✅ Парсер'
    )
    await message.edit_text(text='DONE', reply_markup=kb)


# Other messages
@router.message(StateFilter(FSMCommon.active), ~StateFilter(FSMAdmin.admin))
async def send_error(message: Message):
    try:
        await message.answer(text=BOT_MESSAGES.get('error'))
        await message.delete()
    except TypeError as ex:
        await message.reply(text=BOT_MESSAGES.get('error'))
        logger.warning(ex)


@router.message(StateFilter(default_state))
async def send_echo(message: Message):
    try:
        await message.reply(text=f"handler {BOT_MESSAGES.get('unknown')}")
    except TypeError as ex:
        await message.reply(text=f"handler {BOT_MESSAGES.get('error')}")
        logger.warning(ex)
