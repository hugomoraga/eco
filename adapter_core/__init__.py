"""
adapter_core — Hexagonal architecture adapter layer.

Provides adapters for:
- Human players (via TUI)
- AI players (via LLM backends)
- Network/multiplayer players
- NPC agents (connected to AI backends)
"""

from adapter_core.base import GameAdapter
from adapter_core.human import HumanGameAdapter
from adapter_core.ai import AIGameAdapter
from adapter_core.input_source import (
    InputSource,
    create_input_source,
    create_input_source_for_mode,
    AutoplayInputSource,
    PlayerInputSource,
    HybridInputSource,
)

__all__ = [
    "GameAdapter",
    "HumanGameAdapter",
    "AIGameAdapter",
    "InputSource",
    "create_input_source",
    "create_input_source_for_mode",
    "AutoplayInputSource",
    "PlayerInputSource",
    "HybridInputSource",
]
