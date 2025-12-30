#!/usr/bin/env python3
"""
Affidavit Writing Assistant - Main Entry Point

Simple, single-file entry point for the application.

Usage:
    python main.py
"""
import sys
import logging
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.logging_config import setup_logging
from gui.app import AffidavitApp


def main():
    """Main entry point."""
    # Setup logging
    log_file = setup_logging()

    logger = logging.getLogger(__name__)
    logger.info("Starting Affidavit Writing Assistant")

    try:
        # Create and run GUI
        app = AffidavitApp()
        app.run()

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)

    except Exception as e:
        logger.critical("Fatal error", exc_info=True)
        print(f"\nFatal error: {str(e)}")
        print(f"Check log file for details: {log_file}")
        sys.exit(1)

    logger.info("Application shutdown")


if __name__ == "__main__":
    main()
