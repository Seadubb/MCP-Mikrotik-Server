"""Structured logging configuration for MikroTik MCP Server."""

import logging
import sys
from typing import Optional
from pathlib import Path


class StderrHandler(logging.Handler):
    """Custom handler that writes to stderr with flush."""

    def emit(self, record):
        """Emit a record to stderr."""
        try:
            msg = self.format(record)
            print(msg, file=sys.stderr, flush=True)
        except Exception:
            self.handleError(record)


def setup_logger(
    name: str = "mikrotik_mcp",
    level: str = "INFO",
    log_file: Optional[Path] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Set up structured logger for the MikroTik MCP server.

    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        format_string: Optional custom format string

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Default format with timestamp, level, module, and message
    if format_string is None:
        format_string = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"

    formatter = logging.Formatter(
        format_string,
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Always add stderr handler (for MCP protocol compatibility)
    stderr_handler = StderrHandler()
    stderr_handler.setFormatter(formatter)
    logger.addHandler(stderr_handler)

    # Optionally add file handler
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def get_logger(name: str = "mikrotik_mcp") -> logging.Logger:
    """
    Get or create logger instance.

    Args:
        name: Logger name (defaults to main logger)

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)

    # If logger has no handlers, set it up with defaults
    if not logger.handlers:
        setup_logger(name)

    return logger


# Create default logger instance
default_logger = setup_logger()
