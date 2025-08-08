import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_FORMAT = '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
LOG_DIR = Path('logs')
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / 'novaloom.log'

_initialized = False

def init_logging(level: int = logging.INFO) -> None:
    global _initialized
    if _initialized:
        return
    logger = logging.getLogger()
    logger.setLevel(level)

    # Remove default handlers if any
    for h in list(logger.handlers):
        logger.removeHandler(h)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    _initialized = True


def get_logger(name: str) -> logging.Logger:
    init_logging()
    return logging.getLogger(name)
