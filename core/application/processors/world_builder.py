"""
world_builder.py — World creation and initialization.
"""

from __future__ import annotations

from core.domain.entities.world import World
from core.application.processors.random import SeededRandom


def build_initial_world(
    seed: int,
    civ_id: str,
) -> World:
    """
    Create initial world state with Civ, Echo, Faction, and initial NPCs.
    """
    from adapters.data_loader.person_dataset import load_person_dataset
    from core.factories import (
        create_all_civs,
        create_civ,
        create_echo,
        create_faction,
        create_ideas_for_essence,
        create_player_person_for_echo,
    )

    rng = SeededRandom.get_instance(seed)

    all_civs = create_all_civs(civs_dir="data/civs")
    selected_civ = create_civ(civ_id, civs_dir="data/civs")
    if selected_civ is None:
        selected_civ = all_civs[0] if all_civs else None

    all_persons = load_person_dataset(persons_dir="data/world/persons")
    if selected_civ:
        for p in all_persons:
            p.civ_id = selected_civ.id

    echo_essence = "anarchism"
    echo_name = "First Echo"
    if selected_civ and selected_civ.meta_id == "technocracy":
        echo_essence = "technocracy"
        echo_name = "Data Walker"
    elif selected_civ and selected_civ.meta_id == "theocracy":
        echo_essence = "monoteism"
        echo_name = "The Anointed"
    elif selected_civ and selected_civ.meta_id == "anarchist_utopia":
        echo_essence = "anarchism"
        echo_name = "Free Spirit"

    echo = create_echo(
        name=echo_name,
        essence=echo_essence,
        seed=seed,
    )
    echo.known_tags = create_ideas_for_essence(rng, echo_essence, count=3)
    echo.genealogical_lineage = [echo.essence]

    faction = create_faction(
        name="Circulo Libertario",
        essence=echo.essence,
        ideas=echo.ideas,
        members=5,
        influence=10.0,
        resources={"food": 50, "infrastructure": 30, "energy": 20},
        goals=["expand_influence", "spread_idea"],
    )

    world = World(
        echoes=[echo],
        factions=[faction],
        active_echo_id=echo.id,
        civs=all_civs,
        population=selected_civ.population if selected_civ else 10000,
        stability=selected_civ.stability if selected_civ else 50.0,
        pressure=selected_civ.pressure if selected_civ else 30.0,
        legitimacy=selected_civ.legitimacy if selected_civ else 60.0,
        resources_global=selected_civ.resources_global if selected_civ else 70.0,
        crisis_threshold=selected_civ.crisis_threshold if selected_civ else 75.0,
        collapse_threshold=selected_civ.collapse_threshold if selected_civ else 15.0,
        resources=selected_civ.resources if selected_civ else {
            "food": 80, "infrastructure": 60, "energy": 50, "knowledge": 50, "legitimacy": 60,
        },
    )

    player_person = create_player_person_for_echo(world, echo)
    if player_person and selected_civ:
        player_person.civ_id = selected_civ.id

    for p in all_persons[:20]:
        world.persons.append(p)

    return world
