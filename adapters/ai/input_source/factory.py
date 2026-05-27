"""
adapter_core.input_source.factory — create InputSource based on config.

Single source of truth for input mode.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from adapters.ai.input_source.base import InputSource


def create_input_source(autoplay: bool = False) -> InputSource:
    """
    Factory to create input source based on config.

    Does NOT import ui_core at module level to avoid circular deps.
    """
    from adapters.config.config import get_config

    cfg = get_config()
    mode = cfg.input_config.mode

    if autoplay or mode == "autoplay":
        from adapters.ai.input_source.autoplay import AutoplayInputSource
        return AutoplayInputSource()
    elif mode == "player":
        from adapters.ai.input_source.player import PlayerInputSource
        return PlayerInputSource(timeout_seconds=60)
    elif mode == "hybrid":
        from adapters.ai.input_source.hybrid import HybridInputSource
        return HybridInputSource(interactive_turns=cfg.input_config.interactive_turns)
    else:
        from adapters.ai.input_source.autoplay import AutoplayInputSource
        return AutoplayInputSource()


def create_input_source_for_mode(mode: str, **kwargs) -> InputSource:
    """Create input source for explicit mode (for testing)."""
    if mode == "player":
        from adapters.ai.input_source.player import PlayerInputSource
        return PlayerInputSource(**kwargs)
    elif mode == "hybrid":
        from adapters.ai.input_source.hybrid import HybridInputSource
        return HybridInputSource(**kwargs)
    else:
        from adapters.ai.input_source.autoplay import AutoplayInputSource
        return AutoplayInputSource()
