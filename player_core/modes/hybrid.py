from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_core.domain.entities import World

from player_core.modes.base import InputSource


class HybridInputSource(InputSource):
    """
    Hybrid mode: autoplay by default, interactive at intervals.
    Player can also take control at any time.
    """

    def __init__(self, interactive_turns: int | None = None):
        if interactive_turns is None:
            interactive_turns = int(os.getenv("ECO_INTERACTIVE_TURNS", "5"))
        self.interactive_turns = interactive_turns
        self._player_override = False
        self._pending_action: str | None = None

    @property
    def mode(self) -> str:
        return "hybrid"

    def supports_realtime_override(self) -> bool:
        return True

    def get_action(self, turn: int, world: "World") -> str | None:
        if self._pending_action is not None:
            action = self._pending_action
            self._pending_action = None
            return action

        if self._player_override:
            self._player_override = False
            return self._request_player_input(turn, world)

        if turn % self.interactive_turns == 0:
            return self._request_player_input(turn, world)

        return None

    def inject_action(self, action: str) -> None:
        self._player_override = True
        self._pending_action = action

    def player_take_control(self) -> None:
        self._player_override = True

    def _request_player_input(self, turn: int, world: "World") -> str | None:
        try:
            choice = input().strip()
        except (EOFError, KeyboardInterrupt):
            return None

        if not choice:
            return None

        action_map = {
            "1": "found_circle",
            "2": "write_manifesto",
            "3": "propagate_idea",
            "4": "talk",
            "5": "sabotage",
            "6": "ritualize",
            "7": "join_circle",
            "8": "leave_circle",
        }
        return action_map.get(choice)