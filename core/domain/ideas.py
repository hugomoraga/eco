"""
ideas.py — Ideas, EssenceScore, EssenceProfile
"""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class EssenceScore(BaseModel):
    essence: str
    value: float = Field(ge=0, le=100)

    def to_key(self) -> str:
        return self.essence


class EssenceProfile(BaseModel):
    dominant: list[EssenceScore] = Field(default_factory=list)
    underlying: list[EssenceScore] = Field(default_factory=list)

    def get(self, essence: str) -> float:
        for s in self.dominant:
            if s.essence == essence:
                return s.value
        for s in self.underlying:
            if s.essence == essence:
                return s.value
        return 0.0

    def dominant_essences(self, min_value: float = 15.0) -> list[str]:
        return [s.essence for s in self.dominant if s.value >= min_value]

    def to_weights(self) -> dict[str, float]:
        result = {}
        for s in self.dominant:
            result[s.essence] = s.value
        for s in self.underlying:
            if s.essence not in result:
                result[s.essence] = s.value
        return result


class Ideas(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: str
    name: str
    essence_weights: dict[str, float] = Field(default_factory=dict)

    def to_semantic_key(self) -> str:
        return f"{self.category}:{self.name}"

    @property
    def dominant_essence(self) -> str | None:
        if not self.essence_weights:
            return None
        return max(self.essence_weights, key=lambda k: self.essence_weights.get(k, 0.0))
