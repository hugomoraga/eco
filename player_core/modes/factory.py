"""
player_core.modes.factory — create InputSource based on .env config.

ECO_INPUT_MODE: autoplay | hybrid | player (default: autoplay)
ECO_INTERACTIVE_TURNS: N for hybrid mode (default: 5)
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from player_core.modes.base import InputSource


def create_input_source() -> InputSource:
    """
    Factory to create input source based on .env configuration.

    Does NOT import ui_core at module level to avoid circular deps.
    """
    mode = os.getenv("ECO_INPUT_MODE", "autoplay")

    if mode == "player":
        from player_core.modes.player import PlayerInputSource
        return PlayerInputSource(timeout_seconds=60)

    elif mode == "hybrid":
        from player_core.modes.hybrid import HybridInputSource
        turns = int(os.getenv("ECO_INTERACTIVE_TURNS", "5"))
        return HybridInputSource(interactive_turns=turns)

    else:  # autoplay or default
        from player_core.modes.autoplay import AutoplayInputSource
        return AutoplayInputSource()


def create_input_source_for_mode(mode: str, **kwargs) -> InputSource:
    """Create input source for explicit mode (for testing)."""
    if mode == "player":
        from player_core.modes.player import PlayerInputSource
        return PlayerInputSource(**kwargs)
    elif mode == "hybrid":
        from player_core.modes.hybrid import HybridInputSource
        return HybridInputSource(**kwargs)
    else:
        from player_core.modes.autoplay import AutoplayInputSource
        return AutoplayInputSource()
