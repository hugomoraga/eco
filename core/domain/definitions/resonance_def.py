"""
resonance_def.py — Wrapper for essences.yaml (resonance definitions).

Static data - loaded once and cached.
"""

from __future__ import annotations

from typing import ClassVar

import yaml
from pathlib import Path


class ResonanceDef:
    """
    Definition of a resonance (essence) from data/essences.yaml.

    Static data - loaded once and cached.
    """
    _cache: ClassVar[dict[str, ResonanceDef] | None] = None
    _affinity_cache: ClassVar[dict[str, dict[str, str]] | None] = None
    _affinity_values: ClassVar[dict[str, int]] = {
        "CONFIRMED": 100,
        "HIGH_AFFINITY": 75,
        "MEDIUM_AFFINITY": 50,
        "NEUTRAL": 25,
        "MEDIUM_TENSION": 10,
        "HIGH_TENSION": -25,
        "INCOMPATIBLE": -75,
    }

    def __init__(self, resonance_id: str, name: str, description: str, attributes: dict[str, float]):
        self.id = resonance_id
        self.name = name
        self.description = description
        self.attributes = attributes

    @classmethod
    def _load(cls) -> dict[str, ResonanceDef]:
        """Load all resonances from YAML."""
        if cls._cache is not None:
            return cls._cache

        data_path = Path(__file__).parent.parent.parent.parent / "data" / "essences.yaml"
        with open(data_path) as f:
            data = yaml.safe_load(f)

        essences = data.get("essences", data)
        cls._cache = {}
        for resonance_id, info in essences.items():
            cls._cache[resonance_id] = ResonanceDef(
                resonance_id=resonance_id,
                name=info.get("name", resonance_id),
                description=info.get("description", ""),
                attributes=info.get("attributes", {}),
            )

        cls._affinity_cache = data.get("affinity_matrix", {})
        return cls._cache

    @classmethod
    def get(cls, resonance_id: str) -> ResonanceDef | None:
        """Get a resonance definition by ID."""
        cache = cls._load()
        return cache.get(resonance_id)

    @classmethod
    def all(cls) -> list[ResonanceDef]:
        """Get all resonance definitions."""
        return list(cls._load().values())

    @classmethod
    def get_affinity(cls, resonance1: str, resonance2: str) -> float:
        """Get affinity value between two resonances."""
        if cls._affinity_cache is None:
            cls._load()

        level = cls._affinity_cache.get(resonance1, {}).get(resonance2, "NEUTRAL")
        return cls._affinity_values.get(level, 25)

    @classmethod
    def get_attribute(cls, resonance_id: str, key: str) -> float:
        """Get an attribute value for a resonance."""
        defn = cls.get(resonance_id)
        if defn is None:
            return 0.0
        return defn.attributes.get(key, 0.0)