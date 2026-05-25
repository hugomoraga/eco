from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel


class CircleEvent(BaseModel):
    type: CircleEventType
    turn: int
    echo_id: str | None = None
    npc_id: str | None = None
    details: str = ""


class WorldClock(BaseModel):
    action_tick: int = 0
    world_tick: int = 0
    historical_tick: int = 0
    turns_per_world_tick: ClassVar[int] = 10

    def advance(self, action_ticks: int = 1) -> None:
        self.action_tick += action_ticks
        self.world_tick = self.action_tick // self.turns_per_world_tick
        self.historical_tick = self.world_tick // 100

    def model_dump(self) -> dict:
        return {
            "action_tick": self.action_tick,
            "world_tick": self.world_tick,
            "historical_tick": self.historical_tick,
        }
