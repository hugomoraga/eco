from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, ClassVar

from pydantic import BaseModel, Field

from game_core.domain.enums import (
    CircleEventType,
    CircleStatus,
    EchoPhase,
    CivAlignment,
)
from game_core.domain.manifesto import Manifesto


class CircleEvent(BaseModel):
    type: CircleEventType
    turn: int
    echo_id: str | None = None
    npc_id: str | None = None
    details: str = ""


# ─── Essence Profile (spec-47) ─────────────────────────────────────────

class EssenceScore(BaseModel):
    essence: str
    value: float = Field(ge=0, le=100)

    def to_key(self) -> str:
        return self.essence


class EssenceProfile(BaseModel):
    dominant: list[EssenceScore] = Field(default_factory=list)
    underlying: list[EssenceScore] = Field(default_factory=list)

    def get(self, essence: str) -> float:
        for s in self.dominant:
            if s.essence == essence:
                return s.value
        for s in self.underlying:
            if s.essence == essence:
                return s.value
        return 0.0

    def dominant_essences(self, min_value: float = 15.0) -> list[str]:
        return [s.essence for s in self.dominant if s.value >= min_value]

    def to_weights(self) -> dict[str, float]:
        """Return all essences as weights dict."""
        result = {}
        for s in self.dominant:
            result[s.essence] = s.value
        for s in self.underlying:
            if s.essence not in result:
                result[s.essence] = s.value
        return result


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


class Ideas(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: str
    name: str
    essence_weights: dict[str, float] = Field(default_factory=dict)

    def to_semantic_key(self) -> str:
        return f"{self.category}:{self.name}"

    @property
    def dominant_essence(self) -> str | None:
        if not self.essence_weights:
            return None
        return max(self.essence_weights, key=lambda k: self.essence_weights.get(k, 0.0))


class Person(BaseModel):
    """
    Individuo base en el mundo.
    - type="npc"    → NPC normal, controlado por el juego
    - type="player" → Person actualmente habitada por el Echo del jugador
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    role: str = ""
    archetype: str = "neutral"

    # Tipo — quién controla esta person
    type: str = "npc"  # Literal["npc", "player"]

    # Historial de Echo — permite saber si fue host anteriormente
    echo_id: str | None = None

    # Civ a la que pertenece (spec-47)
    civ_id: str | None = None

    # Essence profile (spec-47) — reemplazó el campo único essence
    essence_profile: EssenceProfile = Field(default_factory=EssenceProfile)

    # Faction membership
    faction_id: str | None = None
    loyalty: float = 50.0

    # Influence
    influence: float = 0.0

    # Métricas de salud
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


class Host(BaseModel):
    """
    Contexto de encarnación.
    Se "pega" a una Person que tiene type="player".
    NO duplica campos de Person — solo añade contexto de Echo.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    # Link a la Person que habita
    person_id: str

    # Link al Echo que encarna en esta Person
    echo_id: str

    # Métricas del Host
    will: float = 50.0
    presence: float = 50.0

    # Historial
    action_history: list[str] = Field(default_factory=list)
    last_action_turn: dict[str, int] = Field(default_factory=dict)

    # Círculo activo actual
    active_circle_id: str | None = None

    # Contador de acciones este turno (para fatiga)
    actions_this_turn: int = 0

    # Is active (False cuando el host murió y está esperando reincarnación)
    is_active: bool = True

    def record_action(self, action: str, turn: int) -> None:
        self.action_history.append(action)
        self.last_action_turn[action] = turn
        self.actions_this_turn += 1

    def reset_turn_actions(self) -> None:
        self.actions_this_turn = 0


class EchoAttribute(BaseModel):
    label: str
    value: float = Field(ge=0, le=100)
    temporal_strain: float = Field(ge=0, default=0.0)
    memory_depth: int = 0


class Echo(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    essence: str = "anarchism"  # DEPRECATED — use essence_profile.dominant[0]
    essence_profile: EssenceProfile = Field(default_factory=EssenceProfile)
    phase: EchoPhase = EchoPhase.DORMANT
    attributes: list[EchoAttribute] = Field(default_factory=list)
    genealogical_lineage: list[str] = Field(default_factory=list)
    temporal_strain: float = 0.0
    shadow_coherence: float = 100.0
    presence: float = 0.0
    last_awakening: datetime | None = None
    reincarnation_count: int = 0

    action_history: list[str] = Field(default_factory=list)
    last_action_turn: dict[str, int] = Field(default_factory=dict)

    def get_attribute(self, label: str) -> EchoAttribute | None:
        for attr in self.attributes:
            if attr.label == label:
                return attr
        return None

    def has_tag(self, tag_key: str) -> bool:
        return any(t.to_semantic_key() == tag_key for t in self.known_tags)

    known_tags: list[Ideas] = Field(default_factory=list)
    ideas: list[Ideas] = Field(default_factory=list)
    manifestos: list[str] = Field(default_factory=list)
    circles: list[str] = Field(default_factory=list)

    @property
    def identity_modifiers(self) -> dict[str, float]:
        result = {}
        for attr in self.attributes:
            result[attr.label] = attr.value
        return result

    @property
    def dominant_essence(self) -> str | None:
        """La esencia actual del Echo = última del lineage."""
        if self.genealogical_lineage:
            return self.genealogical_lineage[-1]
        return self.essence

    @property
    def dominant_essences(self) -> list[str]:
        return self.essence_profile.dominant_essences()

    @property
    def clarity(self) -> float:
        """Claridad ideológica = atributo clarity o 50."""
        attr = self.get_attribute("clarity")
        return attr.value if attr else 50.0


class Circle(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    echo_id: str | None = None
    essence: str = "anarchism"
    founding_tick: int = 0
    ideology_tags: list[str] = Field(default_factory=list)   # DEPRECATED — use ideas
    ideas: list[Ideas] = Field(default_factory=list)
    member_ids: list[str] = Field(default_factory=list)
    influence: float = 0.0
    institutionalization_level: float = 0.0
    health: float = 100.0
    status: CircleStatus = CircleStatus.ACTIVE
    dormant_turns: int = 0
    history: list[CircleEvent] = Field(default_factory=list)
    npcs: list[str] = Field(default_factory=list)

    echo_ids: list[str] = Field(default_factory=list)          # Echo ids members

    @property
    def member_count(self) -> int:
        return len(self.member_ids)

    @property
    def members(self) -> int:
        return len(self.member_ids)

    def add_member(self, echo_id: str) -> None:
        if echo_id not in self.member_ids:
            self.member_ids.append(echo_id)
            self.influence += 2
            self.status = CircleStatus.ACTIVE
            self.dormant_turns = 0

    def remove_member(self, echo_id: str) -> None:
        if echo_id in self.member_ids:
            self.member_ids.remove(echo_id)
            self.influence -= 3

    def is_active(self) -> bool:
        return self.status == CircleStatus.ACTIVE

    def can_grow(self) -> bool:
        return self.influence > 15 and self.member_count < 8 and self.is_active()

    def should_decay(self) -> bool:
        return self.member_count > 1 and self.is_active()

    def should_splinter(self) -> bool:
        return self.member_count >= 6 and self.is_active()


class Faction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    essence: str = "anarchism"
    ideology_tags: list[str] = Field(default_factory=list)   # DEPRECATED — use ideas
    ideas: list[Ideas] = Field(default_factory=list)
    members: int = 0
    member_ids: list[str] = Field(default_factory=list)       # Person ids
    circle_ids: list[str] = Field(default_factory=list)       # Circle ids
    influence: float = 0.0
    resources: dict[str, float] = Field(default_factory=lambda: {"food": 50, "infrastructure": 30, "energy": 20})
    goals: list[str] = Field(default_factory=list)
    radicalization: float = 0.0


# ─── Civ (spec-47) ─────────────────────────────────────────────────────


class Civ(BaseModel):
    """Civilization — la Civ del mundo, con perfil de esencia dominante."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    meta_id: str = ""                      # id del YAML (e.g. "default", "technocracy")
    name: str = ""
    description: str = ""
    difficulty: str = "normal"

    # Essence profile de la Civ (spec-47)
    essence_profile: EssenceProfile = Field(default_factory=EssenceProfile)

    # Metricas de mundo (copiadas del YAML, no del World)
    population: int = 10000
    stability: float = 50.0
    pressure: float = 30.0
    legitimacy: float = 60.0
    resources_global: float = 70.0
    crisis_threshold: float = 75.0
    collapse_threshold: float = 15.0
    resources: dict[str, float] = Field(default_factory=lambda: {
        "food": 80, "infrastructure": 60, "energy": 50, "knowledge": 50, "legitimacy": 60,
    })

    # Balance target (spec-47: 70% aligned, 30% disident)
    target_aligned_ratio: float = 0.70

    @property
    def dominant_essences(self) -> list[str]:
        return self.essence_profile.dominant_essences()

    def alignment_score(self, person_profile: EssenceProfile) -> float:
        """
        Calculate alignment 0-100 between person and Civ.
        spec-47: weighted average of dominant vs dominant compatibilities.
        """
        score = 0.0
        total_weight = 0.0

        for pd in person_profile.dominant:
            for cd in self.essence_profile.dominant:
                affinity = EssenceRegistry.get_affinity(pd.essence, cd.essence)
                # Ponderado por valores de ambos
                weight = pd.value * cd.value / 100.0
                score += affinity * weight / 100.0
                total_weight += weight

        if total_weight == 0:
            return 50.0  # neutral por defecto

        return min(100.0, max(0.0, score))

    def alignment_status(self, person_profile: EssenceProfile) -> CivAlignment:
        score = self.alignment_score(person_profile)
        if score >= 60:
            return CivAlignment.ALIGNED
        elif score <= 40:
            return CivAlignment.DISIDENT
        else:
            return CivAlignment.NEUTRAL


class World(BaseModel):
    clock: WorldClock = Field(default_factory=WorldClock)
    echoes: list[Echo] = Field(default_factory=list)
    circles: list[Circle] = Field(default_factory=list)
    factions: list[Faction] = Field(default_factory=list)
    manifestos: list[Manifesto] = Field(default_factory=list)

    # Persons — todas las personas del mundo (npc + player)
    persons: list[Person] = Field(default_factory=list)

    # Hosts activos — uno por Person.type="player"
    hosts: list[Host] = Field(default_factory=list)

    # Civs disponibles en el mundo (spec-47)
    civs: list[Civ] = Field(default_factory=list)

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
    pressure: float = 30.0
    legitimacy: float = 60.0
    resources_global: float = 70.0
    crisis_threshold: float = 75.0
    collapse_threshold: float = 15.0

    # ──────────────────────────────────────────────────────────
    # Getters
    # ──────────────────────────────────────────────────────────

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

    def get_person(self, person_id: str) -> Person | None:
        for p in self.persons:
            if p.id == person_id:
                return p
        return None

    def get_host(self, host_id: str) -> Host | None:
        for h in self.hosts:
            if h.id == host_id:
                return h
        return None

    def get_host_for_echo(self, echo_id: str) -> Host | None:
        for h in self.hosts:
            if h.echo_id == echo_id and h.is_active:
                return h
        return None

    def get_host_for_person(self, person_id: str) -> Host | None:
        for h in self.hosts:
            if h.person_id == person_id and h.is_active:
                return h
        return None

    def get_active_echo(self) -> Echo | None:
        if self.active_echo_id:
            return self.get_echo(self.active_echo_id)
        return None

    def get_player_person(self) -> Person | None:
        for p in self.persons:
            if p.type == "player":
                return p
        return None

    def get_player_host(self) -> Host | None:
        pp = self.get_player_person()
        if not pp:
            return None
        return self.get_host_for_person(pp.id)

    def get_player_echo(self) -> Echo | None:
        ph = self.get_player_host()
        if not ph:
            return None
        return self.get_echo(ph.echo_id)

    def get_civ(self, civ_id: str) -> Civ | None:
        for c in self.civs:
            if c.id == civ_id:
                return c
        return None

    def get_civ_by_meta_id(self, meta_id: str) -> Civ | None:
        for c in self.civs:
            if c.meta_id == meta_id:
                return c
        return None

    def get_aligned_persons(self, civ_id: str) -> list[Person]:
        civ = self.get_civ(civ_id)
        if not civ:
            return []
        return [p for p in self.persons if civ.alignment_status(p.essence_profile) == CivAlignment.ALIGNED]

    def get_disident_persons(self, civ_id: str) -> list[Person]:
        civ = self.get_civ(civ_id)
        if not civ:
            return []
        return [p for p in self.persons if civ.alignment_status(p.essence_profile) == CivAlignment.DISIDENT]

    # ──────────────────────────────────────────────────────────
    # Metrics
    # ──────────────────────────────────────────────────────────

    def clamp_metrics(self) -> None:
        self.pressure = max(0.0, min(100.0, self.pressure))
        self.legitimacy = max(0.0, min(100.0, self.legitimacy))
        self.resources_global = max(0.0, min(100.0, self.resources_global))

    def evolve_metrics(self, rng) -> dict[str, float]:
        drift = {
            "pressure": rng.uniform(-1.5, 2.0),
            "legitimacy": rng.uniform(-0.5, 1.0),
            "resources_global": rng.uniform(-0.8, 1.2),
        }

        self.pressure += drift["pressure"]
        self.legitimacy += drift["legitimacy"]
        self.resources_global += drift["resources_global"]

        if self.pressure > 70:
            self.legitimacy -= (self.pressure - 70) * 0.05

        if self.resources_global > 80:
            self.pressure -= (self.resources_global - 80) * 0.03

        self.clamp_metrics()

        return drift

    def is_crisis(self) -> bool:
        return self.pressure > self.crisis_threshold

    def is_collapse_risk(self) -> bool:
        return self.legitimacy < self.collapse_threshold


class EssenceRegistry:
    _data: ClassVar[dict[str, dict] | None] = None
    _affinity: ClassVar[dict[str, dict] | None] = None
    _affinity_values: ClassVar[dict[str, int] | None] = None

    @classmethod
    def load(cls, path: str = "data/essences.yaml") -> None:
        import yaml

        with open(path) as f:
            data = yaml.safe_load(f)

        # New format: {essences: {...}, affinity_matrix: {...}, affinity_values: {...}}
        cls._data = data.get("essences", data)  # backwards compat: old format still works

        # Load affinity matrix
        cls._affinity = data.get("affinity_matrix", {})

        # Load numeric affinity values for calculations
        cls._affinity_values = data.get("affinity_values", {
            "CONFIRMED": 100,
            "HIGH_AFFINITY": 75,
            "MEDIUM_AFFINITY": 50,
            "NEUTRAL": 25,
            "MEDIUM_TENSION": 10,
            "HIGH_TENSION": -25,
            "INCOMPATIBLE": -75,
        })

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

        # New format: affinity_matrix[essence1][essence2] = "CONFIRMED", "HIGH_AFFINITY", etc.
        level = cls._affinity.get(essence1, {}).get(essence2, "NEUTRAL")
        return cls._affinity_values.get(level, 25)


# Rebuild models (spec-47: ensure forward refs resolved after new fields added)
Person.model_rebuild()
Echo.model_rebuild()
Host.model_rebuild()
Circle.model_rebuild()
Faction.model_rebuild()
World.model_rebuild()
Civ.model_rebuild()
