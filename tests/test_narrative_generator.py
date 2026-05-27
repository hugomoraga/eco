"""
Tests for game_core.factory.narrative_generator module.
"""

from __future__ import annotations

from core.domain import Circle, CircleStatus, Echo, World, WorldClock
from core.domain.rules.goals import ProgressGoal
from core.factories.narrative_generator import (
    NarrativeFinale,
    NarrativeGenerator,
    NarrativeIntro,
    StoryBeat,
    format_finale,
    format_intro_screen,
    format_story_beat,
)


class TestNarrativeGenerator:
    def test_init_with_seed(self):
        gen1 = NarrativeGenerator(seed=42)
        gen2 = NarrativeGenerator(seed=42)
        assert gen1.rng.random() == gen2.rng.random()

    def test_generate_intro_no_echo(self):
        world = _create_world()
        gen = NarrativeGenerator(seed=42)
        intro = gen.generate_intro(echo=None, world=world)

        assert isinstance(intro, NarrativeIntro)
        assert intro.echo_archetype == "neutral"
        assert isinstance(intro.intro_text, str)
        assert isinstance(intro.legitimacy_text, str)
        assert isinstance(intro.pressure_text, str)

    def test_generate_intro_with_echo(self):
        world = _create_world()
        echo = Echo(name="Test Echo", essence="anarchism")
        gen = NarrativeGenerator(seed=42)
        intro = gen.generate_intro(echo=echo, world=world)

        assert intro.echo_archetype == "neutral"
        assert intro.echo_clarity == echo.clarity

    def test_generate_intro_legitimacy_low(self):
        world = _create_world(legitimacy=20)
        gen = NarrativeGenerator(seed=42)
        intro = gen.generate_intro(echo=None, world=world)

        assert intro.legitimacy == 20
        assert (
            "no confía" in intro.legitimacy_text.lower()
            or "erguidas" in intro.legitimacy_text.lower()
        )

    def test_generate_intro_legitimacy_high(self):
        world = _create_world(legitimacy=80)
        gen = NarrativeGenerator(seed=42)
        intro = gen.generate_intro(echo=None, world=world)

        assert intro.legitimacy == 80
        assert (
            "murmuran" in intro.legitimacy_text.lower()
            or "inevitable" in intro.legitimacy_text.lower()
        )

    def test_generate_intro_pressure_high(self):
        world = _create_world(pressure=85)
        gen = NarrativeGenerator(seed=42)
        intro = gen.generate_intro(echo=None, world=world)

        assert intro.pressure == 85
        assert (
            "revolución" in intro.pressure_text.lower() or "actuar" in intro.pressure_text.lower()
        )

    def test_generate_story_beat_act_1(self):
        world = _create_world()
        gen = NarrativeGenerator(seed=42)
        beat = gen.generate_story_beat(turn=3, world=world, npc_actions=[])

        assert isinstance(beat, StoryBeat)
        assert beat.turn == 3
        assert beat.act_number == 1
        assert "Despertar" in beat.act

    def test_generate_story_beat_act_2(self):
        world = _create_world()
        gen = NarrativeGenerator(seed=42)
        beat = gen.generate_story_beat(turn=10, world=world, npc_actions=[])

        assert beat.act_number == 2
        assert "Efervescencia" in beat.act

    def test_generate_story_beat_act_3(self):
        world = _create_world()
        gen = NarrativeGenerator(seed=42)
        beat = gen.generate_story_beat(turn=17, world=world, npc_actions=[])

        assert beat.act_number == 3
        assert "Cruce" in beat.act

    def test_generate_story_beat_state_summary(self):
        world = _create_world_with_circles(3, legitimacy=65, pressure=45)
        gen = NarrativeGenerator(seed=42)
        beat = gen.generate_story_beat(turn=5, world=world, npc_actions=[])

        assert beat.state_summary["circles"] == 3
        assert beat.state_summary["legitimacy"] == 65
        assert beat.state_summary["pressure"] == 45

    def test_generate_finale_victory(self):
        world = _create_world_with_circles(5)
        player_goal = ProgressGoal(
            goal_id="pg1",
            owner_id="player",
            owner_name="Tú",
            turn_limit=20,
            metric="circles",
            target=5.0,
            description="Fundar 5 círculos",
        )
        rival_goal = ProgressGoal(
            goal_id="rg1",
            owner_id="npc1",
            owner_name="Rival NPC",
            turn_limit=20,
            metric="circles",
            target=3.0,
            description="Fundar 3 círculos",
        )

        gen = NarrativeGenerator(seed=42)
        finale = gen.generate_finale(
            turn=20,
            world=world,
            player_goal=player_goal,
            all_goals=[player_goal, rival_goal],
            winner="player",
            winner_name="Tú",
        )

        assert isinstance(finale, NarrativeFinale)
        assert finale.outcome == "victory"
        assert finale.player_goal_progress == 1.0
        assert finale.winner == "player"

    def test_generate_finale_close_defeat(self):
        world = _create_world_with_circles(3)
        player_goal = ProgressGoal(
            goal_id="pg2",
            owner_id="player",
            owner_name="Tú",
            turn_limit=20,
            metric="circles",
            target=10.0,
            description="Fundar 10 círculos",
        )

        gen = NarrativeGenerator(seed=42)
        finale = gen.generate_finale(
            turn=20,
            world=world,
            player_goal=player_goal,
            all_goals=[player_goal],
            winner="close",
            winner_name="Tú",
        )

        assert finale.outcome == "close_defeat"


class TestFormatFunctions:
    def test_format_intro_screen(self):
        intro = NarrativeIntro(
            echo_archetype="artisan",
            echo_essence="anarchism",
            echo_clarity=70.0,
            legitimacy=50.0,
            pressure=30.0,
            intro_text="Eres la voz de los artesanos.",
            legitimacy_text="Hay esperanza.",
            pressure_text="Los poderosos duermen.",
        )
        output = format_intro_screen(intro)
        assert "artisan" in output
        assert "anarchism" in output
        assert "70" in output
        assert "ECO DE LA REVOLUCIÓN" in output

    def test_format_story_beat(self):
        beat = StoryBeat(
            turn=5,
            act="Acto I: El Despertar",
            act_number=1,
            title="LA SEMILLA SE PLARTA",
            narrative="Los círculos comienzan a formarse.",
            state_summary={"circles": 2, "legitimacy": 55, "pressure": 40},
        )
        output = format_story_beat(beat)
        assert "Acto I" in output
        assert "círculos" in output
        assert "55" in output

    def test_format_finale(self):
        finale = NarrativeFinale(
            turn=20,
            outcome="victory",
            outcome_text="¡Victoria!",
            story_summary="Tu eco resonó.",
            final_stats={"legitimacy": 80, "circles": 5, "circles_created": 5, "pressure": 40},
            player_goal_progress=1.0,
            winner="player",
            winner_name="Tú",
        )
        player_goal = ProgressGoal(
            goal_id="pg3",
            owner_id="player",
            owner_name="Tú",
            turn_limit=20,
            metric="circles",
            target=5.0,
            description="Fundar 5 círculos",
        )

        output = format_finale(finale, player_goal=player_goal, top_rival_goals=[])
        assert "EPÍLOGO" in output
        assert "VICTORIA" in output
        assert "80" in output


def _create_world(
    legitimacy: float = 50.0,
    pressure: float = 30.0,
    resources: float = 50.0,
) -> World:
    world = World(
        clock=WorldClock(),
        circles=[],
        legitimacy=legitimacy,
        pressure=pressure,
        resources_global=resources,
    )
    return world


def _create_world_with_circles(
    num_circles: int,
    legitimacy: float = 50.0,
    pressure: float = 30.0,
) -> World:
    circles = [
        Circle(
            id=f"circle_{i}",
            name=f"Circle {i}",
            status=CircleStatus.ACTIVE,
        )
        for i in range(num_circles)
    ]
    world = World(
        clock=WorldClock(),
        circles=circles,
        legitimacy=legitimacy,
        pressure=pressure,
        resources_global=50.0,
    )
    return world
