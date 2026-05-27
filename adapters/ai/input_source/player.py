"""
PlayerInputSource — human player input with timeout.

Uses queue internally for TUI integration.
Falls back to Selector for console mode.
"""

from __future__ import annotations

import queue
import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.domain import World

from adapters.ai.input_source.base import InputSource


class PlayerInputSource(InputSource):
    """
    Human player input via queue (TUI) or Selector (console).

    TUI mode: inject_action puts in queue, get_action blocks on queue.
    Console mode: get_action calls Selector.run().
    """

    def __init__(self, timeout_seconds: int = 60, selector=None):
        self.timeout_seconds = timeout_seconds
        self._selector = selector
        self._action_queue: queue.Queue[str | None] = queue.Queue()
        self._tui_mode = False
        self._injected = False

    @property
    def mode(self) -> str:
        return "player"

    def supports_realtime_override(self) -> bool:
        return True

    def set_tui_mode(self, enabled: bool = True) -> None:
        """Enable TUI mode - get_action blocks on queue instead of Selector."""
        self._tui_mode = enabled

    def inject_action(self, action: str | None) -> None:
        """TUI calls this to inject player action."""
        self._action_queue.put(action)
        self._injected = True
        self._tui_mode = True

    def get_action(self, turn: int, world: World) -> str | None:
        """Get action from human player. TUI uses queue, console uses Selector."""
        if self._tui_mode:
            try:
                return self._action_queue.get(timeout=self.timeout_seconds)
            except queue.Empty:
                return None
        try:
            return self._action_queue.get_nowait()
        except queue.Empty:
            pass
        if self._selector is None:
            try:
                return self._action_queue.get(timeout=self.timeout_seconds)
            except queue.Empty:
                return None
        return self._request_player_input(turn, world)

    def _request_player_input(self, turn: int, world: World) -> str | None:
        """Display menu and wait for player input using Selector (arrow keys)."""
        from adapters.i18n import t
        from adapters.tui.selector import Selector

        actions = self._get_available_actions()

        selector = Selector(
            title=t('ui.actions.prompt', turn=turn),
            options=actions,
        )
        return selector.run()

    def _parse_input(self, choice: str, actions: list[str]) -> str | None:
        """Parse player input into action name."""
        if choice.startswith("/"):
            return self._handle_command(choice[1:])

        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(actions):
                return actions[idx]
            return None

        if choice in actions:
            return choice

        return None

    def _handle_command(self, cmd: str) -> str | None:
        """Handle /commands. Returns None to skip turn."""
        parts = cmd.split()
        name = parts[0] if parts else ""
        parts[1:]

        from adapters.tui.input import COMMANDS

        if name == "quit":
            return None

        if name in COMMANDS:
            return None

        return None

    def _get_available_actions(self) -> list[str]:
        """Return list of available action names."""
        return [
            "found_circle",
            "write_manifesto",
            "propagate_idea",
            "talk",
            "sabotage",
            "ritualize",
            "join_circle",
            "leave_circle",
        ]
