import os
import tempfile

from aiogram import Router, F, Bot, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter

from config import logger
from filters import IsAdminFilter
from text import ADMIN_MESSAGES
from keyboards import admin_kb
from db import db_add_user, db_delete_user, db_set_admin, db_remove_admin, db_get_admin_list, db_get_user_list
from states import FSMAdmin

router = Router()
router.message.filter(F.chat.type.in_({"private"}))


# Test Admin
@router.message(Command(commands='admin'), IsAdminFilter())
async def process_command_help(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(FSMAdmin.admin)
    await message.answer(text=ADMIN_MESSAGES['hello'],
                         reply_markup=admin_kb)


# Add User, Delete User, Set as admin, Remove admin
@router.message(F.text.in_({'Add User', 'Del User', 'Set as Admin', 'Remove Admin'}),
                IsAdminFilter(), StateFilter(FSMAdmin.admin))
async def process_add_user(message: Message, state: FSMContext):
    await state.set_state(FSMAdmin.enter_id)
    await state.update_data(process_type=message.text)
    text = 'Enter User ID'
    await message.answer(text=text, reply_markup=ReplyKeyboardRemove())


# Get User List
@router.message(F.text.in_({'User List', }),
                IsAdminFilter(), StateFilter(FSMAdmin.admin))
async def process_get_user_list(message: Message, bot: Bot):
    chat_id = message.from_user.id
    user_list = await db_get_user_list(bot, chat_id)
    if user_list:
        try:
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as temp_file:
                for user in user_list:
                    admin_marker = '*' if user.is_admin else ''
                    temp_file.write(f'{user.tg_user_id}{admin_marker}\n')
                temp_file.flush()
                input_file = types.FSInputFile(path=temp_file.name)
                await bot.send_document(
                    chat_id=chat_id,
                    caption='✅ User List',
                    document=input_file,
                    reply_markup=admin_kb,
                )
            logger.success(f'[ADMIN] The User-list requested by the user {chat_id} was sent successfully')
        except Exception as e:
            logger.warning(f'[ADMIN] Error sending user_list: {e}')
        finally:
            os.remove(temp_file.name)


# Get Admin List
@router.message(F.text.in_({'Admin List', }),
                IsAdminFilter(), StateFilter(FSMAdmin.admin))
async def process_get_user_list(message: Message, bot: Bot):
    chat_id = message.from_user.id
    admin_list = await db_get_admin_list(bot, chat_id)
    if admin_list:
        try:
            message_text = "\n".join([user.tg_user_id for user in admin_list])
            await bot.send_message(
                text=message_text,
                chat_id=chat_id,
                reply_markup=admin_kb,
            )
            logger.success(f'[ADMIN] The Admin-list requested by the user {chat_id} was sent successfully')
        except Exception as e:
            logger.warning(f'[ADMIN] Error sending admin_list: {e}')


# Exit to user mode
@router.message(F.text.in_({'Exit'}), IsAdminFilter(),
                StateFilter(FSMAdmin.admin, FSMAdmin.enter_id))
async def process_remove_admin(message: Message, state: FSMContext):
    await state.clear()
    text = ADMIN_MESSAGES['logout']
    await message.answer(text=text, reply_markup=ReplyKeyboardRemove())


# Processing user ID
@router.message(StateFilter(FSMAdmin.enter_id), IsAdminFilter())
async def get_tg_userid(message: Message, state: FSMContext, bot: Bot):
    chat_id = message.from_user.id
    tg_user_id = message.text
    user_data = await state.get_data()
    process_type = user_data['process_type']
    status = None
    match process_type:
        case 'Add User':
            status = await db_add_user(tg_user_id, bot, chat_id)
        case 'Del User':
            status = await db_delete_user(tg_user_id, bot, chat_id)
        case 'Set as Admin':
            status = await db_set_admin(tg_user_id, bot, chat_id)
        case 'Remove Admin':
            status = await db_remove_admin(tg_user_id, bot, chat_id)
    if status:
        await message.answer(text=f'🟢 {process_type} {ADMIN_MESSAGES["done"]}',
                             reply_markup=admin_kb)
    await state.set_state(FSMAdmin.admin)
