"""
Faction factory — creates Faction entities.
"""
from __future__ import annotations

import uuid

from game_core.domain.entities import Faction, Ideas


def _str_to_ideas(tag_str: str, essence: str) -> Ideas:
    """Convert a string tag to an Ideas instance."""
    return Ideas(id=str(uuid.uuid4()), category="concept", name=tag_str, essence_weights={essence: 1.0})


def create_faction(
    name: str,
    essence: str,
    ideas: list[Ideas] | None = None,
    members: int = 5,
    influence: float = 10.0,
    resources: dict | None = None,
    goals: list[str] | None = None,
) -> Faction:
    """Create a Faction with defaults."""
    if ideas is None:
        ideas = []
    if resources is None:
        resources = {"food": 50, "infrastructure": 30, "energy": 20}
    if goals is None:
        goals = ["expand_influence", "spread_idea"]

    return Faction(
        name=name,
        essence=essence,
        ideas=ideas,
        members=members,
        influence=influence,
        resources=resources,
        goals=goals,
    )
