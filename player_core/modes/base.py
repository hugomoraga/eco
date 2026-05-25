from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_core.domain.entities import World


class InputSource(ABC):
    """Abstract base class for player input sources."""

    @abstractmethod
    def get_action(self, turn: int, world: World) -> str | None:
        """
        Returns action name (e.g., "found_circle", "write_manifesto")
        or None for autoplay fallback.
        """
        pass

    @property
    @abstractmethod
    def mode(self) -> str:
        """Returns: 'autoplay' | 'hybrid' | 'player'"""
        pass

    def supports_realtime_override(self) -> bool:
        """Whether input can be injected mid-simulation (for TUI)."""
        return False

    def inject_action(self, action: str) -> None:
        """TUI calls this to inject player action."""
        raise NotImplementedError