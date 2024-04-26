from .config import LOGGING_CONFIG, settings
from .logger import logger
from .salt import get_sign
from .schema import AlertManagerModel

__all__ = ["LOGGING_CONFIG", "settings", "logger", "get_sign", "AlertManagerModel"]

for key, value in vars(settings).items():
    logger.info(f"{key}: {value}")
