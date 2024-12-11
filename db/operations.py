from datetime import datetime
from typing import List

from db import Task, User
from config import logger
from peewee import OperationalError, DatabaseError, PeeweeException


# Tasks
def create_task(category_url: str, target_category: str) -> bool:
    try:
        Task.create(
            source_url=category_url,
            target_category=target_category,
            start=datetime.now(),
            status='running'
        )
        logger.info(f'Task successfully created for URL: {category_url}')
        return True
    except Exception as e:
        logger.exception(f'Error creating task: {e}')
        return False


def get_current_task(category_url):
    try:
        task = (Task.select()
                .where(Task.source_url == category_url, Task.status == 'running')
                .order_by(Task.start.desc())
                .first())
        return task
    except OperationalError as ex:
        logger.exception(f"Database connection issue: {ex}")
    except DatabaseError as ex:
        logger.exception(f"Database query error: {ex}")
        return


def task_error(task):
    try:
        task.status = 'error'
        task.save()
    except OperationalError as ex:
        logger.exception(f"Database connection issue: {ex}")
    except DatabaseError as ex:
        logger.exception(f"Database query error: {ex}")
        return None


def task_finish(task):
    try:
        task.end = datetime.now()
        task.status = 'finish'
        task.save()
    except OperationalError as ex:
        logger.exception(f"Database connection issue: {ex}")
    except DatabaseError as ex:
        logger.exception(f"Database query error: {ex}")
        return


def task_warning(task):
    try:
        task.status = 'warning'
        task.save()
    except OperationalError as ex:
        logger.exception(f"Database connection issue: {ex}")
    except DatabaseError as ex:
        logger.exception(f"Database query error: {ex}")
        return


# Users
async def db_get_user_list() -> List[User] | None:
    try:
        user_list = User.select()
        return user_list
    except PeeweeException as e:
        logger.exception(f'Database query error: {e}')
        return None


async def db_get_admin_list() -> List[User] | None:
    try:
        query = User.select().where(User.is_admin)
        admin_list: List[User] = list(query)
        return admin_list
    except PeeweeException as e:
        logger.exception(f'Database query error: {e}')
        return None


async def db_add_user(tg_user_id: str) -> str | None:
    if not tg_user_id.isdigit():
        return None
    try:
        User.get_or_create(tg_user_id=tg_user_id,
                           is_admin=False)
        return 'User added successfully'
    except PeeweeException as e:
        logger.exception(f'Database query error: {e}')
        return None


async def db_delete_user(tg_user_id: str) -> str | None:
    if not tg_user_id.isdigit():
        return None
    try:
        user_to_delete = User.get_or_none(User.tg_user_id == tg_user_id)
        if user_to_delete:
            user_to_delete.delete_instance()
            return 'User deleted successfully'
        else:
            logger.warning(f'User not found')
    except PeeweeException as e:
        logger.exception(f'Database query error: {e}')
        return None


async def db_set_admin(tg_user_id: str) -> str | None:
    if not tg_user_id.isdigit():
        return None
    try:
        user_to_update = User.get_or_none(User.tg_user_id == tg_user_id)
        if user_to_update:
            user_to_update.is_admin = True
            user_to_update.save()
            return 'Status updated successfully'
        else:
            logger.warning(f'User not found')
    except PeeweeException as e:
        logger.exception(f'Database query error: {e}')
        return None


async def db_remove_admin(tg_user_id: str) -> str | None:
    if not tg_user_id.isdigit():
        return None
    try:
        user_to_update = User.get_or_none(User.tg_user_id == tg_user_id)
        if user_to_update:
            user_to_update.is_admin = False
            user_to_update.save()
            return 'Status updated successfully'
        else:
            logger.warning(f'User not found')
    except PeeweeException as e:
        logger.exception(f'Database query error: {e}')
        return None
