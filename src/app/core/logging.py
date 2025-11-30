"""Structured logging configuration using loguru."""

import sys
from pathlib import Path

from loguru import logger

from app.config import settings


def setup_logging():
    """Configure structured logging with loguru."""
    # Remove default handler
    logger.remove()

    # Console handler with appropriate format based on environment
    if settings.debug:
        # Development: Human-readable format
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
        logger.add(
            sys.stdout,
            format=log_format,
            level="DEBUG",
            colorize=True,
        )
    else:
        # Production: JSON format for log aggregation
        logger.add(
            sys.stdout,
            format="{message}",
            level="INFO",
            serialize=True,  # Output as JSON
        )

    # File handler for all logs (optional, useful for debugging)
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Rotating file handler
    logger.add(
        logs_dir / "loops-api.log",
        rotation="100 MB",
        retention="30 days",
        compression="zip",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
    )

    # Error-only file handler
    logger.add(
        logs_dir / "errors.log",
        rotation="50 MB",
        retention="60 days",
        compression="zip",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
    )

    logger.info("Logging configured", debug=settings.debug, app_name=settings.app_name)


# Export logger for use in other modules
__all__ = ["logger", "setup_logging"]
