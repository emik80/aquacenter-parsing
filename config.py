import os

from dotenv import load_dotenv
from loguru import logger

from dataclasses import dataclass
from pathlib import Path


headers = {
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'
}

ROOT_DIR = Path(__file__)
DATA_DIR = 'data'
DATABASE = 'products.db'
LOG_DIR = 'logs'
PRODUCTION = os.getenv("PRODUCTION", "FALSE").upper() == "TRUE"


@dataclass
class BaseParserConfig:
    MAIN_DOMAIN: str
    DEFAULT_IMG: str
    HEADERS: dict
    DATA_DIR: Path
    DATABASE: Path
    BOT_TOKEN: str
    SUPERADMIN: str
    ADMINS: list
    REDIS_HOST: str


def load_config():
    # Logger Config
    logger.add(Path(ROOT_DIR.parent, LOG_DIR, 'info.log'),
               rotation='1 day',
               retention='14 days',
               level='INFO',
               enqueue=True)

    load_dotenv()

    config = BaseParserConfig(
        MAIN_DOMAIN=os.getenv('MAIN_DOMAIN'),
        DEFAULT_IMG=os.getenv('DEFAULT_IMG'),
        HEADERS=headers,
        DATA_DIR=Path(ROOT_DIR.parent, DATA_DIR),
        DATABASE=Path(ROOT_DIR.parent, DATA_DIR, DATABASE),
        BOT_TOKEN=os.getenv('BOT_TOKEN'),
        SUPERADMIN=os.getenv('SUPERADMIN'),
        ADMINS=os.getenv('ADMINS').split(','),
        REDIS_HOST=os.getenv("PROD_REDIS_HOST") if PRODUCTION else os.getenv("REDIS_HOST"),
        )

    logger.info('Configuration Loaded')
    return config


parser_config = load_config()
