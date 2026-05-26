"""
adapter_core.base — GameAdapter abstract base class.

GameAdapter is the main entry point for game control.
Owns the connection to the simulation engine.
Receives events, sends commands.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.systems.simulation import SimulationEngine


@dataclass
class AIResponse:
    """Response from an AI generator adapter."""
    text: str = ""
    success: bool = True
    error: str | None = None
    data: dict | None = None


class AIAdapter(ABC):
    """Base class for AI content generation adapters (NPC generation, narrative, etc.)."""

    @abstractmethod
    def generate_npc(self, context: dict) -> AIResponse:
        """Generate an NPC based on context."""
        ...

    @abstractmethod
    def generate_event(self, context: dict) -> AIResponse:
        """Generate an event based on context."""
        ...

    @abstractmethod
    def generate_manifesto(self, essence: str, context: dict) -> AIResponse:
        """Generate a manifesto based on essence and context."""
        ...


class GameAdapter(ABC):
    """
    Main entry point for game control.
    Owns the connection to the simulation engine.
    Receives events, sends commands.
    """

    def __init__(self, input_source=None):
        self._input_source = input_source
        self._engine: SimulationEngine | None = None
        self._running = False

    @abstractmethod
    def connect(self, engine: SimulationEngine) -> None:
        """Connect this adapter to a simulation engine."""
        ...

    @abstractmethod
    def on_world_state(self, turn: int, world_state: dict) -> None:
        """Called when engine sends world state."""
        ...

    @abstractmethod
    def on_event(self, event_type: str, data: dict) -> None:
        """Called when engine sends an event (crisis, echo_spawned, etc)."""
        ...

    @abstractmethod
    def on_action_result(self, turn: int, action: str, success: bool, message: str) -> None:
        """Called when player's action completes."""
        ...

    def get_action(self, turn: int) -> str | None:
        """Request a decision from the underlying InputSource."""
        if self._input_source is None:
            return None
        from core.domain.entities import World
        return self._input_source.get_action(turn, self._engine.world if self._engine else None)

    @abstractmethod
    def start(self) -> None:
        """Begin the game loop."""
        ...

    @abstractmethod
    def stop(self) -> None:
        """Stop the game loop."""
        ...

    @property
    def input_source(self):
        """The InputSource owned by this adapter."""
        return self._input_source


class MockAdapter(AIAdapter):
    """Mock AI adapter for testing when no real AI is available."""

    def generate_npc(self, context: dict) -> AIResponse:
        return AIResponse(text="Mock NPC", success=True)

    def generate_event(self, context: dict) -> AIResponse:
        return AIResponse(text="Mock Event", success=True)

    def generate_manifesto(self, essence: str, context: dict) -> AIResponse:
        return AIResponse(text="Mock Manifesto", success=True)
