import logging
from app.config import Config


def setup_logging():
    root = logging.getLogger()

    handler = logging.StreamHandler()

    formatter = logging.Formatter(Config.LOG_FORMAT)

    handler.setFormatter(formatter)

    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(Config.LOG_LEVEL)