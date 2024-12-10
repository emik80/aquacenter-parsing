from datetime import datetime

from config import logger
import parser as parser
from db import Task
from db import operations as db_operations


@logger.catch
def parser_core(category_url, target_category):
    logger.info(f'START: Parsing of category {category_url} into {target_category}')
    db_operations.create_task(category_url=category_url,
                              target_category=target_category)

    current_task = db_operations.get_current_task(category_url)
    if not current_task:
        db_operations.task_error(current_task)
        logger.error(f'Error {category_url} STEP 1')
        return

    step_2 = parser.collect_product_list(current_task, category_url)
    if not step_2:
        db_operations.task_error(current_task)
        logger.error(f'Category {category_url} STEP 2')
        return

    step_3 = parser.processing_product_list(current_task)
    if not step_3:
        db_operations.task_error(current_task)
        logger.error(f'Category {category_url} STEP 3')
        return

    output_filename = parser.process_csv(current_task)
    if not output_filename:
        db_operations.task_error(current_task)
        logger.error(f'Category {category_url} STEP 4')
        return

    db_operations.task_finish(current_task)
    return output_filename
