from datetime import datetime
from pathlib import Path
from random import randint
from time import time
from typing import Optional, Dict
import csv

import requests
from bs4 import BeautifulSoup

from config import parser_config, logger


def time_of_function(function):
    def wrapped(*args):
        start_time = time()
        res = function(*args)
        logger.info(f'Task completed in {round(time() - start_time, 2)} seconds')
        return res
    return wrapped


def soup_maker(url: str) -> Optional[BeautifulSoup]:
    try:
        response = requests.get(url=url, headers=parser_config.HEADERS)
        if response.status_code == 200:
            src = response.text
            soup = BeautifulSoup(src, 'lxml')
            return soup
        else:
            logger.error(f"An error occurred while accessing the page. Status code: {response.status_code}")
            return None
    except Exception as ex:
        logger.error(f'Error {ex}')
        return None


def parse_table_data(specs_html) -> Dict:
    result = {}

    for row in specs_html.find_all('tr'):
        header = row.find('th')
        cell = row.find('td')

        if header and "Завантажте додаткові матеріали" in header.get_text(strip=True):
            continue

        if header and cell:
            key = header.get_text(strip=True)
            value = cell.get_text(strip=True)
            if cell.find('ul'):
                value = [li.get_text(strip=True) for li in cell.find_all('li')]

            result[key] = value

    return result


def dict_to_html_table(data_dict: Dict) -> str:
    html = ['<table>']
    for key, value in data_dict.items():
        html.append('<tr>')
        html.append(f'<td>{key}</td>')
        if isinstance(value, list):
            list_items = ''.join([f'<li>{item}</li>' for item in value])
            html.append(f'<td><ul>{list_items}</ul></td>')
        else:
            html.append(f'<td>{value}</td>')

        html.append('</tr>')
    html.append('</table>')
    return ''.join(html)


def data_to_csv(queryset) -> Path | None:
    file_name = f'products_{datetime.now().strftime('%Y%m%d')}_{randint(1, 10000000)}.csv'
    output_filename = Path(parser_config.DATA_DIR, file_name)

    headers = [
        'product_name',
        'product_url',
        'target_category',
        'product_code',
        'price',
        'stock',
        'description',
        'specs_table',
        'images',
    ]
    try:
        with open(output_filename, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(headers)
            for product in queryset:
                row = [
                    product.product_name,
                    product.product_url,
                    product.target_category,
                    product.product_code,
                    product.price,
                    product.stock,
                    product.description,
                    product.specs_table,
                    product.images,
                ]
                csv_writer.writerow(row)
            logger.success(f'CSV file saved at {output_filename}')
            return output_filename

    except Exception as ex:
        logger.exception(f'Error generating csv {ex}')
        return None
