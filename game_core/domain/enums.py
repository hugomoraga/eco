from __future__ import annotations

from enum import StrEnum


class TemporalLayer(StrEnum):
    ACTION = "action"
    WORLD = "world"
    HISTORICAL = "historical"


class EchoPhase(StrEnum):
    DORMANT = "dormant"
    AWAKENING = "awakening"
    ACTIVE = "active"
    ECHOING = "echoing"
    FADING = "fading"


class CircleStatus(StrEnum):
    ACTIVE = "active"
    DORMANT = "dormant"
    DISSOLVED = "dissolved"


class CircleEventType(StrEnum):
    FOUNDED = "founded"
    JOIN = "join"
    LEAVE = "leave"
    RITUAL = "ritual"
    SPLINTER = "splinter"
    DECAY = "decay"
    NPC_SPAWN = "npc_spawn"
    DISSOLVED = "dissolved"


class EventCategory(StrEnum):
    CRISIS = "crisis"
    RITUAL = "ritual"
    POLITICAL = "political"
    DISCOVERY = "discovery"
    SOCIAL = "social"
    ENTROPY = "entropy"


class CivAlignment(StrEnum):
    ALIGNED = "aligned"     # ≥60
    NEUTRAL = "neutral"     # 40-60
    DISIDENT = "disident"   # ≤40


class ActionCategory(StrEnum):
    SOCIAL = "social"
    CREATIVE = "creative"
    RITUAL = "ritual"
    DESTRUCTIVE = "destructive"
