from config import logger
from typing import Dict, List

import service as service_tools


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
        'items_qty': items_qty,
        'cat_name': cat_name
    }

    return category_data


def _get_pagination(category_url: str) -> Dict | None:
    soup = service_tools.soup_maker(url=category_url)
    cat_name = soup.find('div', class_='page-title-wrapper').get_text()
    if not soup:
        return None

    try:
        items_qty = soup.find_all('span', class_='toolbar-number')[-1].text
    except Exception as ex:
        logger.exception(f'{category_url} - items_qty: {ex}')
        return None

    pages = [category_url, ]
    pages_qty = int(items_qty) // 30 + 1
    if pages_qty > 1:
        for i in range(2, pages_qty + 1):
            pages.append(f'{category_url}?p={i}')
    res = {
        'cat_name': cat_name,
        'pages': pages,
        'items_qty': int(items_qty)
    }
    return res


def get_product_info(url: str) -> Dict | None:
    soup = service_tools.soup_maker(url)
    if not soup:
        return None

    product_data = {}

    try:
        product_data['product_name'] = soup.find('h1').text.strip()
        product_data['product_code'] = (soup.find('div', class_='product attribute sku').
                                        find_next('div', class_='value').text.strip())
        product_data['price'] = (soup.find('div', class_='product-info-price').
                                 find('span', attrs={"data-price-amount": True}).
                                 get('data-price-amount'))

        stock_unavailable = soup.find('div', class_='stock unavailable')
        if stock_unavailable and stock_unavailable.text.strip() == 'Немає у наявності':
            product_data['stock'] = 0
        else:
            product_data['stock'] = 1

        short_description = soup.find('div', class_='product attribute overview').text.strip()
        product_data['description'] = short_description

        specs_raw = soup.find('caption', class_='table-caption').find_next('tbody')
        specs_clean = service_tools.parse_table_data(specs_html=specs_raw)
        specs_table = service_tools.dict_to_html_table(data_dict=specs_clean)
        product_data['specs_table'] = specs_table

        img_block = soup.find('div', class_='MagicToolboxSelectorsContainer').find_all('a')
        product_data['images'] = '|'.join([i.get('href') for i in img_block])

    except Exception as ex:
        logger.exception(f'{url} - {ex}')

    return product_data
