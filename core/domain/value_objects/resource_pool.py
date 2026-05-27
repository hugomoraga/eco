"""
resource_pool.py — ResourcePool value object.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ResourcePool(BaseModel):
    """
    Pool of resources for an entity.

    Note: legitimacy is NOT here - it lives in Civ.
    """
    model_config = {"arbitrary_types_allowed": True}

    food: float = 100.0
    infrastructure: float = 80.0
    energy: float = 60.0
    knowledge: float = 40.0

    def total(self) -> float:
        """Sum of all resources."""
        return self.food + self.infrastructure + self.energy + self.knowledge

    def apply_delta(self, delta: dict[str, float]) -> None:
        """Apply a delta to resources."""
        self.food = max(0, self.food + delta.get("food", 0))
        self.infrastructure = max(0, self.infrastructure + delta.get("infrastructure", 0))
        self.energy = max(0, self.energy + delta.get("energy", 0))
        self.knowledge = max(0, self.knowledge + delta.get("knowledge", 0))

    def clamp(self) -> None:
        """Clamp all values to 0-100."""
        self.food = max(0, min(100, self.food))
        self.infrastructure = max(0, min(100, self.infrastructure))
        self.energy = max(0, min(100, self.energy))
        self.knowledge = max(0, min(100, self.knowledge))

    def to_dict(self) -> dict[str, float]:
        return {
            "food": self.food,
            "infrastructure": self.infrastructure,
            "energy": self.energy,
            "knowledge": self.knowledge,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ResourcePool":
        return cls(
            food=data.get("food", 100.0),
            infrastructure=data.get("infrastructure", 80.0),
            energy=data.get("energy", 60.0),
            knowledge=data.get("knowledge", 40.0),
        )