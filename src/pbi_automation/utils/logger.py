import logging
import structlog
from typing import Optional
from pathlib import Path


def setup_logging(verbose: bool = False, log_file: Optional[Path] = None):
    """Setup structured logging."""
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ]
    
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    level = logging.DEBUG if verbose else logging.INFO
    
    if log_file:
        logging.basicConfig(
            format="%(message)s",
            stream=open(log_file, 'w'),
            level=level
        )
    else:
        logging.basicConfig(
            format="%(message)s",
            level=level
        )


def log_info(message: str):
    """Log an info message."""
    logger = structlog.get_logger()
    logger.info(message)


def log_error(message: str):
    """Log an error message."""
    logger = structlog.get_logger()
    logger.error(message)


def log_warning(message: str):
    """Log a warning message."""
    logger = structlog.get_logger()
    logger.warning(message)


def log_success(message: str):
    """Log a success message."""
    logger = structlog.get_logger()
    logger.info(message) 