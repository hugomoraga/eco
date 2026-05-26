"""
game_core.utils.logger - Structured logging with structlog.

Usage:
    from game_core.utils.logger import get_logger

    log = get_logger(__name__)
    log.info("message", key=value)

Configuration:
    ECO_LOG_LEVEL=DEBUG|INFO|WARNING|ERROR (default: DEBUG)
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    pass


_log_level: str = os.getenv("ECO_LOG_LEVEL", "DEBUG").upper()
_log_file_path: Path | None = None


def init_logger(run_dir: Path) -> None:
    """
    Initialize structlog with output to stderr and debug.log file.

    Args:
        run_dir: Directory for debug.log file.
    """
    global _log_file_path
    _log_file_path = run_dir / "debug.log"

    structlog.reset_defaults()

    # Create stdlib logger for file output
    file_logger = logging.getLogger("eco_file")
    file_logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(_log_file_path, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(message)s"))
    file_logger.addHandler(file_handler)
    file_logger.propagate = False

    # Console renderer (stderr)
    console_renderer = structlog.dev.ConsoleRenderer()

    # Processor chain
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="%H:%M:%S.%f", utc=False),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
        structlog.processors.format_exc_info,
    ]

    def dual_renderer(logger, method_name, event_dict):
        """Render to both file (JSON) and console."""
        # Write JSON to file
        json_renderer = structlog.processors.JSONRenderer()
        file_msg = json_renderer(logger, method_name, event_dict)
        file_logger.info(file_msg)

        # Write to console
        console_msg = console_renderer(logger, method_name, event_dict)
        return console_msg

    level = getattr(structlog.stdlib.logging, _log_level, structlog.stdlib.logging.DEBUG)

    structlog.configure(
        processors=processors + [dual_renderer],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a structlog bound logger for the given module name.

    Usage:
        log = get_logger(__name__)
        log.info("hello", turn=1)
    """
    return structlog.get_logger(name)


def log_file() -> Path | None:
    """Return the current log file path, if initialized."""
    return _log_file_path
