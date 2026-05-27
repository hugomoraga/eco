"""
test_new_entities.py — Tests for new spec-57 entities.
"""

from __future__ import annotations

from core.domain.entities.actor import Actor
from core.domain.entities.doctrine import Doctrine, DoctrineBranch
from core.domain.entities.idea import Idea, IdeaKind, IdeaState
from core.domain.value_objects import ResonanceProfile, ResonanceScore, ResourcePool


class TestActor:
    """Tests for Actor entity."""

    def test_create_actor(self):
        actor = Actor(name="Test Actor", type="human")
        assert actor.name == "Test Actor"
        assert actor.type == "human"
        assert actor.influence == 0.0
        assert isinstance(actor.resources, ResourcePool)

    def test_actor_default_npc(self):
        actor = Actor(name="NPC Actor")
        assert actor.type == "npc"

    def test_actor_links(self):
        actor = Actor(
            name="Test",
            echo_id="echo-123",
            person_id="person-456",
            faction_id="faction-789",
        )
        assert actor.echo_id == "echo-123"
        assert actor.person_id == "person-456"
        assert actor.faction_id == "faction-789"

    def test_actor_resources(self):
        actor = Actor(name="Test")
        assert actor.resources.food == 100.0
        assert actor.resources.infrastructure == 80.0

        actor.resources.food = 50.0
        assert actor.resources.food == 50.0

    def test_actor_action_history(self):
        actor = Actor(name="Test")
        actor.action_history.append("write_manifesto")
        actor.action_history.append("found_circle")
        assert len(actor.action_history) == 2


class TestIdea:
    """Tests for Idea entity."""

    def test_create_idea(self):
        idea = Idea(
            name="La Voluntad Colectiva",
            author_actor_id="actor-123",
            kind=IdeaKind.BELIEF,
        )
        assert idea.name == "La Voluntad Colectiva"
        assert idea.author_actor_id == "actor-123"
        assert idea.kind == IdeaKind.BELIEF
        assert idea.state == IdeaState.GERMINATING

    def test_idea_defaults(self):
        idea = Idea(name="Test Idea")
        assert idea.clarity == 50.0
        assert idea.virality == 50.0
        assert idea.stability == 50.0
        assert idea.mutation_risk == 50.0
        assert idea.spread == 0.0
        assert idea.followers == 0

    def test_idea_lifecycle_states(self):
        idea = Idea(name="Test")
        assert idea.state == IdeaState.GERMINATING

        idea.state = IdeaState.EXPANDING
        assert idea.state == IdeaState.EXPANDING

        idea.state = IdeaState.STABLE
        assert idea.state == IdeaState.STABLE

    def test_idea_genealogy(self):
        idea = Idea(name="Child Idea", parent_idea_ids=["parent-1", "parent-2"])
        assert len(idea.parent_idea_ids) == 2
        assert "parent-1" in idea.parent_idea_ids

    def test_idea_doctrine_link(self):
        idea = Idea(name="Test")
        assert idea.doctrine_id is None

        idea.doctrine_id = "doctrine-123"
        assert idea.doctrine_id == "doctrine-123"

    def test_idea_resonance(self):
        idea = Idea(name="Test")
        idea.resonance.dominant = [
            ResonanceScore(resonance_id="thelema", value=60),
            ResonanceScore(resonance_id="individualism", value=40),
        ]
        assert idea.resonance.get("thelema") == 60.0
        assert idea.resonance.dominant_resonances() == ["thelema", "individualism"]


class TestDoctrine:
    """Tests for Doctrine entity."""

    def test_create_doctrine(self):
        doctrine = Doctrine(
            name="Protocolos Autónomos",
            source_idea_id="idea-123",
        )
        assert doctrine.name == "Protocolos Autónomos"
        assert doctrine.source_idea_id == "idea-123"
        assert doctrine.institutionalization == 0.0
        assert doctrine.distortion == 0.0

    def test_doctrine_branches(self):
        doctrine = Doctrine(name="Test Doctrine")
        doctrine.branches = [
            DoctrineBranch(
                name="Rama Libertaria",
                emphasis="autonomía individual",
                core_resonance_id="anarchism",
                secondary_resonance_id="thelema",
            ),
            DoctrineBranch(
                name="Rama Algorítmica",
                emphasis="coordinación centralizada",
                core_resonance_id="technocracy",
                secondary_resonance_id="absurdism",
            ),
        ]
        assert len(doctrine.branches) == 2
        assert doctrine.branches[0].name == "Rama Libertaria"

    def test_doctrine_followers(self):
        doctrine = Doctrine(name="Test")
        assert doctrine.follower_count == 0
        doctrine.follower_count = 100
        assert doctrine.follower_count == 100

    def test_doctrine_stability(self):
        doctrine = Doctrine(name="Test")
        assert doctrine.stability == 50.0
        doctrine.stability = 75.0
        assert doctrine.stability == 75.0


class TestResonanceProfile:
    """Tests for ResonanceProfile value object."""

    def test_create_profile(self):
        profile = ResonanceProfile(
            dominant=[
                ResonanceScore(resonance_id="humanism", value=60),
                ResonanceScore(resonance_id="pragmatism", value=40),
            ]
        )
        assert profile.get("humanism") == 60.0
        assert profile.get("pragmatism") == 40.0
        assert profile.get("unknown") == 0.0

    def test_dominant_resonances(self):
        profile = ResonanceProfile(
            dominant=[
                ResonanceScore(resonance_id="thelema", value=60),
                ResonanceScore(resonance_id="anarchism", value=30),
                ResonanceScore(resonance_id="humanism", value=10),
            ]
        )
        result = profile.dominant_resonances(min_value=15.0)
        assert "thelema" in result
        assert "anarchism" in result
        assert "humanism" not in result

    def test_to_weights(self):
        profile = ResonanceProfile(
            dominant=[ResonanceScore(resonance_id="thelema", value=70)],
            underlying=[ResonanceScore(resonance_id="anarchism", value=30)],
        )
        weights = profile.to_weights()
        assert weights["thelema"] == 70
        assert weights["anarchism"] == 30


class TestResourcePool:
    """Tests for ResourcePool value object."""

    def test_create_pool(self):
        pool = ResourcePool()
        assert pool.food == 100.0
        assert pool.infrastructure == 80.0
        assert pool.energy == 60.0
        assert pool.knowledge == 40.0

    def test_total(self):
        pool = ResourcePool(food=50, infrastructure=30, energy=20, knowledge=10)
        assert pool.total() == 110.0

    def test_apply_delta(self):
        pool = ResourcePool(food=100, infrastructure=80, energy=60, knowledge=40)
        pool.apply_delta({"food": -20, "energy": 10})
        assert pool.food == 80.0
        assert pool.energy == 70.0

    def test_clamp(self):
        pool = ResourcePool(food=150, infrastructure=-10, energy=50, knowledge=200)
        pool.clamp()
        assert pool.food == 100.0
        assert pool.infrastructure == 0.0
        assert pool.knowledge == 100.0
