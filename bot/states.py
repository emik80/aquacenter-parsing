from aiogram.fsm.state import StatesGroup, State


class FSMCommon(StatesGroup):
    active = State('Active')
    enter_url = State('Enter URL')
    enter_category = State('Enter category')
    run = State('Run')


class FSMAdmin(StatesGroup):
    admin = State('Admin')
    enter_id = State('Enter ID')
