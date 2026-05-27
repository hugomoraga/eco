"""
actor.py — Actor entity.

Unit that competes, wins, and accumulates influence.
Links to Echo (identity), Person (body), and Faction (if belonging).
"""

from __future__ import annotations

import uuid
from typing import Literal

from pydantic import BaseModel, Field

from core.domain.value_objects import ResourcePool


class Actor(BaseModel):
    """
    Unit that plays the game and can win.

    Attributes:
        id: Unique identifier
        name: Display name
        type: human, npc, or faction_ai
        echo_id: Link to Echo (persistent identity)
        person_id: Link to Person (incarnated body)
        faction_id: Link to Faction (political group)
        goal_id: Active goal definition
        influence: Political influence 0+
        resources: Actor's own resources
        action_history: List of actions taken
        idea_ids: Ideas owned by this actor
        doctrine_ids: Doctrines known
        manifesto_ids: Manifestos created
        circle_ids: Circles joined
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""

    type: Literal["human", "npc", "faction_ai"] = "npc"

    # Links
    echo_id: str | None = None
    person_id: str | None = None
    faction_id: str | None = None

    # Meta
    goal_id: str = ""

    # State
    influence: float = 0.0
    resources: ResourcePool = Field(default_factory=ResourcePool)

    # History
    action_history: list[str] = Field(default_factory=list)

    # Memetic resources
    idea_ids: list[str] = Field(default_factory=list)
    doctrine_ids: list[str] = Field(default_factory=list)
    manifesto_ids: list[str] = Field(default_factory=list)
    circle_ids: list[str] = Field(default_factory=list)
