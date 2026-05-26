"""
game_core.autoplayer.engine - Re-exports from adapter_core.autoplayer for backward compatibility.

The actual AutoplayerEngine is now in adapter_core.autoplayer.engine.
This module exists for backward compatibility during the transition.
"""
from adapter_core.autoplayer.engine import AutoplayerEngine

__all__ = ["AutoplayerEngine"]
