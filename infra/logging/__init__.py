"""
infra.logging - Structured logging with structlog.

Logs go to stderr (observability lane).
stdout is reserved for JSON protocol messages.

Usage:
    from infra.logging import init_logger, get_logger

    init_logger(run_dir)
    log = get_logger(__name__)
    log.info("message", key=value)
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


def init_logger(run_dir: Path | None = None) -> None:
    """
    Initialize structlog with output to stderr and optional debug.log file.

    Args:
        run_dir: Directory for debug.log file (optional).
    """
    global _log_file_path

    structlog.reset_defaults()

    console_renderer = structlog.dev.ConsoleRenderer()

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="%H:%M:%S.%f", utc=False),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
        structlog.processors.format_exc_info,
    ]

    def console_only_renderer(logger, method_name, event_dict):
        """Render to console only (stderr)."""
        return console_renderer(logger, method_name, event_dict)

    def file_renderer(logger, method_name, event_dict):
        """Render to file."""
        return console_renderer(logger, method_name, event_dict)

    level = getattr(structlog.stdlib.logging, _log_level, structlog.stdlib.logging.DEBUG)

    if run_dir:
        _log_file_path = run_dir / "debug.log"
        file_logger = structlog.PrintLoggerFactory(file=open(_log_file_path, "a", encoding="utf-8"))
        structlog.configure(
            processors=processors + [file_renderer],
            wrapper_class=structlog.make_filtering_bound_logger(level),
            context_class=dict,
            logger_factory=file_logger,
            cache_logger_on_first_use=False,
        )
    else:
        _log_file_path = None
        structlog.configure(
            processors=processors + [console_only_renderer],
            wrapper_class=structlog.make_filtering_bound_logger(level),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
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
