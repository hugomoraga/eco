"""
world.py — World, WorldClock
"""

from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel, Field

from core.domain.entities.circle import Circle
from core.domain.entities.civ import Civ
from core.domain.entities.echo import Echo
from core.domain.entities.faction import Faction
from core.domain.entities.host import Host
from core.domain.entities.manifesto import Manifesto
from core.domain.entities.person import Person, PlayerPerson
from core.domain.enums import CivAlignment


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


class World(BaseModel):
    clock: WorldClock = Field(default_factory=WorldClock)
    echoes: list[Echo] = Field(default_factory=list)
    circles: list[Circle] = Field(default_factory=list)
    factions: list[Faction] = Field(default_factory=list)
    manifestos: list[Manifesto] = Field(default_factory=list)
    persons: list[Person] = Field(default_factory=list)
    hosts: list[Host] = Field(default_factory=list)
    civs: list[Civ] = Field(default_factory=list)
    population: int = 10000
    stability: float = 50.0
    resources: dict[str, float] = Field(
        default_factory=lambda: {
            "food": 100,
            "infrastructure": 80,
            "energy": 60,
            "knowledge": 40,
            "legitimacy": 70,
        }
    )
    active_echo_id: str | None = None
    pressure: float = 30.0
    legitimacy: float = 60.0
    resources_global: float = 70.0
    crisis_threshold: float = 75.0
    collapse_threshold: float = 15.0
    transition_turn: int = 0

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

    def get_active_player_person(self) -> PlayerPerson | None:
        for p in self.persons:
            if isinstance(p, PlayerPerson) and p.is_active:
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
        return [
            p
            for p in self.persons
            if civ.alignment_status(p.essence_profile) == CivAlignment.ALIGNED
        ]

    def get_disident_persons(self, civ_id: str) -> list[Person]:
        civ = self.get_civ(civ_id)
        if not civ:
            return []
        return [
            p
            for p in self.persons
            if civ.alignment_status(p.essence_profile) == CivAlignment.DISIDENT
        ]

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
