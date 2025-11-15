import logging

def get_logger(name: str) -> logging.Logger:
    """
    Provides a configured logger instance.
    Usage:
        logger = get_logger(__name__)
    """
    logger = logging.getLogger(name)

    # Configure only once
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s'
        )
        handler.setFormatter(formatter)

        logger.addHandler(handler)

    return logger
