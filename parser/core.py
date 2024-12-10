from urllib.parse import urlparse

from aiogram.types import Message

from config import logger, parser_config
import parser as parser
from db import operations as db_operations


class ParserCore:
    def __init__(self, category_url: str, target_category: str):
        self.category_url = category_url
        self.target_category = target_category

    def _check_url(self, url: str) -> bool:
        logger.info(f'Checking URL: {self.category_url}')
        parsed_domain = urlparse(url).netloc
        if parsed_domain == str(parser_config.MAIN_DOMAIN):
            return True
        else:
            logger.warning(f'URL does not match {parser_config.MAIN_DOMAIN}')
            return False

    def run_parsing(self):
        logger.info(f'START: Parsing of category {self.category_url} into {self.target_category}')

        is_valid = self._check_url(self.category_url)
        if not is_valid:
            logger.error(f'Error incorrect URL - {self.category_url}')
            return None

        db_operations.create_task(category_url=self.category_url,
                                  target_category=self.target_category)

        current_task = db_operations.get_current_task(self.category_url)
        if not current_task:
            db_operations.task_error(current_task)
            logger.error(f'Error {self.category_url} STEP 1')
            return None

        step_2 = parser.collect_product_list(current_task, self.category_url)
        if not step_2:
            db_operations.task_error(current_task)
            logger.error(f'Category {self.category_url} STEP 2')
            return None

        step_3 = parser.processing_product_list(current_task)
        if not step_3:
            db_operations.task_error(current_task)
            logger.error(f'Category {self.category_url} STEP 3')
            return None

        output_filename = parser.process_csv(current_task)
        if not output_filename:
            db_operations.task_error(current_task)
            logger.error(f'Category {self.category_url} STEP 4')
            return None

        db_operations.task_finish(current_task)
        return output_filename, current_task


class ParserCoreTG(ParserCore):
    def __init__(self, category_url: str, target_category: str, user_message: Message):
        super().__init__(category_url, target_category)
        self.user_message = user_message

    async def run_parsing(self):
        logger.info(f'START: Parsing of category {self.category_url} into {self.target_category}')

        await self.user_message.edit_text("📌 Етап 1: Перевірка url...")
        is_valid = self._check_url(self.category_url)
        if not is_valid:
            logger.error(f'Error incorrect URL - {self.category_url}')
            await self.user_message.edit_text("❌ Некоректний URL")
            return None

        db_operations.create_task(category_url=self.category_url,
                                  target_category=self.target_category)

        await self.user_message.edit_text("📌 Етап 2: Створення задачі...")
        current_task = db_operations.get_current_task(self.category_url)
        if not current_task:
            db_operations.task_error(current_task)
            await self.user_message.edit_text("❌ Помилка створення задачі")
            return None

        await self.user_message.edit_text("📌 Етап 3: Збирання списка продуктів...")
        step_2 = parser.collect_product_list(current_task, self.category_url)
        if not step_2:
            db_operations.task_error(current_task)
            logger.error(f'Category {self.category_url} STEP 2')
            await self.user_message.edit_text("❌ Збирання списка продуктів завершилося з помилкою")
            return None

        await self.user_message.edit_text("📌 Етап 4: Обробка списка продуктів...")
        step_3 = parser.processing_product_list(current_task)
        if not step_3:
            db_operations.task_error(current_task)
            logger.error(f'Category {self.category_url} STEP 3')
            await self.user_message.edit_text("❌ Обробка списка продуктів завершилося з помилкою")
            return None

        await self.user_message.edit_text("📌 Етап 5: Генерація CSV файла...")
        output_filename = parser.process_csv(current_task)
        if not output_filename:
            db_operations.task_error(current_task)
            logger.error(f'Category {self.category_url} STEP 4')
            await self.user_message.edit_text("❌ Генерація файла завершилась з помилкою")
            return None

        db_operations.task_finish(current_task)
        await self.user_message.edit_text("✅ Парсинг завершено успішно!")
        return output_filename, current_task
