"""
factory/ — centralized creation of all domain entities.

All entities are created via factory functions — no direct instantiation outside factory/.
API:
    create_circle()              — circle.py
    create_echo()               — echo.py
    create_faction()            — faction.py
    create_player_person()      — host.py (PlayerPerson ↔ Echo linking)
    create_player_person_for_echo() — host.py
    create_npc_person()         — host.py (NPCPerson creation)
    on_player_death()           — host.py (reincarnation)
    create_npc()                — npc.py (Person + Host, deprecated)
    create_ideas_for_essence()  — tags.py
    create_random_idea()        — tags.py
    process_circle_tick()       — circle.py
"""
from __future__ import annotations

# Circle
from core.factories.circle import (
    create_circle,
    generate_circle_name_with_fallback,
    generate_unique_circle_name,
    process_circle_tick,
)

# Civ
from core.factories.civ import create_all_civs, create_civ, create_default_civ

# Echo
from core.factories.echo import create_echo

# Faction
from core.factories.faction import create_faction

# Person (PlayerPerson and NPCPerson)
from core.factories.host import (
    create_npc_person,
    create_player_person,
    create_player_person_for_echo,
    find_available_npc_person,
    on_player_death,
)

# Person (deprecated - use host.py instead)
from core.factories.npc import (
    create_npc,
    create_npcs,
    load_npcs_from_datasets,
    spawn_npcs_to_world,
)

# Ideas
from core.factories.tags import create_ideas_for_essence, create_random_idea

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
    # Person (new pattern)
    "create_player_person",
    "create_player_person_for_echo",
    "create_npc_person",
    "on_player_death",
    "find_available_npc_person",
    # Person (deprecated - use host.py)
    "create_npc",
    "create_npcs",
    "load_npcs_from_datasets",
    "spawn_npcs_to_world",
    # Ideas
    "create_ideas_for_essence",
    "create_random_idea",
]
