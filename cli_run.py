from config import logger
from parser import ParserCore
from db import task_warning, initialize_database, db


@logger.catch
def main():
    initialize_database(db)
    category_url = input('Category URL: ')
    target_category = input('Target category: ')

    parser = ParserCore(category_url=category_url,
                        target_category=target_category)
    result = parser.run_parsing()
    if result is None:
        logger.error('Parsing failed or returned no data.')
    else:
        output_filename, current_task = result[0], result[1]
        if current_task and current_task.status == 'running':
            task_warning(current_task)
        print(f'Output filename: {output_filename}')


if __name__ == '__main__':
    main()
