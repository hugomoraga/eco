"""
doctrine.py — Doctrine entity.

Idea stabilized into institution.
"""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field

from core.domain.value_objects import ResonanceProfile


class DoctrineBranch(BaseModel):
    """A branch/schism of a Doctrine."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    emphasis: str = ""  # Main interpretation
    core_resonance_id: str = ""
    secondary_resonance_id: str = ""
    distortion: float = 0.0
    follower_count: int = 0
    stability: float = 50.0


class Doctrine(BaseModel):
    """
    Stabilized Idea living in institutions.

    Born from a stable Idea. Can fracture into branches.

    Attributes:
        id: Unique identifier
        name: Display name
        source_idea_id: Idea that birthed this doctrine
        resonance: Resonance profile
        institutionalization: Integration into institutions 0-100
        distortion: Deviation from original idea intent 0-100
        branches: Schisms/forks of this doctrine
        follower_count: Total followers
        stability: Internal stability 0-100
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    name: str = ""
    source_idea_id: str = ""

    resonance: ResonanceProfile = Field(default_factory=ResonanceProfile)

    # Institutionalization
    institutionalization: float = 0.0
    distortion: float = 0.0

    # Fractures
    branches: list[DoctrineBranch] = Field(default_factory=list)

    # Community
    follower_count: int = 0
    stability: float = 50.0
