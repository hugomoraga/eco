"""
PlayerInputSource — human player input with timeout.

Uses ui_core interface to display actions and capture player choice.
Falls back to timeout if no input.
"""

from __future__ import annotations

import signal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_core.domain.entities import World

from adapter_core.input_source.base import InputSource


class TimeoutException(Exception):
    pass


def _timeout_handler(signum, frame):
    raise TimeoutException()


class PlayerInputSource(InputSource):
    """
    Human player input with timeout.

    Shows action menu, captures player choice via number or command.
    Uses ui_core for display and input.
    """

    def __init__(self, timeout_seconds: int = 60, selector=None):
        self.timeout_seconds = timeout_seconds
        self._pending_action: str | None = None
        self._selector = selector

    @property
    def mode(self) -> str:
        return "player"

    def supports_realtime_override(self) -> bool:
        return True

    def inject_action(self, action: str) -> None:
        """TUI calls this to inject player action mid-simulation."""
        self._pending_action = action

    def get_action(self, turn: int, world: World) -> str | None:
        """Get action from human player. Returns action name or None on timeout."""
        if self._pending_action is not None:
            action = self._pending_action
            self._pending_action = None
            return action

        return self._request_player_input(turn, world)

    def _request_player_input(self, turn: int, world: World) -> str | None:
        """Display menu and wait for player input using Selector (arrow keys)."""
        from game_core.i18n import t
        from ui_core.selector import Selector

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

        from ui_core.input import COMMANDS

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
