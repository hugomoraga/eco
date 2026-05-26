"""
entities.py — Re-exports for backward compatibility.

All domain entities have been split into:
- ideas.py: Ideas, EssenceScore, EssenceProfile
- person.py: Person, NPCPerson, PlayerPerson
- host.py: Host
- echo.py: Echo, EchoAttribute
- circle.py: Circle, CircleEvent
- faction.py: Faction
- civ.py: Civ
- world.py: World, WorldClock
- essence_registry.py: EssenceRegistry

Import from submodules for new code:
    from core.domain.world import World
    from core.domain.person import Person

Use this file for backward compatibility:
    from core.domain.entities import World, Person
"""

from __future__ import annotations

from core.domain.circle import Circle, CircleEvent
from core.domain.civ import Civ
from core.domain.echo import Echo, EchoAttribute
from core.domain.registries.essence_registry import EssenceRegistry
from core.domain.enums import (
    CircleEventType,
    CircleStatus,
    CivAlignment,
    EchoPhase,
    EventCategory,
    TemporalLayer,
)
from core.domain.faction import Faction
from core.domain.host import Host
from core.domain.ideas import EssenceProfile, EssenceScore, Ideas
from core.domain.manifesto import Manifesto
from core.domain.person import NPCPerson, Person, PlayerPerson
from core.domain.world import World, WorldClock

# Rebuild models (for backward compatibility)
Person.model_rebuild()
Echo.model_rebuild()
Host.model_rebuild()
Circle.model_rebuild()
Faction.model_rebuild()
World.model_rebuild()
Civ.model_rebuild()

__all__ = [
    # Enums
    "CircleEventType",
    "CircleStatus",
    "CivAlignment",
    "EchoPhase",
    "EventCategory",
    "TemporalLayer",
    # Entities
    "Circle",
    "CircleEvent",
    "Civ",
    "Echo",
    "EchoAttribute",
    "EssenceProfile",
    "EssenceRegistry",
    "EssenceScore",
    "Faction",
    "Host",
    "Ideas",
    "Manifesto",
    "NPCPerson",
    "Person",
    "PlayerPerson",
    "World",
    "WorldClock",
]
