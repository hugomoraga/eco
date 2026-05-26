"""
faction.py — Faction
"""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field

from core.domain.ideas import Ideas


class Faction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    essence: str = "anarchism"
    ideology_tags: list[str] = Field(default_factory=list)
    ideas: list[Ideas] = Field(default_factory=list)
    members: int = 0
    member_ids: list[str] = Field(default_factory=list)
    circle_ids: list[str] = Field(default_factory=list)
    influence: float = 0.0
    resources: dict[str, float] = Field(default_factory=lambda: {"food": 50, "infrastructure": 30, "energy": 20})
    goals: list[str] = Field(default_factory=list)
    radicalization: float = 0.0
