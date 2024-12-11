from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter

from config import logger
from bot.filters import IsAdminFilter
from bot.text import ADMIN_MESSAGES
from bot.keyboards import admin_kb
from bot.states import FSMAdmin
from db import db_add_user, db_delete_user, db_set_admin, db_remove_admin, db_get_admin_list, db_get_user_list

router = Router()
router.message.filter(F.chat.type.in_({"private"}))


# Test Admin
@router.message(Command(commands='admin'), IsAdminFilter())
async def process_command_help(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(FSMAdmin.admin)
    await message.answer(text=ADMIN_MESSAGES.get('hello'),
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
async def process_get_user_list(message: Message):
    user_list = await db_get_user_list()
    if user_list:
        users = ['Admins marked *',]
        for user in user_list:
            admin_marker = '*' if user.is_admin else ''
            users.append(f'{user.tg_user_id}{admin_marker}')
        await message.answer(
            text='\n'.join(users),
            reply_markup=admin_kb,
        )
        logger.success(f'[ADMIN] The User-list requested by the user {message.from_user.id} was sent successfully')
    else:
        await message.answer(
            text='⚠ ERROR: db_get_user_list',
            reply_markup=admin_kb
        )


# Get Admin List
@router.message(F.text.in_({'Admin List', }),
                IsAdminFilter(), StateFilter(FSMAdmin.admin))
async def process_get_admin_list(message: Message):
    admin_list = await db_get_admin_list()
    if admin_list:
        message_text = '\n'.join([user.tg_user_id for user in admin_list])
        await message.answer(
            text=message_text,
            reply_markup=admin_kb,
        )
        logger.success(f'[ADMIN] The Admin-list requested by the user {message.from_user.id} was sent successfully')
    else:
        await message.answer(
            text='⚠ ERROR: db_get_user_list',
            reply_markup=admin_kb
        )


# Exit to user mode
@router.message(F.text.in_({'Exit'}), IsAdminFilter(),
                StateFilter(FSMAdmin.admin, FSMAdmin.enter_id))
async def process_remove_admin(message: Message, state: FSMContext):
    await state.clear()
    text = ADMIN_MESSAGES.get('logout')
    await message.answer(text=text, reply_markup=ReplyKeyboardRemove())


# Processing user ID
@router.message(StateFilter(FSMAdmin.enter_id), IsAdminFilter())
async def get_tg_userid(message: Message, state: FSMContext):
    tg_user_id = message.text.strip()
    user_data = await state.get_data()
    process_type = user_data['process_type']
    status = None
    match process_type:
        case 'Add User':
            status = await db_add_user(tg_user_id)
        case 'Del User':
            status = await db_delete_user(tg_user_id)
        case 'Set as Admin':
            status = await db_set_admin(tg_user_id)
        case 'Remove Admin':
            status = await db_remove_admin(tg_user_id)
    if status:
        logger.success(f'[ADMIN] {status}. Error with this operation')
        await message.answer(text=f'🟢 {status}. {ADMIN_MESSAGES.get('done')}',
                             reply_markup=admin_kb)
    else:
        await message.answer(text=f'🔴 {status}. {ADMIN_MESSAGES.get('error')}',
                             reply_markup=admin_kb)
    await state.set_state(FSMAdmin.admin)
