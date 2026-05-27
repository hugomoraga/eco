"""
person.py — Person, NPCPerson, PlayerPerson
"""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field

from core.domain.entities.ideas import EssenceProfile


class Person(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    role: str = ""
    archetype: str = "neutral"
    type: str = "npc"
    echo_id: str | None = None
    civ_id: str | None = None
    essence_profile: EssenceProfile = Field(default_factory=EssenceProfile)
    faction_id: str | None = None
    loyalty: float = 50.0
    influence: float = 0.0
    vitality: float = 100.0
    coherence: float = 50.0

    @property
    def is_player(self) -> bool:
        return self.type == "player"

    @property
    def is_npc(self) -> bool:
        return self.type == "npc"

    def take_damage(self, amount: float) -> None:
        self.vitality = max(0.0, self.vitality - amount)

    def heal(self, amount: float) -> None:
        self.vitality = min(100.0, self.vitality + amount)

    @property
    def dominant_essences(self) -> list[str]:
        return self.essence_profile.dominant_essences()


class NPCPerson(Person):
    """Marker class for NPC-controlled persons."""


class PlayerPerson(Person):
    echo_id: str | None = None
    previous_echo_ids: list[str] = Field(default_factory=list)
    will: float = 50.0
    presence: float = 50.0
    reincarnation_count: int = 0
    action_history: list[str] = Field(default_factory=list)
    last_action_turn: dict[str, int] = Field(default_factory=dict)
    active_circle_id: str | None = None
    actions_this_turn: int = 0
    is_active: bool = True

    def link_echo(self, echo_id: str) -> None:
        if self.echo_id and self.echo_id != echo_id:
            self.previous_echo_ids.append(self.echo_id)
        self.echo_id = echo_id

    def unlink_echo(self) -> None:
        self.echo_id = None
        self.is_active = False

    def reincarnate(self, new_echo_id: str) -> None:
        self.reincarnation_count += 1
        self.link_echo(new_echo_id)
        self.is_active = True
        self.vitality = 100.0
        self.action_history.clear()
        self.last_action_turn.clear()

    def is_available_for_reincarnation(self) -> bool:
        return not self.is_active and self.vitality > 0

    def record_action(self, action: str, turn: int) -> None:
        self.action_history.append(action)
        self.last_action_turn[action] = turn
        self.actions_this_turn += 1

    def reset_turn_actions(self) -> None:
        self.actions_this_turn = 0
