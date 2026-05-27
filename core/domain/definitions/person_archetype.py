"""
person_archetype.py — Wrapper for data/archetypes.yaml.

Static data - loaded once and cached.
"""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

import yaml


class PersonArchetype:
    """
    Template for a person archetype from data/archetypes.yaml.

    Static data - loaded once and cached.
    """

    _cache: ClassVar[dict[str, PersonArchetype] | None] = None

    def __init__(
        self,
        archetype_id: str,
        display_name: str,
        description: str,
        color: str,
        goal_weights: dict[str, float],
        action_preferences: list[str],
        base_stats: dict[str, float],
    ):
        self.archetype_id = archetype_id
        self.display_name = display_name
        self.description = description
        self.color = color
        self.goal_weights = goal_weights
        self.action_preferences = action_preferences
        self.base_stats = base_stats

    @classmethod
    def _load(cls) -> dict[str, PersonArchetype]:
        """Load all person archetypes from YAML."""
        if cls._cache is not None:
            return cls._cache

        cls._cache = {}
        archetypes_file = Path(__file__).parent.parent.parent.parent / "data" / "archetypes.yaml"

        with open(archetypes_file) as f:
            data = yaml.safe_load(f)

        for archetype_id, arch_data in data.get("archetypes", {}).items():
            cls._cache[archetype_id] = PersonArchetype(
                archetype_id=archetype_id,
                display_name=arch_data.get("display_name", archetype_id),
                description=arch_data.get("description", ""),
                color=arch_data.get("color", "white"),
                goal_weights=arch_data.get("goal_weights", {}),
                action_preferences=arch_data.get("action_preferences", []),
                base_stats=arch_data.get("base_stats", {}),
            )

        return cls._cache

    @classmethod
    def get(cls, archetype_id: str) -> PersonArchetype | None:
        """Get an archetype by ID."""
        return cls._load().get(archetype_id)

    @classmethod
    def all(cls) -> list[PersonArchetype]:
        """Get all archetypes."""
        return list(cls._load().values())

    @classmethod
    def default(cls) -> PersonArchetype | None:
        """Get the default (neutral) archetype."""
        return cls._load().get("neutral")
