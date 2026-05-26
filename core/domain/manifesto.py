from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class Manifesto(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    author_echo_id: str = ""
    content: str = ""
    tags: list[str] = Field(default_factory=list)
    world_tick_created: int = 0
    essence: str = "anarchism"
    influence_generated: float = 0.0
