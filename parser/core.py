from datetime import datetime

from config import logger
import service as service_tools
import parser as parser
from db import Task


@logger.catch
def parser_core(category_url, target_category):
    logger.info(f'START: Parsing of category {category_url} into {target_category}')
    try:
        Task.create(
            source_url=category_url,
            target_category=target_category,
            start=datetime.now(),
            status='running'
        )
    except Exception as e:
        logger.exception(f'Error creating task: {e} STEP 0')

    current_task = service_tools.get_current_task(category_url)
    if not current_task:
        service_tools.task_error(category_url)
        logger.error(f'Error {category_url} STEP 1')
        return

    step_2 = parser.collect_product_list(current_task, category_url)
    if not step_2:
        service_tools.task_error(category_url)
        logger.error(f'Category {category_url} STEP 2')
        return

    step_3 = parser.processing_product_list(current_task)
    if not step_3:
        service_tools.task_error(category_url)
        logger.error(f'Category {category_url} STEP 3')
        return

    output_filename = parser.process_csv(current_task)
    if not output_filename:
        service_tools.task_error(category_url)
        logger.error(f'Category {category_url} STEP 4')
        return

    return output_filename
