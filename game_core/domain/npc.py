from __future__ import annotations

from pydantic import BaseModel, Field
import uuid


class NPC(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    essence: str = "anarchism"
    role: str = ""
    archetype: str = "neutral"
    echo_id: str | None = None
    faction_id: str | None = None
    influence: float = 0.0
    loyalty: float = 50.0