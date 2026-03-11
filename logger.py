import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log"), 
        logging.StreamHandler(),         
    ],
)

_logger = logging.getLogger(__name__)


def log_message(message: str, level: str = "info") -> None:
    """Log a message at the given level: info / warning / error"""
    if level == "info":
        _logger.info(message)
    elif level == "warning":
        _logger.warning(message)
    elif level == "error":
        _logger.error(message)
