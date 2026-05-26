"""
Tests for game_core.factory functions.
"""
from __future__ import annotations

import pytest

from core.domain.entities import (
    Circle,
    Echo,
    EchoPhase,
    NPCPerson,
    Person,
    PlayerPerson,
    World,
)
from core.factories import (
    create_circle,
    create_echo,
    create_faction,
    create_npc_person,
    create_player_person,
    create_player_person_for_echo,
    find_available_npc_person,
    generate_circle_name_with_fallback,
    generate_unique_circle_name,
    on_player_death,
)


class TestCreateEcho:
    def test_create_echo_basic(self):
        echo = create_echo(name="Test Echo", essence="anarchism")
        assert echo.name == "Test Echo"
        assert echo.essence == "anarchism"
        assert echo.phase == EchoPhase.ACTIVE
        assert echo.genealogical_lineage == ["anarchism"]

    def test_create_echo_with_attributes(self):
        from core.domain.entities import EchoAttribute
        attrs = [EchoAttribute(label="clarity", value=80.0)]
        echo = create_echo(name="Att Echo", essence="technocracy", attributes=attrs)
        assert echo.get_attribute("clarity").value == 80.0

    def test_create_echo_adds_to_world(self):
        world = World()
        echo = create_echo(name="World Echo", essence="absurdism")
        world.echoes.append(echo)
        assert echo in world.echoes


class TestCreateCircle:
    def test_create_circle_basic(self):
        world = World()
        echo = create_echo(name="Founder", essence="anarchism")
        world.echoes.append(echo)
        circle = create_circle(world, echo=echo, essence="anarchism")
        assert circle.essence == "anarchism"
        assert circle.status.value == "active"

    def test_create_circle_registered_in_world(self):
        world = World()
        echo = create_echo(name="Founder2", essence="collectivism")
        world.echoes.append(echo)
        circle = create_circle(world, echo=echo, essence="collectivism")
        assert circle in world.circles

    def test_create_circle_without_name_generates_name(self):
        world = World()
        echo = create_echo(name="Founder3", essence="ecology")
        world.echoes.append(echo)
        circle = create_circle(world, echo=echo, essence="ecology")
        assert circle.name != ""


class TestGenerateCircleName:
    def test_generate_unique_circle_name(self):
        name = generate_unique_circle_name("anarchism", [])
        assert "Circle" in name or "Círculo" in name

    def test_generate_unique_avoids_duplicates(self):
        circle1 = Circle(name="Circle of the Free", essence="anarchism")
        name = generate_unique_circle_name("anarchism", [circle1])
        assert name != circle1.name

    def test_generate_circle_name_with_fallback(self):
        name = generate_circle_name_with_fallback("thelema", [])
        assert name != ""


class TestCreatePlayerPerson:
    def test_create_player_person_basic(self):
        world = World()
        echo = create_echo(name="Soul", essence="anarchism")
        world.echoes.append(echo)

        person = create_player_person(world, echo_id=echo.id, name="Host Person")
        assert person.name == "Host Person"
        assert person.type == "player"
        assert person.echo_id == echo.id
        assert person.is_active is True

    def test_create_player_person_registered(self):
        world = World()
        echo = create_echo(name="Soul2", essence="technocracy")
        world.echoes.append(echo)

        person = create_player_person(world, echo_id=echo.id)
        assert person in world.persons
        assert isinstance(person, PlayerPerson)

    def test_create_player_person_invalid_echo_raises(self):
        world = World()
        with pytest.raises(ValueError, match="Echo not found"):
            create_player_person(world, echo_id="nonexistent")

    def test_player_person_link_echo(self):
        world = World()
        echo1 = create_echo(name="Soul1", essence="anarchism")
        echo2 = create_echo(name="Soul2", essence="technocracy")
        world.echoes.extend([echo1, echo2])

        person = create_player_person(world, echo_id=echo1.id)
        assert person.echo_id == echo1.id

        person.link_echo(echo2.id)
        assert person.echo_id == echo2.id
        assert echo1.id in person.previous_echo_ids

    def test_player_person_unlink_echo(self):
        world = World()
        echo = create_echo(name="Soul", essence="absurdism")
        world.echoes.append(echo)

        person = create_player_person(world, echo_id=echo.id)
        person.unlink_echo()
        assert person.echo_id is None
        assert person.is_active is False

    def test_player_person_reincarnate(self):
        world = World()
        echo = create_echo(name="Soul", essence="thelema")
        world.echoes.append(echo)

        person = create_player_person(world, echo_id=echo.id)
        person.vitality = 50.0
        person.action_history.append("action1")

        person.reincarnate(echo.id)
        assert person.is_active is True
        assert person.vitality == 100.0
        assert person.action_history == []
        assert person.reincarnation_count == 1


class TestCreateNPCPerson:
    def test_create_npc_person_basic(self):
        world = World()
        npc = create_npc_person(world, name="NPC One", archetype="radical")
        assert npc.name == "NPC One"
        assert npc.type == "npc"
        assert isinstance(npc, NPCPerson)

    def test_create_npc_person_registered(self):
        world = World()
        npc = create_npc_person(world)
        assert npc in world.persons

    def test_create_npc_person_is_not_player(self):
        world = World()
        npc = create_npc_person(world, name="NPC Two")
        assert npc.is_player is False
        assert npc.is_npc is True


class TestCreatePlayerPersonForEcho:
    def test_promotes_npc_to_player(self):
        world = World()
        echo = create_echo(name="Soul", essence="anarchism")
        world.echoes.append(echo)

        npc = create_npc_person(world, name="NPC Candidate")
        assert npc.type == "npc"

        player = create_player_person_for_echo(world, echo)
        assert player is not None
        assert player.type == "player"
        assert player.echo_id == echo.id
        assert isinstance(player, PlayerPerson)

    def test_returns_none_when_no_npc_available(self):
        world = World()
        echo = create_echo(name="Soul", essence="anarchism")
        world.echoes.append(echo)

        player = create_player_person_for_echo(world, echo)
        assert player is None


class TestFindAvailableNPCPerson:
    def test_finds_npc_person(self):
        world = World()
        npc1 = create_npc_person(world, name="NPC A")
        create_npc_person(world, name="NPC B")

        found = find_available_npc_person(world)
        assert found is not None
        assert found.name == "NPC A"

    def test_returns_none_when_all_occupied(self):
        world = World()
        npc1 = create_npc_person(world, name="NPC1")
        npc2 = create_npc_person(world, name="NPC2")

        echo1 = create_echo(name="Soul1", essence="anarchism")
        echo2 = create_echo(name="Soul2", essence="technocracy")
        world.echoes.extend([echo1, echo2])

        # create_player_person_for_echo consumes the NPC and converts it
        player1 = create_player_person_for_echo(world, echo1)
        player2 = create_player_person_for_echo(world, echo2)
        assert player1 is not None
        assert player2 is not None

        found = find_available_npc_person(world)
        assert found is None


class TestOnPlayerDeath:
    def test_marks_player_inactive(self):
        world = World()
        echo = create_echo(name="Soul", essence="anarchism")
        world.echoes.append(echo)

        player = create_player_person(world, echo_id=echo.id)
        assert player.is_active is True

        on_player_death(world, player)
        assert player.is_active is False

    def test_resets_vitality(self):
        world = World()
        echo = create_echo(name="Soul", essence="absurdism")
        world.echoes.append(echo)

        player = create_player_person(world, echo_id=echo.id)
        player.vitality = 0.0

        on_player_death(world, player)
        assert player.vitality == 100.0


class TestCreateFaction:
    def test_create_faction_basic(self):
        faction = create_faction(name="Test Faction", essence="technocracy")
        assert faction.name == "Test Faction"
        assert faction.essence == "technocracy"

    def test_create_faction_registered(self):
        world = World()
        faction = create_faction(name="Faction Two", essence="ecology")
        world.factions.append(faction)
        assert faction in world.factions
