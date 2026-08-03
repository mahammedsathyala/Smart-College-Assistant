"""
Smart College Assistant — Logger Utility
Configures application, error, AI, and audit loggers.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from colorlog import ColoredFormatter

from config.settings import ActiveConfig


def _make_file_handler(path: str, level: int = logging.DEBUG) -> logging.FileHandler:
    """Create a rotating file handler."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    handler = logging.handlers.RotatingFileHandler(
        path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    handler.setLevel(level)
    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(fmt)
    return handler


def _make_console_handler() -> logging.StreamHandler:
    """Create a colored console handler."""
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    fmt = ColoredFormatter(
        "%(log_color)s%(asctime)s%(reset)s | %(log_color)s%(levelname)-8s%(reset)s"
        " | %(cyan)s%(name)s%(reset)s | %(message)s",
        datefmt="%H:%M:%S",
        log_colors={
            "DEBUG": "blue",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )
    handler.setFormatter(fmt)
    return handler


def setup_logger(name: str, log_file: str | None = None) -> logging.Logger:
    """
    Create and return a named logger.

    Args:
        name: Logger name (typically __name__).
        log_file: Optional specific log file path.

    Returns:
        Configured Logger instance.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # Already configured

    level = getattr(logging, ActiveConfig.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(level)

    # Console handler
    logger.addHandler(_make_console_handler())

    # File handler — default app.log
    target = log_file or ActiveConfig.LOG_FILE
    logger.addHandler(_make_file_handler(target))

    # Error file handler
    logger.addHandler(
        _make_file_handler(ActiveConfig.ERROR_LOG_FILE, logging.ERROR)
    )

    logger.propagate = False
    return logger


def get_ai_logger() -> logging.Logger:
    """Return dedicated AI/LLM logger."""
    return setup_logger("ai", ActiveConfig.AI_LOG_FILE)


def get_audit_logger() -> logging.Logger:
    """Return dedicated audit trail logger."""
    return setup_logger("audit", ActiveConfig.AUDIT_LOG_FILE)


# ── Module-level default logger ──────────────────────────────
logger = setup_logger("smart_college")
