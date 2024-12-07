from typing import Optional, Tuple, Dict

import requests
from bs4 import BeautifulSoup
import csv

from config import parser_config, logger


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
    return '\n'.join(html)


def data_to_csv():
    pass
