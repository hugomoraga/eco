from __future__ import annotations

from pydantic import BaseModel, Field
import uuid


class District(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    city_id: str = ""
    population: int = 0
    stability: float = 50.0
    resources: dict[str, float] = Field(default_factory=dict)


class City(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    districts: list[District] = Field(default_factory=list)
    total_population: int = 0
    influence: float = 0.0
    control_level: float = 50.0