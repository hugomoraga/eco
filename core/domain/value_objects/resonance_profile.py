"""
resonance_profile.py — ResonanceProfile value object.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from core.domain.value_objects.resonance_score import ResonanceScore


class ResonanceProfile(BaseModel):
    """
    Profile of resonances (essences) for an entity.

    Attributes:
        dominant: 1-3 dominant resonances, sum ~100
        underlying: Other resonances, 0-100 each
    """
    model_config = {"arbitrary_types_allowed": True}

    dominant: list[ResonanceScore] = Field(default_factory=list)
    underlying: list[ResonanceScore] = Field(default_factory=list)

    def get(self, resonance_id: str) -> float:
        """Get value for a resonance_id, returns 0 if not found."""
        for s in self.dominant:
            if s.resonance_id == resonance_id:
                return s.value
        for s in self.underlying:
            if s.resonance_id == resonance_id:
                return s.value
        return 0.0

    def dominant_resonances(self, min_value: float = 15.0) -> list[str]:
        """Return list of resonance_ids with value >= min_value in dominant."""
        return [s.resonance_id for s in self.dominant if s.value >= min_value]

    def to_weights(self) -> dict[str, float]:
        """Convert to dict of resonance_id -> value."""
        result = {}
        for s in self.dominant:
            result[s.resonance_id] = s.value
        for s in self.underlying:
            if s.resonance_id not in result:
                result[s.resonance_id] = s.value
        return result

    def __iter__(self):
        """Allow iteration over all resonance scores."""
        return iter(self.dominant + self.underlying)

    def __len__(self):
        return len(self.dominant) + len(self.underlying)