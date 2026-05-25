"""
ECO Debug Logging — structured log to run_dir/debug.log
"""

from __future__ import annotations

import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_core.domain.entities import World


# ANSI escape code stripper
_ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*m')


def strip_ansi(text: str) -> str:
    return _ANSI_ESCAPE.sub('', text)


class DebugLog:
    """
    Singleton debug logger for ECO.
    Logs to run_dir/debug.log with timestamps + levels.
    Console shows INFO+, file shows DEBUG.
    """
    _instance: "DebugLog | None" = None

    def __init__(self, run_dir: Path):
        self.run_dir = run_dir
        self.log_file = run_dir / "debug.log"
        self._logger: logging.Logger | None = None
        self._setup()

    def _setup(self) -> None:
        self._logger = logging.getLogger("eco")
        self._logger.setLevel(logging.DEBUG)
        self._logger.handlers.clear()

        # File handler — DEBUG level (all messages)
        fh = logging.FileHandler(self.log_file, mode='w')
        fh.setLevel(logging.DEBUG)
        file_fmt = logging.Formatter(
            "%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        fh.setFormatter(file_fmt)

        # Console handler — INFO level only
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        console_fmt = logging.Formatter(
            "%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S"
        )
        ch.setFormatter(console_fmt)

        self._logger.addHandler(fh)
        self._logger.addHandler(ch)

    def _log(self, level: int, msg: str) -> None:
        if self._logger:
            # Strip ANSI from message before writing to file
            clean = strip_ansi(msg)
            self._logger.log(level, clean)

    def debug(self, msg: str) -> None:
        self._log(logging.DEBUG, msg)

    def info(self, msg: str) -> None:
        self._log(logging.INFO, msg)

    def warn(self, msg: str) -> None:
        self._log(logging.WARNING, msg)

    def error(self, msg: str, exc: BaseException | None = None) -> None:
        if exc:
            self._log(logging.ERROR, f"{msg}: {exc}")
            if self._logger:
                self._logger.exception(exc)
        else:
            self._log(logging.ERROR, msg)

    # ─── Convenience helpers ────────────────────────────────────────────────

    def turn_start(self, turn: int, world: "World") -> None:
        p = world.pressure
        l = world.legitimacy
        r = world.resources_global
        self.info(f"Turn {turn} started — pressure={p:.1f} legitimacy={l:.1f} resources={r:.1f}")

    def turn_end(self, turn: int, action: str | None) -> None:
        self.info(f"Turn {turn} ended — action={action}")

    def input_mode(self, mode: str, input_class: str) -> None:
        self.info(f"Input source: mode={mode} class={input_class}")

    def menu_interactive(self, interactive: bool, reason: str) -> None:
        self.debug(f"InteractiveMenu._is_interactive() → {interactive} ({reason})")

    def menu_raw_enable(self, fd: int) -> None:
        self.debug(f"InteractiveMenu: raw mode enabled (fd={fd})")

    def menu_raw_restore(self) -> None:
        self.debug("InteractiveMenu: terminal restored")

    def key_captured(self, key_desc: str, raw: str) -> None:
        self.debug(f"Key captured: {key_desc} (raw={repr(raw)})")

    def menu_selection(self, action: str, index: int) -> None:
        self.info(f"Menu: selected action={action} (index={index})")

    def menu_autoplay_trigger(self, reason: str) -> None:
        self.info(f"Menu: autoplay triggered ({reason})")

    def fallback_to_text(self, reason: str) -> None:
        self.warn(f"Input fallback: interactive → text ({reason})")

    def fallback_to_autoplay(self, reason: str) -> None:
        self.warn(f"Input fallback: text → autoplay ({reason})")

    # ─── Singleton ─────────────────────────────────────────────────────────

    @classmethod
    def init(cls, run_dir: Path) -> "DebugLog":
        cls._instance = cls(run_dir)
        return cls._instance

    @classmethod
    def get(cls) -> "DebugLog | None":
        return cls._instance


def dbg() -> DebugLog | None:
    return DebugLog.get()