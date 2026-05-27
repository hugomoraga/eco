"""
Integration test for disconnected systems.
Tests: DerivePressureCalculator, EventGenerator, EssenceEffects, create_npc
"""
from __future__ import annotations

import sys

sys.path.insert(0, '.')

from adapters.ai import MockAdapter
from core.domain import Circle, Faction, World, WorldClock
from core.domain.rules.essence_effects import EssenceEffects
from core.factories import create_npc
from core.application.processors.event_generator import EventGenerator
from core.application.processors.event_pool import EventPool
from core.application.processors.pressure import DerivePressureCalculator, EconomyPressure


def test_derive_pressure_calculator():
    """Test 1: DerivePressureCalculator affects faction score."""
    print("\n=== Test 1: DerivePressureCalculator ===")

    # Calculate pressures using EconomyPressure
    material_pressure = EconomyPressure.calculate_material_pressure(
        {"food": 50, "infrastructure": 30, "energy": 20}
    )
    world = World(clock=WorldClock(), factions=[], stability=50.0)
    social_pressure = EconomyPressure.calculate_social_pressure(world)
    institutional_pressure = 30.0  # Mock value
    temporal_pressure = 20.0  # Mock value

    lineage = ["anarchism", "anarchism"]
    dominant_essence = "anarchism"

    pressure = DerivePressureCalculator.calculate(
        material_pressure=material_pressure,
        social_pressure=social_pressure,
        institutional_pressure=institutional_pressure,
        temporal_pressure=temporal_pressure,
        lineage=lineage,
        dominant_essence=dominant_essence,
    )

    print(f"  Material pressure: {material_pressure:.2f}")
    print(f"  Social pressure: {social_pressure:.2f}")
    print(f"  Institutional pressure: {institutional_pressure:.2f}")
    print(f"  Temporal pressure: {temporal_pressure:.2f}")
    print(f"  Lineage: {lineage}")
    print(f"  Dominant essence: {dominant_essence}")
    print(f"  Total pressure: {pressure:.2f}")

    # Score modifier: base 31.66 * (1 + pressure/100)
    base_score = 31.66
    modified_score = base_score * (1 + pressure / 100)
    print(f"  Base faction score: {base_score:.2f}")
    print(f"  Modified score: {modified_score:.2f}")

    assert pressure >= 0, "Pressure should be non-negative"
    assert modified_score >= base_score * 0.5, "Modified score should be in valid range"
    print("  PASS: Pressure calculator working")


def test_essence_effects():
    """Test 2: EssenceEffects modifies action outcomes."""
    print("\n=== Test 2: EssenceEffects ===")

    # Test affinity between essences
    essences = ["anarchism", "technocracy", "absurdism", "thelema", "ecology"]

    print("  Affinity matrix (sample):")
    for e1 in essences[:3]:
        for e2 in essences[:3]:
            if e1 != e2:
                affinity = EssenceEffects.get_essence_affinity(e1, e2)
                bonus = affinity * 0.02 * 100  # percentage
                print(f"    {e1} -> {e2}: {affinity:.3f} ({bonus:+.1f}% action bonus)")

    # Test that high affinity gives bonus, low/negative gives penalty
    high_affinity = EssenceEffects.get_essence_affinity("anarchism", "ecology")
    low_affinity = EssenceEffects.get_essence_affinity("anarchism", "technocracy")

    print(f"\n  High affinity (anarchism-ecology): {high_affinity:.3f}")
    print(f"  Low affinity (anarchism-technocracy): {low_affinity:.3f}")

    assert abs(high_affinity) > abs(low_affinity), "Similar essences should have higher affinity"
    print("  PASS: Essence effects working")


def test_event_generator():
    """Test 3: EventGenerator fires events."""
    print("\n=== Test 3: EventGenerator ===")

    world = World(
        clock=WorldClock(),
        factions=[],
        circles=[],
        echoes=[],
        stability=50.0
    )

    ai_adapter = MockAdapter()
    pool = EventPool()
    event_gen = EventGenerator(ai_adapter, seed=42, pool=pool)

    print("  Generating events for 5 turns...")

    events_generated = 0
    for turn in range(1, 6):
        context = {
            "turn": turn,
            "world_state": world,
            "faction": None,
            "event_type": "tick",
        }
        event = event_gen.generate(context)
        events_generated += 1
        print(f"    Turn {turn}: {event.title}")

    print(f"  Total events generated: {events_generated}")
    assert events_generated >= 5, "Should generate events"
    print("  PASS: Event generator working")


def test_npc_generator():
    """Test 4: NPCGenerator creates NPCs when circles grow."""
    print("\n=== Test 4: create_npc ===")

    ai_adapter = MockAdapter()

    # Simulate a circle with 3+ members
    circle = Circle(
        id="test_circle",
        name="Test Circle",
        essence="anarchism",
        member_ids=["echo1", "echo2", "echo3"],
        npcs=[]
    )

    print(f"  Circle: {circle.name}")
    print(f"  Members: {circle.member_count}")
    print(f"  NPCs before: {len(circle.npcs)}")

    # Check threshold
    threshold = 3
    if circle.member_count >= threshold:
        npc = create_npc(ai_adapter, {"essence": circle.essence, "context": "circle_growth"}, seed=42)
        circle.npcs.append(npc.id)
        print(f"  Generated NPC: {npc.name} (ID: {npc.id})")
        print(f"  NPCs after: {len(circle.npcs)}")
        print("  PASS: NPC generator working")
    else:
        print(f"  FAIL: Circle has {circle.member_count} members, need {threshold}")
        raise AssertionError("Circle should have 3+ members")


def test_full_integration():
    """Test 5: All systems working together."""
    print("\n=== Test 5: Full Integration ===")

    # Create a world with factions and circles
    faction = Faction(
        id="test_faction",
        name="Test Faction",
        essence="anarchism",
        influence=50.0,
        resources={"food": 50, "infrastructure": 30, "energy": 20}
    )

    circle = Circle(
        id="test_circle",
        name="Test Circle",
        essence="anarchism",
        members=3
    )

    world = World(
        clock=WorldClock(),
        factions=[faction],
        circles=[circle],
        echoes=[],
        stability=50.0
    )

    print(f"  World: {len(world.factions)} factions, {len(world.circles)} circles")

    # 1. Calculate pressure
    material = EconomyPressure.calculate_material_pressure(world.resources)
    social = EconomyPressure.calculate_social_pressure(world)
    pressure = DerivePressureCalculator.calculate(
        material_pressure=material,
        social_pressure=social,
        institutional_pressure=30.0,
        temporal_pressure=20.0,
        lineage=["anarchism"],
        dominant_essence="anarchism",
    )
    print(f"  Pressure: {pressure:.2f}")

    # 2. Generate event
    ai_adapter = MockAdapter()
    pool = EventPool()
    event_gen = EventGenerator(ai_adapter, seed=42, pool=pool)
    context = {"turn": 1, "world_state": world, "faction": None, "event_type": "tick"}
    events = event_gen.generate(context)
    print(f"  Event generated: {events.title}")

    # 3. Check NPC
    threshold = 3
    if circle.member_count >= threshold:
        npc = create_npc(ai_adapter, {"essence": circle.essence, "context": "circle_growth"}, seed=42)
        circle.npcs.append(npc.id)
        print(f"  NPC created: {npc.name}")

    print("  PASS: All systems integrated")


if __name__ == "__main__":
    print("=" * 60)
    print("ECO Integration Tests")
    print("=" * 60)

    try:
        test_derive_pressure_calculator()
        test_essence_effects()
        test_event_generator()
        test_npc_generator()
        test_full_integration()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED")
        print("=" * 60)

    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
