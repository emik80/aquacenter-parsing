from config import logger
from parser import parser_core


@logger.catch
def main():
    category_url = input('Category URL: ')
    target_category = input('Target category: ')

    output_filename = parser_core(category_url=category_url,
                                  target_category=target_category)
    print(f'Output filename: {output_filename}')


if __name__ == '__main__':
    main()
