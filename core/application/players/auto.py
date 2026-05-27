"""
auto.py — AutoPlayer: wraps AutoplayerEngine as a Player.
"""

from adapters.autoplayer.engine import AutoplayerEngine
from adapters.autoplayer.types import AutoplayMode
from core.ports.player import Player


class AutoPlayer(Player):
    """Player that selects actions automatically using AutoplayerEngine."""

    def __init__(
        self,
        seed: int = 42,
        mode: str = "autoplay",
        style_id: str = "preservationist",
    ):
        autoplay_mode = (
            AutoplayMode(mode) if mode in [m.value for m in AutoplayMode] else AutoplayMode.AUTOPLAY
        )
        self._engine = AutoplayerEngine(
            seed=seed,
            mode=autoplay_mode,
            style_id=style_id,
        )

    def select_action(self, turn: int, world, available_actions: list[str]) -> str | None:
        echo = world.get_active_echo()
        if not echo:
            return None
        decision = self._engine.select_action(echo, world, available_actions)
        return decision.selected_action if decision.selected_action else None

    def on_turn_end(self, turn: int, world) -> None:
        pass
