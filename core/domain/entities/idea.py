"""
idea.py — Idea entity.

Active meme runtime entity.
Created by Manifesto or actions.
"""

from __future__ import annotations

import uuid
from enum import Enum

from pydantic import BaseModel, Field

from core.domain.value_objects import ResonanceProfile


class IdeaState(str, Enum):
    """Lifecycle state of an Idea."""
    GERMINATING = "germinating"
    EXPANDING = "expanding"
    STABLE = "stable"
    MUTATING = "mutating"
    DEAD = "dead"


class IdeaKind(str, Enum):
    """Kind of idea."""
    BELIEF = "belief"
    RUMOR = "rumor"
    MOVEMENT_SEED = "movement_seed"
    MANIFESTO_SEED = "manifesto_seed"


class Idea(BaseModel):
    """
    Active meme runtime entity.

    Born from Manifesto or actions. Can stabilize into Doctrine.

    Attributes:
        id: Unique identifier
        author_actor_id: Actor who created this idea
        name: Display name
        kind: Type of idea
        resonance: Resonance weights
        clarity: Coherence, resistance to distortion 0-100
        virality: Propagation capacity 0-100
        stability: Resistance to mutation 0-100
        mutation_risk: Probability of uncontrolled transformation 0-100
        spread: Current reach 0+
        followers: Number of followers
        state: Current lifecycle state
        world_tick_created: When created
        parent_idea_ids: Ideas this was born from
        child_idea_ids: Ideas born from this
        distortion: Deviation from original intent 0-100
        doctrine_id: If stabilized into a Doctrine
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    author_actor_id: str = ""

    name: str = ""
    kind: IdeaKind = IdeaKind.BELIEF

    resonance: ResonanceProfile = Field(default_factory=ResonanceProfile)

    # Memetic attributes
    clarity: float = 50.0
    virality: float = 50.0
    stability: float = 50.0
    mutation_risk: float = 50.0
    spread: float = 0.0
    followers: int = 0

    # Lifecycle
    state: IdeaState = IdeaState.GERMINATING
    world_tick_created: int = 0

    # Genealogy
    parent_idea_ids: list[str] = Field(default_factory=list)
    child_idea_ids: list[str] = Field(default_factory=list)

    # Distortion and stabilization
    distortion: float = 0.0
    doctrine_id: str | None = None