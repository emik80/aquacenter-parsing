import math
import re

from typing import Dict, List

import service as service_tools
from config import logger, parser_config


def get_product_list(category_url: str) -> Dict | None:
    res = _get_pagination(category_url)
    if not res:
        return None
    else:
        cat_name = res.get('cat_name')
        pages = res.get('pages')
        items_qty = res.get('items_qty')

    product_urls = []
    for page in pages:
        logger.info(f'Processing page {page}')
        soup = service_tools.soup_maker(url=page)
        if not soup:
            logger.error(f'No soup found {page}')
            continue
        else:
            try:
                urls = soup.find_all('a', class_='product-item-link')
                if urls:
                    product_urls.extend(_.get('href') for _ in urls)
            except Exception as e:
                logger.exception(f'Exception while processing page {page}')

    category_data = {
        'product_urls': product_urls,
        'cat_name': cat_name,
        'items_qty': items_qty
    }
    return category_data


def _get_pagination(category_url: str) -> Dict | None:
    soup = service_tools.soup_maker(url=category_url)
    cat_name = soup.find('div', class_='page-title-wrapper').get_text()
    if not soup:
        return None

    pages = [category_url, ]

    try:
        is_pagination = soup.find(class_="pages")
        if is_pagination:
            items_qty = soup.find_all('span', class_='toolbar-number')[-1].text
            if items_qty and int(items_qty) > 30:
                pages_qty = int(items_qty) // 30 + 1
                for i in range(2, pages_qty + 1):
                    pages.append(f'{category_url}?p={i}')
        else:
            script_tag = soup.find('p', class_='toolbar-amount').find('script').string
            item_count_match = re.search(r'let\s+itemCount\s*=\s*(\d+);', script_tag)
            items_qty = int(item_count_match.group(1))
    except Exception as ex:
        logger.exception(f'{category_url} - items_qty: {ex}')
        items_qty = None

    res = {
        'cat_name': cat_name,
        'pages': pages,
        'items_qty': items_qty
    }
    return res


def get_product_info(url: str) -> List[Dict] | None:
    soup = service_tools.soup_maker(url)
    if not soup:
        return None

    res = []
    try:
        variants_table = soup.find(id='super-product-table')

        if variants_table:
            variants = variants_table.find_next('tbody').find_all('tr')
            for variant in variants:
                product_name = variant.find(class_='product-item-name').text.strip()
                product_code = variant.find(class_='product-item-code').text.replace('Код:', '').strip()
                product_price = (variant.find('div', class_='price-box price-final_price').
                                 find_next('span', attrs={"data-price-amount": True}).
                                 get('data-price-amount'))
                in_stock = variant.find(class_='col qty').get_text().strip()
                stock = 'outofstock' if in_stock == 'Немає у наявності' else 'instock'
                product_attrs = {
                    'product_name': product_name,
                    'product_code': product_code,
                    'product_price': math.ceil(float(product_price)),
                    'stock': stock,
                }
                res.append(product_attrs)

        else:
            product_name = soup.find('h1').text.strip()
            product_code = (soup.find('div', class_='product attribute sku').
                            find_next('div', class_='value').text.strip())
            product_price_box = (soup.find('div', class_='product-info-price').
                                find('span', attrs={"data-price-amount": True}))
            if product_price_box:
                product_price = product_price_box.get('data-price-amount')
            else:
                product_price = 0

            stock_preorder = soup.find('div', class_='stock preorder')
            stock_unavailable = soup.find('div', class_='stock unavailable')
            stock = 'outofstock' if stock_unavailable or stock_preorder or product_price == 0\
                else 'instock'
            product_attrs = {
                'product_name': product_name,
                'product_code': product_code,
                'product_price': math.ceil(float(product_price)),
                'stock': stock,
            }
            res.append(product_attrs)

        short_description = (soup.find('div', class_='product attribute overview')
                             .find_next('div', class_='value'))
        specs_raw = (soup.find('div', class_='additional-attributes-wrapper table-wrapper')
                     .find_next('tbody'))
        specs_clean = service_tools.parse_table_data(specs_html=specs_raw)
        specs_table = service_tools.dict_to_html_table(data_dict=specs_clean)
        default_img = soup.find('div', class_='MagicToolboxContainer placeholder')
        if default_img:
            images = parser_config.DEFAULT_IMG
        else:
            img_block = soup.find('div', class_='MagicToolboxSelectorsContainer').find_all('a')
            images = '|'.join([i.get('href') for i in img_block if i.get('href') != '#'])

        for product in res:
            product['product_url'] = url
            product['description'] = short_description
            product['specs_table'] = specs_table
            product['images'] = images

    except Exception as ex:
        logger.exception(f'{url} - {ex}')

    return res
