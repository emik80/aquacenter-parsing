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
    output_filename, current_task = parser.run_parsing()
    if current_task:
        task_warning(current_task)

    print(f'Output filename: {output_filename}')


if __name__ == '__main__':
    main()
