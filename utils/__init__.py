from .config import settings, LOGGING_CONFIG
from .salt import get_sign
from .schema import AlertManagerModel
from .logger import logger

for key, value in vars(settings).items():
    logger.info(f"{key}: {value}")