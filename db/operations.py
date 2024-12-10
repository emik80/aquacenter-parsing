from datetime import datetime

from db import Task
from config import logger


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
    except Exception as ex:
        logger.exception(f'Error getting task {ex}')
        return


def task_error(task):
    try:
        task.status = 'error'
        task.save()
    except Exception as ex:
        logger.exception(f'Error task update {ex}')
        return None


def task_finish(task):
    try:
        task.end = datetime.now()
        task.status = 'finish'
        task.save()
    except Exception as ex:
        logger.exception(f'Error task update {ex}')
        return
