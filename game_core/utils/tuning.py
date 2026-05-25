"""
ECO Tuning Configuration Loader
Reads game_core/tuning.yaml and provides access to tuning values.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class Tuning:
    """Load and provide access to tuning.yaml values."""

    _instance: Tuning | None = None
    _config: dict = {}

    def __new__(cls) -> Tuning:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self) -> None:
        """Load tuning.yaml from data directory."""
        tuning_path = Path(__file__).parent.parent.parent / "data" / "tuning.yaml"
        if tuning_path.exists():
            with open(tuning_path) as f:
                self._config = yaml.safe_load(f) or {}
        else:
            self._config = {}

    def get(self, *keys: str, default: Any = None) -> Any:
        """Get a tuning value by path: get('autoplay', 'action_base_scores', 'found_circle')"""
        value = self._config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
            if value is None:
                return default
        return value

    # Convenience methods for common values
    @property
    def action_base_scores(self) -> dict:
        return self.get("autoplay", "action_base_scores") or {}

    @property
    def style_modifiers(self) -> dict:
        return self.get("autoplay", "style_modifiers") or {}

    @property
    def diminishing_penalty(self) -> float:
        return self.get("diminishing_returns", "penalty_per_repeat") or 0.15

    @property
    def diminishing_min(self) -> float:
        return self.get("diminishing_returns", "min_multiplier") or 0.3

    @property
    def freshness_bonus_per_turn(self) -> float:
        return self.get("diminishing_returns", "freshness_bonus_per_turn") or 0.05

    @property
    def max_freshness_bonus(self) -> float:
        return self.get("diminishing_returns", "max_freshness_bonus") or 0.30

    @property
    def echo_spawn_enabled(self) -> bool:
        return self.get("echo_spawning", "enabled", default=True)

    @property
    def echo_spawn_min_influence(self) -> float:
        return self.get("echo_spawning", "min_influence_threshold") or 80

    @property
    def echo_spawn_cooldown(self) -> int:
        return self.get("echo_spawning", "cooldown_turns") or 5

    @property
    def echo_spawn_base_chance(self) -> float:
        return self.get("echo_spawning", "base_chance") or 0.3

    @property
    def circle_members_for_npc(self) -> int:
        return self.get("circles", "members_for_npc") or 3

    @property
    def tags_per_manifesto(self) -> int:
        return self.get("manifesto", "tags_per_manifesto") or 5

    @property
    def influence_per_tag(self) -> float:
        return self.get("manifesto", "influence_per_tag") or 3.0


# Singleton instance
tuning = Tuning()
