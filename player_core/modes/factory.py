from __future__ import annotations

import os

from player_core.modes.base import InputSource


def create_input_source() -> InputSource:
    """
    Factory to create input source based on .env configuration.

    ECO_INPUT_MODE: autoplay | hybrid | player (default: autoplay)
    ECO_INTERACTIVE_TURNS: N for hybrid mode (default: 5)
    """
    mode = os.getenv("ECO_INPUT_MODE", "autoplay")

    if mode == "player":
        from ui_core.selector import Selector
        from player_core.modes.player import PlayerInputSource
        selector = Selector("Acciones", [])
        return PlayerInputSource(selector=selector)

    elif mode == "hybrid":
        from player_core.modes.hybrid import HybridInputSource
        turns = int(os.getenv("ECO_INTERACTIVE_TURNS", "5"))
        return HybridInputSource(interactive_turns=turns)

    else:
        from player_core.modes.autoplay import AutoplayInputSource
        return AutoplayInputSource()