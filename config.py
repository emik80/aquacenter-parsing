from dotenv import load_dotenv
from loguru import logger

from dataclasses import dataclass
from pathlib import Path

ROOT_DIR = Path(__file__)
DATA_DIR = 'data'
DATABASE = 'products.db'
LOG_DIR = 'logs'
MAIN_DOMAN = 'https://aquapolis.ua'
headers = {
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'
}


@dataclass
class BaseParserConfig:
    MAIN_DOMAIN: str
    HEADERS: dict
    DATA_DIR: Path
    DATABASE: Path


def load_config():
    # Logger Config
    logger.add(Path(ROOT_DIR.parent, LOG_DIR, 'info.log'),
               rotation='1 day',
               retention='14 days',
               level='INFO',
               enqueue=True)

    load_dotenv()

    config = BaseParserConfig(
        MAIN_DOMAIN=MAIN_DOMAN,
        HEADERS=headers,
        DATA_DIR=Path(ROOT_DIR.parent, DATA_DIR),
        DATABASE=Path(ROOT_DIR.parent, DATA_DIR, DATABASE),
        )

    logger.info('Configuration Loaded')
    return config


parser_config = load_config()
