from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import ClassVar

from pydantic import BaseModel, Field


class ActionContext(BaseModel):
    world_tick: int
    action_tick: int
    autoplay: bool = False


class ActionResult(BaseModel):
    success: bool
    message: str
    state_delta: dict = Field(default_factory=dict)
    new_entities: list[str] = Field(default_factory=list)
    consumed_resources: dict[str, float] = Field(default_factory=dict)
    tags_created: list[str] = Field(default_factory=list)
    social_cost: float = 0.0


class Action(ABC):
    name: ClassVar[str] = "action"
    cooldown: ClassVar[int] = 0
    social_cost: ClassVar[float] = 0.0
    tags_required: ClassVar[list[str]] = []
    _last_used_tick: ClassVar[int] = -100

    def __init__(self):
        self.last_used_tick = self._last_used_tick

    @abstractmethod
    def execute(self, echo, world, context: ActionContext) -> ActionResult:
        pass

    def can_execute(self, echo, world, context: ActionContext) -> bool:
        if context.world_tick - self.last_used_tick < self.cooldown:
            return False
        return True

    def _apply_temporal_strain(self, echo, cost: float) -> None:
        echo.temporal_strain += cost
        for attr in echo.attributes:
            attr.temporal_strain += cost * 0.5