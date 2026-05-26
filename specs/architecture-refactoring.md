# ECO Architecture Refactoring Spec

## Status: IN PROGRESS

## Overview

Refactor ECO's codebase to follow hexagonal architecture with clean separation of concerns. This makes the codebase maintainable, testable, and ready for future features (goals, narrative, crisis system).

---

## Motivation

### Problems
- `game_core` knows about AI and UI (violates hexagonal architecture)
- Files are too large (`simulation.py` 746 lines, `entities.py` 695 lines)
- Duplicate code for archetypes across `goals.py`, `narrative_generator.py`, `narrative_actions.py`
- No clear rules for where new files should go
- Hard to test individual components

### Benefits
- Clear dependency direction: adapters → core → domain
- Core is reusable (can run headless, swap AI, swap UI)
- Small, focused files (< 300 lines)
- Easy to test in isolation
- Clear contracts via ports

---

## Target Architecture

```
eco/
├── core/              # Pure simulation (no AI, no UI, no filesystem)
│   ├── domain/       # Entities: World, Echo, Person, Circle, Faction, Crisis, Goal
│   ├── systems/      # Game logic: simulation, turn_processor, npc_processor, goal_tracker, crisis_engine
│   ├── factories/    # Entity creation: echo_factory, person_factory, circle_factory, goal_factory
│   └── ports/       # Interfaces: observer, events
│
├── adapters/         # External adapters (implement ports)
│   ├── ai/         # AI adapters: OpenAI, MiniMax
│   ├── autoplayer/ # NPC AI, autoplay engine
│   └── tui/        # Textual UI
│
├── data/            # YAML: archetypes, essences, civs, crisis_templates
├── specs/          # Design specs
└── tests/          # Tests (mirror core structure)
```

---

## Directory Changes

### 1. Rename `game_core` → `core`

### 2. Rename `factory` → `factories`

### 3. Rename `protocol` → `ports`

### 4. Consolidate `adapter_core` + `ui_core` → `adapters/`

```
adapter_core/ai/          → adapters/ai/
adapter_core/autoplayer/  → adapters/autoplayer/
ui_core/textual/          → adapters/tui/
```

### 5. Keep `data/` and `specs/` at root

---

## Module Reorganization

### Move files from `domain/`

| File | Destination | Reason |
|------|-------------|--------|
| `entities.py` (695l) | `domain/world.py`, `domain/person.py`, `domain/echo.py`, etc. | Split by entity type |
| `goals.py` | `domain/goal.py` | Already entity |
| `crisis.py` | `domain/crisis.py` | Already entity |
| `archetype_registry.py` | `domain/archetype_registry.py` | Registry of domain data |

### Move files from `factory/` → `factories/`

| File | Destination | Reason |
|------|-------------|--------|
| `goal_factory.py` | `factories/goal_factory.py` | Creation logic |
| `narrative_generator.py` | `core/systems/narrative_system.py` | Deterministic narrative logic (not entity creation) |

### Keep in `systems/`

- `simulation.py` (needs split)
- `turn_processor.py` (new - extracted from simulation.py)
- `npc_processor.py` (new - extracted from simulation.py)
- `goal_tracker.py` (new - goals evaluation)
- `crisis_engine.py` (new - crisis detection/application)

---

## Files to Split

### `simulation.py` (746 lines) → Split into:

```
systems/
├── simulation.py       # Main loop orchestration (~150 lines)
├── turn_processor.py  # Turn processing logic (~200 lines)
├── npc_processor.py   # NPC turn processing (~150 lines)
└── metrics_processor.py # World metrics evolution (~100 lines)
```

**Extract to separate files:**
- `_process_npc_turns()` → `npc_processor.py`
- `_process_circle_activities()` → (keep in simulation for now)
- `_handle_npc_damage_to_player()` → `damage_processor.py`
- `_handle_reincarnation()` → `reincarnation_processor.py`
- `_generate_finale()` → (keep in simulation)
- `_evaluate_goals()` → `goal_tracker.py`

### `entities.py` (695 lines) → Split into:

```
domain/
├── world.py           # World, WorldClock (~100 lines)
├── person.py          # Person, PlayerPerson, NPCPerson (~150 lines)
├── echo.py            # Echo, EchoAttribute (~100 lines)
├── circle.py          # Circle, CircleEvent (~80 lines)
├── faction.py         # Faction (~50 lines)
├── civ.py            # Civ (~50 lines)
├── essence.py         # EssenceScore, EssenceProfile, EssenceRegistry (~80 lines)
├── ideas.py          # Ideas, Tags (~30 lines)
├── manifesto.py       # Manifesto (~20 lines)
└── events.py         # Domain events (~30 lines)
```

---

## Import Refactoring

### Before (violates rules)
```python
# In game_core/systems/simulation.py
from adapter_core.autoplayer import NPCActionExecutor  # ❌ Core knows about adapters
from game_core.ai import MiniMaxAdapter  # ❌ Core knows about AI
```

### After (clean)
```python
# In core/systems/simulation.py
from core.ports import SimulationObserver  # ✓ Via port
# AI adapters are instantiated OUTSIDE core and passed in
```

### New Import Pattern

```python
# adapters/tui/app.py - Creates AI adapter and passes to core
from core.systems.simulation import SimulationEngine
from adapters.ai.openai_adapter import OpenAIAdapter

ai_adapter = OpenAIAdapter()
engine = SimulationEngine(ai_adapter=ai_adapter)  # Injected
```

---

## Protocol/Events Changes

### Rename `protocol/` → `ports/`

```
protocol/observer.py  → ports/observer.py
protocol/events.py    → ports/events.py
protocol/__init__.py  → ports/__init__.py
```

### Keep MessageType in `ports/messages.py`

---

## Adapters Structure

### `adapters/ai/`
```
adapters/ai/
├── __init__.py
├── base.py          # AIAdapter interface
├── openai_adapter.py
└── minimax_adapter.py
```

### `adapters/autoplayer/`
```
adapters/autoplayer/
├── __init__.py
├── engine.py
├── npc_engine.py
└── styles.py
```

### `adapters/tui/`
```
adapters/tui/
├── __init__.py
├── app.py
├── widgets/
├── theme.py
└── styles.py
```

---

## New Files to Create

### 1. `core/systems/turn_processor.py`
Responsibility: Process a single turn's logic

### 2. `core/systems/npc_processor.py`
Responsibility: Process NPC turns

### 3. `core/systems/goal_tracker.py`
Responsibility: Evaluate goals each turn

### 4. `core/systems/crisis_engine.py`
Responsibility: Detect and apply crisis effects

---

## Data Files

### Consolidate Archetypes

Current problem: Archetype data scattered across:
- `data/archetypes.yaml` (new - single source)
- `goals.py` (ARCHETYPE_GOAL_WEIGHTS)
- `narrative_actions.py` (ARCHETYPE_ACTION_PREFERENCES)
- `narrative_generator.py` (NARRATIVE_INTROS)

**Solution:** `data/archetypes.yaml` is the source of truth. All code reads from it via `ArchetypeRegistry`.

---

## Tests Structure

```
tests/
├── core/
│   ├── domain/
│   │   ├── test_goal.py
│   │   └── test_crisis.py
│   ├── systems/
│   │   └── test_simulation.py
│   ├── factories/
│   │   └── test_goal_factory.py
│   └── ports/
│       └── test_observer.py
└── adapters/
    ├── ai/
    └── tui/
```

---

## Migration Steps

### Phase 1: Directory Rename
1. Rename `game_core` → `core`
2. Rename `factory` → `factories`
3. Rename `protocol` → `ports`
4. Move `adapter_core` and `ui_core` → `adapters/`

### Phase 2: Import Fixes
1. Update all imports to new paths
2. Fix cross-layer imports
3. Run tests to verify

### Phase 3: File Splits
1. Split `entities.py` → individual domain files
2. Split `simulation.py` → processor modules
3. Run tests to verify

### Phase 4: Cleanup
1. Delete empty directories
2. Update `__init__.py` exports
3. Final test run

---

## Verification

After each phase, run:
```bash
# Tests pass
pytest tests/ -x -q

# Ruff clean
ruff check core/ adapters/

# No circular imports
python -c "import core; import adapters"
```

---

## Open Questions

1. [x] Structure confirmed
2. [ ] `narrative_generator` - keep in `factories/` or move to `adapters/`?
   - Decision: Keep deterministic version in `factories/`. AI version in `adapters/ai/`.
3. [ ] `autoplayer` - pure simulation or adapter?
   - Decision: `adapters/autoplayer/` - uses heuristics that may be game-specific
4. [ ] Split `systems/` later when > 15 files?
   - Decision: Split when needed, not preemptively

---

## Success Criteria

- [ ] `core/` has ZERO imports from `adapters/`
- [ ] All files < 300 lines
- [ ] Tests pass
- [ ] No circular dependencies
- [ ] Clear dependency flow: adapters implement ports, core defines ports, core never imports adapters
