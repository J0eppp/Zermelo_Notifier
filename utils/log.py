import logging
import os

from datetime import datetime

logger = None


def setup():
    log_path = os.environ["LOG_PATH"]
    logger = logging.getLogger("bot")
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(
        filename=log_path, encoding="utf-8", mode="a")
    handler.setFormatter(logging.Formatter(
        '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s'))
    logger.addHandler(handler)
    # logging.basicConfig(filename=log_path, level=logging.DEBUG)


def debug(msg: str):
    logger.debug(msg)


def info(msg: str):
    logger.info(msg)


def warning(msg: str):
    logger.warning(msg)


def error(msg: str):
    logger.error(msg)
