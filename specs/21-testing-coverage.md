# 21 - Testing Coverage for Core Systems

## Metadata

- Status: draft
- Created: 2026-05-24
- Depends on: 01-12 (core systems)

## Context

Currently we have integration tests for 4 systems:
- DerivePressureCalculator
- EssenceEffects
- EventGenerator
- NPCGenerator

But we have 10 core systems and only 4 are covered by tests.

## Systems Without Tests

| # | System | Files | Priority |
|---|---------|-------|----------|
| 1 | Domain Entities | entities.py, city.py, npc.py | high |
| 2 | Simulation Engine | simulation.py | high |
| 3 | Actions | echo_actions.py (6 actions) | high |
| 4 | EssenceRegistry | essence_registry.py | medium |
| 5 | AI Adapters | mock_adapter.py, openai_adapter.py | medium |
| 6 | Temporal/WorldClock | world_clock.py | low |

## Scope

### High Priority (MVP 1 completion)

**1. Domain Entities** (`game_core/domain/entities.py`)
```
Test: test_echo_creation
Test: test_circle_creation
Test: test_faction_creation
Test: test_world_state
Test: test_essence_registry_integration
```

**2. Simulation Engine** (`game_core/engine/simulation.py`)
```
Test: test_simulation_run
Test: test_seed_reproducibility
Test: test_autoplay_flag
Test: test_jsonl_logging
```

**3. Actions** (`game_core/actions/echo_actions.py`)
```
Test: test_found_circle_action
Test: test_propagate_idea_action
Test: test_talk_action
Test: test_write_manifesto_action
Test: test_sabotage_action
Test: test_ritualize_action
```

### Medium Priority

**4. EssenceRegistry** (`game_core/domain/essence_registry.py`)
```
Test: test_get_affinity
Test: test_get_modifier
Test: test_essence_list
```

**5. AI Adapters** (`game_core/ai/`)
```
Test: test_mock_adapter_response
Test: test_openai_adapter_response
```

### Low Priority

**6. WorldClock** (`game_core/domain/world_clock.py`)
```
Test: test_advance
Test: test_world_tick_increment
```

## Notes

- Tests should be in `scripts/test_integration.py` or `tests/` folder
- Use pytest framework
- Each test should print PASS/FAIL clearly
- Run all tests with: `uv run pytest tests/ -v`

## Status History

- 2026-05-24: draft created