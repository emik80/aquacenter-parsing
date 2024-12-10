import json
from datetime import datetime
from typing import Dict
from peewee import IntegrityError

from config import logger
from db import Product, Task
from .parser_tools import get_product_list, get_product_info
import service as service_tools


@service_tools.time_of_function
def collect_product_list(current_task: Task, url: str) -> Dict | None:
    logger.info(f'Parsing of category {url} starting...')

    category_data = get_product_list(url)
    if not category_data:
        logger.warning(f'{url} is probably incorrect...')
        return None

    items_qty = category_data.get('items_qty')
    source_category_name = category_data.get('cat_name')
    product_urls = category_data.get('product_urls')
    try:
        task = current_task
        task.source_category_name = source_category_name
        task.cat_qty = items_qty
        task.urls = json.dumps(product_urls)
        task.save()
    except Exception as e:
        logger.exception(f'Error updating task {url}: {e}')
        return None

    logger.success(f'Successfully collected product list for {url}')
    return category_data


@service_tools.time_of_function
def processing_product_list(current_task: Task) -> bool:
    product_urls = json.loads(current_task.urls)
    for url in product_urls:
        product_data = get_product_info(url=url)
        if product_data:
            for product in product_data:
                product_name = product.get('product_name')
                try:
                    Product.create(
                        product_url=product['product_url'],
                        product_name=product_name,
                        target_category=current_task.target_category,
                        product_code=product.get('product_code'),
                        price=product.get('product_price'),
                        stock=product.get('stock'),
                        description=product.get('description'),
                        specs_table=product.get('specs_table'),
                        images=product.get('images'),
                    )
                    logger.success(f'Product {product_name} created successfully')
                except IntegrityError as e:
                    logger.error(f"IntegrityError for product {product_name}: {e}")
                except Exception as e:
                    logger.exception(f'Error creating product in DB {product_name}: {e}')
    logger.success(f'Product list was processed successfully')
    return True


@service_tools.time_of_function
def process_csv(task):
    queryset = Product.select().where(
        (Product.target_category == task.target_category) &
        (Product.status == 'new')
    )

    if not queryset.exists():
        logger.warning(f'Queryset is empty: {queryset}')
        return None

    output_filename = service_tools.data_to_csv(queryset)
    if not output_filename:
        return None
    else:
        for product in queryset:
            product.status = 'exported'
            product.modified_at = datetime.now()
            product.save()
        return output_filename
