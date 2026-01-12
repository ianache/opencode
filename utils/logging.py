"""
Logging utilities for GraphRAG application.

Provides centralized logging setup and configuration using loguru.
"""

import sys
from pathlib import Path
from typing import Optional

from loguru import logger

from config.settings import get_settings


def setup_logger(name: str, log_file: Optional[Path] = None) -> None:
    """Set up and configure logger using loguru."""

    settings = get_settings()

    # Remove default handler
    logger.remove()

    # Configure console handler
    logger.add(
        sys.stdout,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
        level=settings.log_level.upper(),
        colorize=True,
    )

    # Add file handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
            level=settings.log_level.upper(),
            rotation="10 MB",
            retention="7 days",
            compression="zip",
        )


def get_logger(name: str):
    """Get a logger instance."""
    # Loguru uses a shared logger, so we just bind the name
    return logger.bind(name=name)
