"""
player.py — Hexagonal core: Player port (interface).
Defines the contract for all player types (human, auto, AI).
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.domain.world import World


class Player(ABC):
    """Abstract player interface. Engine asks player for action each turn."""

    @abstractmethod
    def select_action(self, turn: int, world: "World", available_actions: list[str]) -> str | None:
        """
        Called by engine at turn start.
        Returns action name or None to skip.
        """

    def on_turn_end(self, turn: int, world: "World") -> None:
        """Optional hook called after turn completes."""
