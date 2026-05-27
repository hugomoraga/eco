"""
civ_template.py — Wrapper for civs/*.yaml.

Static data - loaded once and cached.
"""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

import yaml


class CivTemplate:
    """
    Template for a civilization from data/civs/*.yaml.

    Static data - loaded once and cached.
    """

    _cache: ClassVar[dict[str, CivTemplate] | None] = None

    def __init__(
        self,
        meta_id: str,
        name: str,
        description: str,
        difficulty: str,
        population: int,
        stability: float,
        pressure: float,
        legitimacy: float,
        resources: dict[str, float],
        target_aligned_ratio: float,
        dominant_resonances: list[tuple[str, float]],
    ):
        self.meta_id = meta_id
        self.name = name
        self.description = description
        self.difficulty = difficulty
        self.population = population
        self.stability = stability
        self.pressure = pressure
        self.legitimacy = legitimacy
        self.resources = resources
        self.target_aligned_ratio = target_aligned_ratio
        self.dominant_resonances = dominant_resonances

    @classmethod
    def _load(cls) -> dict[str, CivTemplate]:
        """Load all civ templates from YAML."""
        if cls._cache is not None:
            return cls._cache

        cls._cache = {}
        civs_dir = Path(__file__).parent.parent.parent.parent / "data" / "civs"

        for yaml_file in civs_dir.glob("*.yaml"):
            with open(yaml_file) as f:
                data = yaml.safe_load(f)

            meta = data.get("meta", {})
            civ_data = data.get("civ", {})
            essence_data = data.get("essence", {})

            meta_id = meta.get("id", yaml_file.stem)

            dominant = []
            for item in essence_data.get("dominant", []):
                dominant.append((item["essence"], item["value"]))

            cls._cache[meta_id] = CivTemplate(
                meta_id=meta_id,
                name=meta.get("name", meta_id),
                description=meta.get("description", ""),
                difficulty=meta.get("difficulty", "normal"),
                population=civ_data.get("population", 10000),
                stability=civ_data.get("stability", 50.0),
                pressure=civ_data.get("pressure", 30.0),
                legitimacy=civ_data.get("legitimacy", 60.0),
                resources=civ_data.get("resources", {}),
                target_aligned_ratio=0.7,
                dominant_resonances=dominant,
            )

        return cls._cache

    @classmethod
    def get(cls, meta_id: str) -> CivTemplate | None:
        """Get a civ template by meta_id."""
        return cls._load().get(meta_id)

    @classmethod
    def all(cls) -> list[CivTemplate]:
        """Get all civ templates."""
        return list(cls._load().values())

    @classmethod
    def default(cls) -> CivTemplate | None:
        """Get the default civ template."""
        return cls._load().get("default")
