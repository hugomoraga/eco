from __future__ import annotations

from enum import Enum


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


class CircleStatus(str, Enum):
    ACTIVE = "active"
    DORMANT = "dormant"
    DISSOLVED = "dissolved"


class CircleEventType(str, Enum):
    FOUNDED = "founded"
    JOIN = "join"
    LEAVE = "leave"
    RITUAL = "ritual"
    SPLINTER = "splinter"
    DECAY = "decay"
    NPC_SPAWN = "npc_spawn"
    DISSOLVED = "dissolved"


class EventCategory(str, Enum):
    CRISIS = "crisis"
    RITUAL = "ritual"
    POLITICAL = "political"
    DISCOVERY = "discovery"
    SOCIAL = "social"
    ENTROPY = "entropy"