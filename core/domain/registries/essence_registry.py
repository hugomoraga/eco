"""
essence_registry.py — EssenceRegistry
"""

from __future__ import annotations

from typing import ClassVar


class EssenceRegistry:
    _data: ClassVar[dict[str, dict] | None] = None
    _affinity: ClassVar[dict[str, dict] | None] = None
    _affinity_values: ClassVar[dict[str, int] | None] = None

    @classmethod
    def load(cls, path: str = "data/essences.yaml") -> None:
        import yaml

        with open(path) as f:
            data = yaml.safe_load(f)

        cls._data = data.get("essences", data)

        cls._affinity = data.get("affinity_matrix", {})

        cls._affinity_values = data.get("affinity_values", {
            "CONFIRMED": 100,
            "HIGH_AFFINITY": 75,
            "MEDIUM_AFFINITY": 50,
            "NEUTRAL": 25,
            "MEDIUM_TENSION": 10,
            "HIGH_TENSION": -25,
            "INCOMPATIBLE": -75,
        })

    @classmethod
    def get(cls, essence: str) -> dict:
        if cls._data is None:
            cls.load()
        return cls._data.get(essence, {})

    @classmethod
    def get_order(cls, essence: str) -> float:
        return cls.get(essence).get("order", 0)

    @classmethod
    def get_modifier(cls, essence: str, key: str) -> float:
        return cls.get(essence).get(key, 0)

    @classmethod
    def get_modifiers(cls, essence: str) -> dict[str, float]:
        data = cls.get(essence)
        excluded = {"order", "affinities"}
        return {k: v for k, v in data.items() if k not in excluded}

    @classmethod
    def get_affinity(cls, essence1: str, essence2: str) -> float:
        if cls._affinity is None:
            cls.load()

        level = cls._affinity.get(essence1, {}).get(essence2, "NEUTRAL")
        return cls._affinity_values.get(level, 25)
