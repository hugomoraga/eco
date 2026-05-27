from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.domain import World

from adapters.ai.input_source.base import InputSource


class AutoplayInputSource(InputSource):
    """Full autoplay — never asks for player input."""

    @property
    def mode(self) -> str:
        return "autoplay"

    def get_action(self, turn: int, world: World) -> str | None:
        return None

    def supports_realtime_override(self) -> bool:
        return False
