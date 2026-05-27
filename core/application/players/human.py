"""
human.py — HumanPlayer: adaptable player that works with any UI.

Decoupled from TUI by using PlayerInputSource internally:
- TUI mode: inject_action() via queue
- Console mode: Selector-based input
"""

from core.ports.player import Player
from infra.logging import get_logger

log = get_logger(__name__)


class HumanPlayer(Player):
    """
    Player that gets actions via PlayerInputSource.

    Works with any UI:
    - TUI: calls submit_action() to inject into queue
    - Console: uses Selector for interactive input
    """

    def __init__(self, timeout_seconds: int = 60, selector=None):
        self._timeout = timeout_seconds
        from adapters.ai.input_source.player import PlayerInputSource
        self._input_source = PlayerInputSource(timeout_seconds=timeout_seconds, selector=selector)

    def select_action(self, turn: int, world, available_actions: list[str]) -> str | None:
        log.warning("HumanPlayer_requesting_action", turn=turn)
        action = self._input_source.get_action(turn, world)
        log.warning("HumanPlayer_returning_action", turn=turn, action=action)
        return action

    def submit_action(self, action: str | None) -> None:
        """Called by TUI to submit player's action choice."""
        self._input_source.inject_action(action)
        log.warning("HumanPlayer_action_received", action=action)
