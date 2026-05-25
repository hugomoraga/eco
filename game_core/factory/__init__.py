"""
factory/ — centralized creation of all domain entities.

All entities are created via factory functions — no direct instantiation outside factory/.
API:
    create_circle()         — circle.py
    create_echo()           — echo.py
    create_faction()        — faction.py
    create_host()           — host.py (Person ↔ Echo linking)
    create_host_for_echo()  — host.py
    create_npc()            — npc.py (Person + Host, returns Person)
    create_ideas_for_essence() — tags.py
    create_random_idea()    — tags.py
    on_host_death()         — host.py (reincarnation)
    process_circle_tick()  — circle.py
"""
from __future__ import annotations

# Circle
from game_core.factory.circle import (
    create_circle,
    generate_circle_name_with_fallback,
    generate_unique_circle_name,
    process_circle_tick,
)

# Echo
from game_core.factory.echo import create_echo

# Faction
from game_core.factory.faction import create_faction

# Civ
from game_core.factory.civ import create_civ, create_all_civs, create_default_civ

# Host
from game_core.factory.host import create_host, create_host_for_echo, on_host_death

# Person (includes NPC creation)
from game_core.factory.npc import create_npc, create_npcs

# Ideas
from game_core.factory.tags import create_ideas_for_essence, create_random_idea

__all__ = [
    # Circle
    "create_circle",
    "generate_circle_name_with_fallback",
    "generate_unique_circle_name",
    "process_circle_tick",
    # Echo
    "create_echo",
    # Faction
    "create_faction",
    # Civ
    "create_civ",
    "create_all_civs",
    "create_default_civ",
    # Host
    "create_host",
    "create_host_for_echo",
    "on_host_death",
    # Person
    "create_npc",
    "create_npcs",
    # Ideas
    "create_ideas_for_essence",
    "create_random_idea",
]