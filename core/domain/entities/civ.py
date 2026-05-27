"""
civ.py — Civ
"""

from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel, Field

from core.domain.enums import CivAlignment
from core.domain.entities.ideas import EssenceProfile


class Civ(BaseModel):
    id: str = Field(default_factory=lambda: str(__import__("uuid").uuid4()))
    meta_id: str = ""
    name: str = ""
    description: str = ""
    difficulty: str = "normal"
    essence_profile: EssenceProfile = Field(default_factory=EssenceProfile)
    population: int = 10000
    stability: float = 50.0
    pressure: float = 30.0
    legitimacy: float = 60.0
    resources_global: float = 70.0
    crisis_threshold: float = 75.0
    collapse_threshold: float = 15.0
    resources: dict[str, float] = Field(default_factory=lambda: {
        "food": 80, "infrastructure": 60, "energy": 50, "knowledge": 50, "legitimacy": 60,
    })
    target_aligned_ratio: float = 0.70

    @property
    def dominant_essences(self) -> list[str]:
        return self.essence_profile.dominant_essences()

    def alignment_score(self, person_profile: EssenceProfile) -> float:
        from core.domain.registries.essence_registry import EssenceRegistry

        score = 0.0
        total_weight = 0.0

        for pd in person_profile.dominant:
            for cd in self.essence_profile.dominant:
                affinity = EssenceRegistry.get_affinity(pd.essence, cd.essence)
                weight = pd.value * cd.value / 100.0
                score += affinity * weight / 100.0
                total_weight += weight

        if total_weight == 0:
            return 50.0

        return min(100.0, max(0.0, score))

    def alignment_status(self, person_profile: EssenceProfile) -> CivAlignment:
        score = self.alignment_score(person_profile)
        if score >= 60:
            return CivAlignment.ALIGNED
        elif score <= 40:
            return CivAlignment.DISIDENT
        else:
            return CivAlignment.NEUTRAL
