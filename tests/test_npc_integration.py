"""
Integration tests for NPC Engine in adapter_core.

Tests that verify NPC AI decision making works correctly.
"""

from __future__ import annotations

from adapters.autoplayer.npc_engine import NPCEngine, get_archetype_for_npc
from core.application.players.auto import AutoPlayer
from core.application.processors.simulation import SimulationEngine


class TestNPCEngine:
    """Tests for NPCEngine."""

    def test_npc_engine_creation(self):
        """NPCEngine can be created."""
        engine = NPCEngine(seed=42)
        assert engine is not None

    def test_npc_engine_with_world(self):
        """NPCEngine can evaluate world state."""
        player = AutoPlayer(seed=42)
        engine = SimulationEngine(
            seed=42,
            max_turns=3,
            player=player,
        )
        engine.run()

        npc_engine = NPCEngine(seed=42)
        world = engine.world

        persons = [p for p in world.persons if p.type == "npc"]
        if persons:
            npc = persons[0]
            metrics = npc_engine.evaluate_npc_state(npc, world)
            assert "loyalty_score" in metrics
            assert "social_influence" in metrics
            assert "vitality_score" in metrics

    def test_npc_archetype_detection(self):
        """get_archetype_for_npc returns correct archetype."""

        class MockPerson:
            archetype = "leader,mystic"
            name = "Test NPC"
            id = "test-123"
            loyalty = 50
            influence = 30
            vitality = 80
            coherence = 70
            essence_profile = None
            action_history = []

        person = MockPerson()
        archetype = get_archetype_for_npc(person)
        assert archetype == "leader"

    def test_npc_archetype_default(self):
        """get_archetype_for_npc returns leader when no archetype."""

        class MockPerson:
            archetype = None
            name = "Test NPC"
            id = "test-123"
            loyalty = 50
            influence = 30
            vitality = 80
            coherence = 70
            essence_profile = None
            action_history = []

        person = MockPerson()
        archetype = get_archetype_for_npc(person)
        assert archetype == "leader"


class TestNPCsInWorld:
    """Tests for NPCs existing in the game world."""

    def test_engine_runs_without_npcs(self):
        """Engine runs fine even if no NPCs exist yet."""
        player = AutoPlayer(seed=42)
        engine = SimulationEngine(
            seed=42,
            max_turns=5,
            player=player,
        )

        engine.run()

        assert engine.turn == 5
        assert engine.world is not None
