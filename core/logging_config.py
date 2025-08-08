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

    # Suppress extremely noisy Matplotlib font manager DEBUG logs while still allowing warnings/errors.
    # These messages (findfont scoring for every font file) add little diagnostic value for this app
    # and can flood the log when debug mode is enabled.
    try:
        fm_logger = logging.getLogger("matplotlib.font_manager")
        # Only raise its level if it would otherwise inherit DEBUG from root.
        if fm_logger.level == logging.NOTSET or fm_logger.level < logging.WARNING:
            fm_logger.setLevel(logging.WARNING)  # Show warnings and above, hide debug/info
    except Exception:
        pass

    _initialized = True


def get_logger(name: str) -> logging.Logger:
    init_logging()
    return logging.getLogger(name)
