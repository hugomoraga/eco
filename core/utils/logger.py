"""
core.utils.logger - Logger utilities for core/application/ components.

This module provides logging utilities that core components use.
The actual implementation is in infra.logging, but this shim allows
core to use logging without direct dependency on infra.

Hexagonal architecture:
    - core/utils/ provides utilities used by core components
    - These utilities delegate to infra implementations
    - core never imports directly from infra

Usage:
    from core.utils.logger import get_logger

    log = get_logger(__name__)
    log.info("message", turn=1)

Note: init_logger() should be called once by the adapter layer
before creating the engine. Core components only use get_logger().
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.ports.logger import Logger


def get_logger(name: str) -> "Logger":
    """
    Get a logger instance for the given module name.

    This delegates to infra.logging.get_logger.
    The logging system must be initialized by the adapter layer
    before calling this function.
    """
    from infra.logging import get_logger as _get_logger
    return _get_logger(name)


def init_logger(run_dir: Path | None = None) -> None:
    """
    Initialize the logging system.

    Should be called once at application startup by the ADAPTER LAYER.
    NOT by core components.

    Args:
        run_dir: Directory for debug.log file (optional).
    """
    from infra.logging import init_logger as _init_logger
    _init_logger(run_dir)


def log_file() -> Path | None:
    """Return the current log file path, if initialized."""
    from infra.logging import log_file as _log_file
    return _log_file()
