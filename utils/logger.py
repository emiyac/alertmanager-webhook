
import logging

from .config import settings

def get_logger() -> logging.Logger:
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(name)s %(threadName)s %(module)s.%(funcName)s - %(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger = logging.getLogger("root")
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    return logger


logger = get_logger()
