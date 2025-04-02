import os
import sys
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path

from summit_seo.web.api.core.config import settings


def setup_logging():
    """
    Set up logging configuration for the application.
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Determine log file path from settings or use default
    log_file_path = os.getenv("LOG_FILE_PATH", "logs/summit-seo.log")
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO if settings.environment == "production" else logging.DEBUG)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatters
    verbose_formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    simple_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Configure console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(simple_formatter)
    console_handler.setLevel(logging.INFO if settings.environment == "production" else logging.DEBUG)
    root_logger.addHandler(console_handler)
    
    # Configure file handler
    # Use RotatingFileHandler or TimedRotatingFileHandler based on settings
    if os.getenv("LOG_ROTATION", "size") == "daily":
        file_handler = TimedRotatingFileHandler(
            filename=log_file_path,
            when="midnight",
            interval=1,
            backupCount=30
        )
    else:
        file_handler = RotatingFileHandler(
            filename=log_file_path,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5
        )
    
    file_handler.setFormatter(verbose_formatter)
    file_handler.setLevel(logging.INFO if settings.environment == "production" else logging.DEBUG)
    root_logger.addHandler(file_handler)
    
    # Disable overly verbose loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
    logging.getLogger("aiohttp.client").setLevel(logging.WARNING)
    
    # Adjust log levels based on environment
    if settings.environment == "production":
        logging.getLogger("uvicorn").setLevel(logging.WARNING)
    
    # Create a named logger for the application
    logger = logging.getLogger("summit_seo")
    logger.info(f"Logging setup complete. Environment: {settings.environment}, Level: {logging.getLevelName(root_logger.level)}")
    
    return logger 