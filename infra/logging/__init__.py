"""
infra.logging - Structured logging with structlog.

Re-exports from main.py for backward compatibility.
"""
from .main import init_logger, get_logger, log_file

__all__ = ["init_logger", "get_logger", "log_file"]
