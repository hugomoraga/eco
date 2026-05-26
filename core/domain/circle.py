"""
circle.py — Circle, CircleEvent
"""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field

from core.domain.enums import CircleStatus, CircleEventType
from core.domain.ideas import Ideas


class CircleEvent(BaseModel):
    type: CircleEventType
    turn: int
    echo_id: str | None = None
    npc_id: str | None = None
    details: str = ""


class Circle(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    echo_id: str | None = None
    essence: str = "anarchism"
    founding_tick: int = 0
    ideology_tags: list[str] = Field(default_factory=list)
    ideas: list[Ideas] = Field(default_factory=list)
    member_ids: list[str] = Field(default_factory=list)
    influence: float = 0.0
    institutionalization_level: float = 0.0
    health: float = 100.0
    status: CircleStatus = CircleStatus.ACTIVE
    dormant_turns: int = 0
    history: list[CircleEvent] = Field(default_factory=list)
    npcs: list[str] = Field(default_factory=list)
    echo_ids: list[str] = Field(default_factory=list)

    @property
    def member_count(self) -> int:
        return len(self.member_ids)

    @property
    def members(self) -> int:
        return len(self.member_ids)

    def add_member(self, echo_id: str) -> None:
        if echo_id not in self.member_ids:
            self.member_ids.append(echo_id)
            self.influence += 2
            self.status = CircleStatus.ACTIVE
            self.dormant_turns = 0

    def remove_member(self, echo_id: str) -> None:
        if echo_id in self.member_ids:
            self.member_ids.remove(echo_id)
            self.influence -= 3

    def is_active(self) -> bool:
        return self.status == CircleStatus.ACTIVE

    def can_grow(self) -> bool:
        return self.influence > 15 and self.member_count < 8 and self.is_active()

    def should_decay(self) -> bool:
        return self.member_count > 1 and self.is_active()

    def should_splinter(self) -> bool:
        return self.member_count >= 6 and self.is_active()
