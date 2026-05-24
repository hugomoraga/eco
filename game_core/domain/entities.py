from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import ClassVar

from pydantic import BaseModel, Field


class TemporalLayer(str, Enum):
    ACTION = "action"
    WORLD = "world"
    HISTORICAL = "historical"


class EchoPhase(str, Enum):
    DORMANT = "dormant"
    AWAKENING = "awakening"
    ACTIVE = "active"
    ECHOING = "echoing"
    FADING = "fading"


class WorldClock(BaseModel):
    action_tick: int = 0
    world_tick: int = 0
    historical_tick: int = 0
    turns_per_world_tick: ClassVar[int] = 10

    def advance(self, action_ticks: int = 1) -> None:
        self.action_tick += action_ticks
        self.world_tick = self.action_tick // self.turns_per_world_tick
        self.historical_tick = self.world_tick // 100

    def model_dump(self) -> dict:
        return {
            "action_tick": self.action_tick,
            "world_tick": self.world_tick,
            "historical_tick": self.historical_tick,
        }


class IdeologicalTag(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: str
    name: str
    essence_weights: dict[str, float] = Field(default_factory=dict)

    def to_semantic_key(self) -> str:
        return f"{self.category}:{self.name}"


class EchoAttribute(BaseModel):
    label: str
    value: float = Field(ge=0, le=100)
    temporal_strain: float = Field(ge=0, default=0.0)
    memory_depth: int = 0


class Echo(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    essence: str = "anarchism"
    phase: EchoPhase = EchoPhase.DORMANT
    attributes: list[EchoAttribute] = Field(default_factory=list)
    genealogical_lineage: list[str] = Field(default_factory=list)
    temporal_strain: float = 0.0
    shadow_coherence: float = 100.0
    presence: float = 0.0
    last_awakening: datetime | None = None
    reincarnation_count: int = 0

    # Action tracking for diminishing returns
    action_history: list[str] = Field(default_factory=list)  # Last N actions
    last_action_turn: dict[str, int] = Field(default_factory=dict)  # action -> turn

    def get_attribute(self, label: str) -> EchoAttribute | None:
        for attr in self.attributes:
            if attr.label == label:
                return attr
        return None

    def has_tag(self, tag_key: str) -> bool:
        return any(t.to_semantic_key() == tag_key for t in self.known_tags)

    known_tags: list[IdeologicalTag] = Field(default_factory=list)
    manifestos: list[str] = Field(default_factory=list)

    @property
    def identity_modifiers(self) -> dict[str, float]:
        result = {}
        for attr in self.attributes:
            result[attr.label] = attr.value
        return result


class Circle(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    echo_id: str | None = None
    essence: str = "anarchism"
    founding_tick: int = 0
    ideology_tags: list[str] = Field(default_factory=list)
    members: int = 1
    influence: float = 0.0
    institutionalization_level: float = 0.0
    health: float = 100.0
    is_dormant: bool = False
    npcs: list[str] = Field(default_factory=list)


class Faction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    essence: str = "anarchism"
    ideology_tags: list[str] = Field(default_factory=list)
    members: int = 0
    influence: float = 0.0
    resources: dict[str, float] = Field(default_factory=lambda: {"food": 50, "infrastructure": 30, "energy": 20})
    goals: list[str] = Field(default_factory=list)
    radicalization: float = 0.0


class World(BaseModel):
    clock: WorldClock = Field(default_factory=WorldClock)
    echoes: list[Echo] = Field(default_factory=list)
    circles: list[Circle] = Field(default_factory=list)
    factions: list[Faction] = Field(default_factory=list)
    manifestos: list[Manifesto] = Field(default_factory=list)
    population: int = 10000
    stability: float = 50.0
    resources: dict[str, float] = Field(default_factory=lambda: {
        "food": 100,
        "infrastructure": 80,
        "energy": 60,
        "knowledge": 40,
        "legitimacy": 70,
    })
    active_echo_id: str | None = None

    def get_echo(self, echo_id: str) -> Echo | None:
        for e in self.echoes:
            if e.id == echo_id:
                return e
        return None

    def get_circle(self, circle_id: str) -> Circle | None:
        for c in self.circles:
            if c.id == circle_id:
                return c
        return None

    def get_active_echo(self) -> Echo | None:
        if self.active_echo_id:
            return self.get_echo(self.active_echo_id)
        return None


class EssenceRegistry:
    _data: ClassVar[dict[str, dict] | None] = None
    _affinity: ClassVar[dict[str, dict] | None] = None

    @classmethod
    def load(cls, path: str = "game_core/data/essences.yaml") -> None:
        import yaml

        with open(path) as f:
            cls._data = yaml.safe_load(f)

        cls._affinity = {}
        for essence, data in cls._data.items():
            cls._affinity[essence] = data.get("affinities", {})

    @classmethod
    def get(cls, essence: str) -> dict:
        if cls._data is None:
            cls.load()
        return cls._data.get(essence, {})

    @classmethod
    def get_order(cls, essence: str) -> float:
        return cls.get(essence).get("order", 0)

    @classmethod
    def get_modifier(cls, essence: str, key: str) -> float:
        return cls.get(essence).get(key, 0)

    @classmethod
    def get_modifiers(cls, essence: str) -> dict[str, float]:
        data = cls.get(essence)
        excluded = {"order", "affinities"}
        return {k: v for k, v in data.items() if k not in excluded}

    @classmethod
    def get_affinity(cls, essence1: str, essence2: str) -> float:
        if cls._affinity is None:
            cls.load()

        affinities = cls._affinity.get(essence1, {})
        return affinities.get(essence2, 0.0)


class Manifesto(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    author_echo_id: str = ""
    content: str = ""
    tags: list[str] = Field(default_factory=list)
    world_tick_created: int = 0
    essence: str = "anarchism"
    influence_generated: float = 0.0