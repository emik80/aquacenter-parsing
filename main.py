from datetime import datetime

from config import parser_config, logger
import parser as parser
import service as service_tools
from db import Task


@logger.catch
def main():
    # category_url = input('Category URL: ')
    # target_category = input('Target category: ')

    category_url = 'https://aquapolis.ua/ua/zakladnye-detali/zakladnye_material_filtr/nerzhavejuschaja-stal.html'
    target_category = 'Нержавійка'

    logger.info(f'START: Parsing of category {category_url} into {target_category}')
    Task.create(
        source_url=category_url,
        target_category=target_category,
        start=datetime.now(),
        status='running'
    )

    current_task = service_tools.get_current_task(category_url)
    if not current_task:
        service_tools.task_error(category_url)
        logger.error(f'Error {category_url} STEP 0')
        return

    step_1 = parser.collect_product_list(current_task, category_url)
    if not step_1:
        service_tools.task_error(category_url)
        logger.error(f'Category {category_url} STEP 1')
        return

    step_2 = parser.processing_product_list(current_task)
    if not step_2:
        service_tools.task_error(category_url)
        logger.error(f'Category {category_url} STEP 2')
        return

    output_filename = parser.process_csv(current_task)
    if not output_filename:
        service_tools.task_error(category_url)
        logger.error(f'Category {category_url} STEP 3')
        return
    print(output_filename)


if __name__ == '__main__':
    main()
