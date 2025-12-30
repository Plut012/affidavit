"""
Logging configuration for affidavit assistant.
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from config import settings


def setup_logging():
    """
    Configure logging for the application.

    Sets up both file and console logging.
    """
    # Create logs directory if it doesn't exist
    settings.LOGS_DIR.mkdir(exist_ok=True)

    # Generate log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = settings.LOGS_DIR / f"affidavit_{timestamp}.log"

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))

    # Clear any existing handlers
    root_logger.handlers.clear()

    # File handler - detailed logging
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(settings.LOG_FORMAT)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # Console handler - less verbose
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # Log startup
    logging.info("="*60)
    logging.info("Affidavit Writing Assistant Started")
    logging.info(f"Log file: {log_file}")
    logging.info("="*60)

    return log_file
