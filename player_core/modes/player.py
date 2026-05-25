from __future__ import annotations

import signal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_core.domain.entities import World

from player_core.modes.base import InputSource


class TimeoutException(Exception):
    pass


def timeout_handler(signum, frame):
    raise TimeoutException()


class PlayerInputSource(InputSource):
    def __init__(self, timeout_seconds: int = 30, selector=None):
        self.timeout_seconds = timeout_seconds
        self._pending_action: str | None = None
        self._selector = selector

    @property
    def mode(self) -> str:
        return "player"

    def supports_realtime_override(self) -> bool:
        return True

    def get_action(self, turn: int, world: "World") -> str | None:
        if self._pending_action is not None:
            action = self._pending_action
            self._pending_action = None
            return action
        return self._request_player_input(turn, world)

    def inject_action(self, action: str) -> None:
        self._pending_action = action

    def _request_player_input(self, turn: int, world: "World") -> str | None:
        from game_core.i18n import t

        try:
            if self.timeout_seconds > 0:
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(self.timeout_seconds)

            try:
                choice = input().strip()
            except (EOFError, KeyboardInterrupt):
                return None

            if self.timeout_seconds > 0:
                signal.alarm(0)

        except TimeoutException:
            print(f"\n{t('messages:timeout', seconds=self.timeout_seconds)}")
            return None

        if not choice:
            return None

        return self._parse_action_input(choice)

    def _parse_action_input(self, choice: str) -> str | None:
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