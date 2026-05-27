"""
resonance_profile.py — ResonanceProfile value object.
"""

from __future__ import annotations

from pydantic import Field

from core.domain.value_objects.resonance_score import ResonanceScore


class ResonanceProfile:
    """
    Profile of resonances (essences) for an entity.

    Attributes:
        dominant: 1-3 dominant resonances, sum ~100
        underlying: Other resonances, 0-100 each
    """

    def __init__(
        self,
        dominant: list[ResonanceScore] | None = None,
        underlying: list[ResonanceScore] | None = None,
    ):
        self.dominant = dominant or []
        self.underlying = underlying or []

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

    @property
    def model_dump(self):
        """Pydantic v2 compatibility."""
        return {
            "dominant": [{"resonance_id": s.resonance_id, "value": s.value} for s in self.dominant],
            "underlying": [{"resonance_id": s.resonance_id, "value": s.value} for s in self.underlying],
        }