"""Logging configuration for the Twitch bot."""
import logging
import logging.handlers
import os
from datetime import datetime

def setup_logging(log_level: str = "INFO") -> None:
    """Set up logging configuration with rotating file handler and console output.
    
    Args:
        log_level: The logging level to use (default: INFO)
    """
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Configure logging format
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Set up rotating file handler
    log_file = os.path.join(log_dir, f"twitch_bot_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(log_format)

    # Set up console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Set specific levels for some loggers
    logging.getLogger("twitchio").setLevel(logging.WARNING)
    logging.getLogger("websockets").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING) 