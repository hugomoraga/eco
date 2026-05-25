"""
Host factory — vincula Echo + Person y gestiona el ciclo de vida.
"""
from __future__ import annotations

from game_core.domain.entities import Echo, Host, Person, World


def create_host(
    world: World,
    person_id: str,
    echo_id: str,
) -> Host:
    """
    Vincula una Person (que debe tener type="player") con un Echo.
    Crea el Host y lo registra en world.hosts.
    """
    # Validar que la person existe y está libre
    person = world.get_person(person_id)
    if not person:
        raise ValueError(f"Person not found: {person_id}")
    if person.type != "npc":
        raise ValueError(f"Person {person_id} is already a player")

    # Validar que el echo existe
    echo = world.get_echo(echo_id)
    if not echo:
        raise ValueError(f"Echo not found: {echo_id}")

    # Promover person a player
    person.type = "player"
    person.echo_id = echo_id

    # Crear host
    host = Host(person_id=person_id, echo_id=echo_id)
    world.hosts.append(host)

    # Asegurar que persons[] existe en world y tiene la person
    if not hasattr(world, 'persons'):
        world.persons = []
    if person not in world.persons:
        world.persons.append(person)

    return host


def create_host_for_echo(world: World, echo: Echo) -> Host | None:
    """
    Busca una Person compatible con el echo y la convierte en player.
    Retorna el Host creado, o None si no hay ninguna Person compatible.
    """
    # Buscar una person npc libre
    compatible = None
    for p in world.persons:
        if p.type == "npc":
            compatible = p
            break

    if not compatible:
        return None

    return create_host(world, compatible.id, echo.id)


def on_host_death(world: World, host: Host) -> Host | None:
    """
    Cuando un Host muere:
    1. La Person vuelve a type="npc" y vitality se resetea
    2. El Host se marca como inactivo
    3. El Echo busca nueva Person compatible y reincarna
    """
    person = world.get_person(host.person_id)
    if person:
        person.type = "npc"
        person.vitality = 100.0
        person.echo_id = host.echo_id  # mantener historial

    host.is_active = False

    # Buscar nueva person para el echo
    echo = world.get_echo(host.echo_id)
    if echo:
        echo.reincarnation_count += 1
        return create_host_for_echo(world, echo)

    return None


def find_compatible_person(world: World, echo: Echo) -> Person | None:
    """
    Busca una Person.npc() que sea compatible con el Echo.
    Por ahora: cualquier Person con type="npc" es compatible.
    En el futuro se puede filtrar por essence, archetype, role.
    """
    for p in world.persons:
        if p.type == "npc":
            return p
    return None
