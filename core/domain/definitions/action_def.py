"""
action_def.py — Wrapper for actions.yaml.

Static data - loaded once and cached.
"""

from __future__ import annotations

from typing import ClassVar

import yaml
from pathlib import Path


class ActionDef:
    """
    Definition of an action from data/actions.yaml.

    Static data - loaded once and cached.
    """
    _cache: ClassVar[dict[str, ActionDef] | None] = None

    def __init__(self, action_id: str, cooldown: int, social_cost: float, tags_required: list[str]):
        self.id = action_id
        self.cooldown = cooldown
        self.social_cost = social_cost
        self.tags_required = tags_required

    @classmethod
    def _load(cls) -> dict[str, ActionDef]:
        """Load all actions from YAML."""
        if cls._cache is not None:
            return cls._cache

        data_path = Path(__file__).parent.parent.parent.parent / "data" / "actions.yaml"
        with open(data_path) as f:
            data = yaml.safe_load(f)

        actions = data.get("actions", data)
        cls._cache = {}
        for action_id, info in actions.items():
            cls._cache[action_id] = ActionDef(
                action_id=action_id,
                cooldown=info.get("cooldown", 0),
                social_cost=info.get("social_cost", 0.0),
                tags_required=info.get("tags_required", []),
            )
        return cls._cache

    @classmethod
    def get(cls, action_id: str) -> ActionDef | None:
        """Get an action definition by ID."""
        return cls._load().get(action_id)

    @classmethod
    def all(cls) -> list[ActionDef]:
        """Get all action definitions."""
        return list(cls._load().values())