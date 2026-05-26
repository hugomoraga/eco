"""
Person factory — creación de PlayerPerson y NPCPerson.

Replaces the old Host pattern. Instead of separate Host entity linked to Person,
we now create PlayerPerson directly which contains all incarnation context.
"""
from __future__ import annotations

from game_core.domain.entities import Echo, NPCPerson, PlayerPerson, World


def create_player_person(
    world: World,
    echo_id: str,
    name: str = "",
    archetype: str = "neutral",
    role: str = "",
) -> PlayerPerson:
    """
    Crear una PlayerPerson vinculada a un Echo.

    Args:
        world: World destino
        echo_id: ID del Echo a vincular
        name: Nombre de la person
        archetype: Archetype (neutral, radical, mediator, etc.)
        role: Rol ( propagator, scientist, etc.)

    Returns:
        PlayerPerson creada y registrada en world.persons
    """
    echo = world.get_echo(echo_id)
    if not echo:
        raise ValueError(f"Echo not found: {echo_id}")

    person = PlayerPerson(
        name=name,
        archetype=archetype,
        role=role,
        type="player",
        echo_id=echo_id,
        is_active=True,
    )

    world.persons.append(person)
    return person


def create_player_person_for_echo(world: World, echo: Echo) -> PlayerPerson | None:
    """
    Busca una NPCPerson compatible y la convierte en PlayerPerson.
    Retorna la PlayerPerson creada, o None si no hay NPCPerson disponible.
    """
    compatible = find_available_npc_person(world)
    if not compatible:
        return None

    player = _promote_to_player(world, compatible, echo)
    return player


def _promote_to_player(world: World, npc: NPCPerson, echo: Echo) -> PlayerPerson:
    """
    Promote an NPCPerson to PlayerPerson by creating a new PlayerPerson
    from the NPCPerson data and linking to the echo.
    """
    player = PlayerPerson(
        id=npc.id,
        name=npc.name,
        role=npc.role,
        archetype=npc.archetype,
        type="player",
        echo_id=echo.id,
        civ_id=npc.civ_id,
        essence_profile=npc.essence_profile,
        faction_id=npc.faction_id,
        loyalty=npc.loyalty,
        influence=npc.influence,
        vitality=npc.vitality,
        coherence=npc.coherence,
        is_active=True,
    )
    for i, p in enumerate(world.persons):
        if p.id == npc.id:
            world.persons[i] = player
            break
    return player


def on_player_death(world: World, person: PlayerPerson) -> PlayerPerson | None:
    """
    Cuando una PlayerPerson muere:
    1. La person se marca inactiva y vitality se resetea
    2. El echo busca nueva NPCPerson compatible y reincarna

    Returns:
        Nueva PlayerPerson para el mismo echo, o None si no hay disponible
    """
    echo = world.get_echo(person.echo_id) if person.echo_id else None

    person.unlink_echo()
    person.vitality = 100.0

    if echo:
        return create_player_person_for_echo(world, echo)

    return None


def find_available_npc_person(world: World) -> NPCPerson | None:
    """
    Busca una NPCPerson disponible para convertirse en PlayerPerson.
    Por ahora: cualquier NPCPerson es compatible.
    """
    for p in world.persons:
        if isinstance(p, NPCPerson):
            return p
    return None


def create_npc_person(
    world: World,
    name: str = "",
    archetype: str = "neutral",
    role: str = "",
    civ_id: str | None = None,
) -> NPCPerson:
    """
    Crear una NPCPerson controlada por el juego.

    Args:
        world: World destino
        name: Nombre
        archetype: Archetype
        role: Rol
        civ_id: Civilization ID

    Returns:
        NPCPerson creada y registrada
    """
    person = NPCPerson(
        name=name,
        archetype=archetype,
        role=role,
        type="npc",
        civ_id=civ_id,
    )

    world.persons.append(person)
    return person
