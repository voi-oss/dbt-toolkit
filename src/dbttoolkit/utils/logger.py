import logging
import sys

LOG_FORMAT = (
    "%(asctime)s - %(name)s - %(threadName)s - %(levelname)s — %(filename)s:%(funcName)s:%(lineno)d - %(message)s"
)


def init_logger(level=logging.INFO):
    logger = get_logger()
    logger.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(handler)

    return logger


def get_logger():
    return logging.getLogger("dbt-toolkit")
