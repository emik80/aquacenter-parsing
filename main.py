from config import parser_config, logger
import parser as parser


@logger.catch
def main():
    category_url = 'https://aquapolis.ua/ua/zakladnye-detali/zakladnye_material_filtr/nerzhavejuschaja-stal.html'
    category_data = parser.get_product_list(category_url)
    if not category_data:
        return
    else:
        print(category_data)


if __name__ == '__main__':
    main()
