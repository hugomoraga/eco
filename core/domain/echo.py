"""
echo.py — Echo, EchoAttribute
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import ClassVar

from pydantic import BaseModel, Field

from core.domain.enums import EchoPhase
from core.domain.ideas import EssenceProfile, Ideas


class EchoAttribute(BaseModel):
    label: str
    value: float = Field(ge=0, le=100)
    temporal_strain: float = Field(ge=0, default=0.0)
    memory_depth: int = 0


class Echo(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    essence: str = "anarchism"
    essence_profile: EssenceProfile = Field(default_factory=EssenceProfile)
    phase: EchoPhase = EchoPhase.DORMANT
    attributes: list[EchoAttribute] = Field(default_factory=list)
    genealogical_lineage: list[str] = Field(default_factory=list)
    temporal_strain: float = 0.0
    shadow_coherence: float = 100.0
    presence: float = 0.0
    last_awakening: datetime | None = None
    reincarnation_count: int = 0
    action_history: list[str] = Field(default_factory=list)
    last_action_turn: dict[str, int] = Field(default_factory=dict)
    known_tags: list[Ideas] = Field(default_factory=list)
    ideas: list[Ideas] = Field(default_factory=list)
    manifestos: list[str] = Field(default_factory=list)
    circles: list[str] = Field(default_factory=list)

    def get_attribute(self, label: str) -> EchoAttribute | None:
        for attr in self.attributes:
            if attr.label == label:
                return attr
        return None

    def has_tag(self, tag_key: str) -> bool:
        return any(t.to_semantic_key() == tag_key for t in self.known_tags)

    @property
    def identity_modifiers(self) -> dict[str, float]:
        result = {}
        for attr in self.attributes:
            result[attr.label] = attr.value
        return result

    @property
    def dominant_essence(self) -> str | None:
        if self.genealogical_lineage:
            return self.genealogical_lineage[-1]
        return self.essence

    @property
    def dominant_essences(self) -> list[str]:
        return self.essence_profile.dominant_essences()

    @property
    def clarity(self) -> float:
        attr = self.get_attribute("clarity")
        return attr.value if attr else 50.0
