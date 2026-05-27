"""
core.ports.logger - Logger port interface.

This port defines the logging interface that core/application/
processors use. The implementation is in infra.logging.

Hexagonal architecture:
    - core defines ports (interfaces)
    - infra implements ports
    - core never imports from infra or adapters
"""

from __future__ import annotations

from typing import Any, Protocol


class Logger(Protocol):
    """Logger interface for core/application processors."""

    def debug(self, msg: str, **kwargs: Any) -> None: ...
    def info(self, msg: str, **kwargs: Any) -> None: ...
    def warning(self, msg: str, **kwargs: Any) -> None: ...
    def error(self, msg: str, **kwargs: Any) -> None: ...
    def exception(self, msg: str, **kwargs: Any) -> None: ...
