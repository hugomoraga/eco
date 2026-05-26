# ECO Development Guidelines

## Architecture Overview

```
eco/
├── core/           # Pure simulation (no AI, no UI, no filesystem)
├── adapters/       # AI, autoplayer, TUI
├── data/          # YAML configurations
├── specs/         # Design specifications
└── tests/         # Test suite
```

---

## Directory Structure

### `core/` - Pure Simulation Engine

**Principle:** Core knows nothing about AI, UI, or filesystem.

```
core/
├── domain/        # Entities: World, Echo, Person, Circle, Faction, Crisis, Goal
├── application/   # Use cases: actions (FoundCircle, WriteManifesto, Talk, etc.)
├── systems/       # Game logic: simulation, turn_processor, npc_processor, goal_tracker, crisis_engine
├── factories/     # Entity creation: echo_factory, person_factory, circle_factory, goal_factory
└── ports/         # Interfaces: observer, events
```

**Rules:**
- `core` has ZERO imports from `adapters`
- `core` does not know about Textual, OpenAI, MiniMax, or filesystem
- `core` only simulates and emits events through ports

### `adapters/` - External Adapters

```
adapters/
├── ai/            # AI adapters: OpenAI, MiniMax
├── autoplayer/   # NPC AI, autoplay engine
└── tui/          # Textual UI (consumes only ports)
```

**Rules:**
- Adapters implement ports defined in `core/ports/`
- Adapters depend on `core`, never the reverse

### `data/` - Configuration Data

```
data/
├── archetypes.yaml
├── essences.yaml
├── civs/
├── persons/
└── narratives/
```

**Rules:**
- All game configuration in YAML
- No business logic in data/

---

## File Placement Rules

| Type | Location | Example |
|------|----------|---------|
| Data entity | `domain/` | `domain/person.py`, `domain/goal.py` |
| Game logic | `systems/` | `systems/simulation.py` |
| Entity creation | `factories/` | `factories/person_factory.py` |
| UI/protocol interface | `ports/` | `ports/observer.py` |
| AI adapter | `adapters/ai/` | `adapters/ai/openai_adapter.py` |
| UI display | `adapters/tui/` | `adapters/tui/app.py` |
| Static config | `data/` | `data/archetypes.yaml` |

---

## File Size Rules

| Size | Action |
|------|--------|
| < 200 lines | Ideal |
| 200-300 lines | Acceptable |
| > 300 lines | **Must split** |

### Files to Split

- [x] `core/systems/simulation.py` → ✅ REFACTORED COMPLETE
  - `simulation_engine.py` (403 lines) - main orchestrator with run(), _generate_finale()
  - `world_builder.py` (94 lines) - world creation
  - `turn_context.py` (134 lines) - damage, reincarnation, metrics helpers
  - `simulation_api.py` (89 lines) - adapter-friendly API
  - `action_registry.py` (43 lines) - action class registry
  - `simulation.py` - backward compatibility alias
  - Previously: `npc_processor.py` (61), `circle_processor.py` (37), `goal_processor.py` (43)
- [x] `core/domain/entities.py` (695 lines) → ✅ SPLIT COMPLETE
  - `ideas.py`, `person.py`, `host.py`, `echo.py`, `circle.py`, `faction.py`, `civ.py`, `world.py`, `essence_registry.py`
  - `entities.py` kept as re-export for backward compatibility

---

## Naming Conventions

### Files
- `snake_case.py`
- One class per file when reasonable

### Classes
- `PascalCase`
- Suffix: `Factory` for creation, `Service` for business logic, `Port` for interfaces

### Functions
- `snake_case()`

---

## Import Rules

```python
# GOOD: Clean dependency direction
from core.domain import World
from core.factories import create_echo
from core.ports import SimulationObserver

# BAD: Cross-layer dependency
from adapters.ai import OpenAIAdapter  # ❌ in core code
```

**Dependency Rule:** Dependencies only point inward.
```
adapters ──implement──▶ ports ◀──define── core
    │                                   ▲
    └─────────imports────────────────────┘
    
(core NEVER imports adapters)
```

---

## Core Principles

### 1. Core is Pure
- No AI logic in `core/`
- No UI in `core/`
- No direct filesystem access in `core/`
- Simulation only, emits events via ports

### 2. Narrative Generator Location
- Deterministic text generation → `core/systems/narrative_system.py`
- If uses AI → `adapters/ai/narrative_adapter.py`

### 3. Autoplayer Location
- If pure simulation heuristics → `core/systems/autoplayer.py`
- If uses AI/heuristics → `adapters/autoplayer/`

### 4. Tests Mirror Structure
```
tests/
├── core/
│   ├── domain/
│   ├── systems/
│   ├── factories/
│   └── ports/
└── adapters/
    ├── ai/
    └── tui/
```

---

## Decision Tree for New Files

```
Is it a DATA ENTITY (pure model)?
├── YES → core/domain/

Is it GAME LOGIC (rules, processing)?
├── YES → core/systems/

Is it ENTITY CREATION?
├── YES → core/factories/

Is it a PORT/INTERFACE?
├── YES → core/ports/

Is it AI logic?
├── YES → adapters/ai/

Is it UI?
├── YES → adapters/tui/

Is it CONFIGURATION?
├── YES → data/

Is it a TEST?
├── YES → tests/<mirrored_structure>/
```

---

## Refactoring Triggers

| Symptom | Action |
|---------|--------|
| File > 300 lines | Split |
| File has 3+ responsibilities | Split |
| Cross-layer import | Move to correct layer |
| Duplicated logic | Extract to shared |
| `systems/` has > 15 files | Consider splitting into `application/` + `domain/rules/` |

---

## Hexagonal Architecture

```
┌─────────────────────────────────────────────────────┐
│                    adapters/                        │
│   ┌──────────┐  ┌───────────┐  ┌────────────┐    │
│   │   tui/   │  │    ai/    │  │ autoplayer │    │
│   └────┬─────┘  └─────┬─────┘  └──────┬─────┘    │
└────────┼──────────────┼───────────────┼───────────┘
         │              │               │
         ▼              ▼               ▼
┌─────────────────────────────────────────────────────┐
│                   ports/                            │
│   ┌──────────────┐  ┌────────────────────────┐      │
│   │  observer   │  │  event_sink (future)   │      │
│   └──────────────┘  └────────────────────────┘      │
└───────────────────────┬─────────────────────────────┘
                        │
         ┌──────────────┼──────────────┐
         ▼              ▼              ▼
┌─────────────────────────────────────────────────────┐
│                    core/                            │
│  ┌─────────────┐  ┌───────────┐  ┌───────────┐    │
│  │   domain/   │  │  systems/ │  │ factories/ │    │
│  └─────────────┘  └───────────┘  └───────────┘    │
│  ┌─────────────────────────────────────────────┐   │
│  │              application/                     │   │
│  │              └── actions/                      │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

---

## Adding New Features

1. **Check this document first**
2. **Identify the layer** using decision tree
3. **Check if file will exceed 300 lines** - split if needed
4. **Follow import rules** - no cross-layer dependencies
5. **Add test** in mirrored structure
6. **Run ruff format** before committing

---

## Current TODO

- [x] Rename `game_core` → `core`
- [x] Rename `factory` → `factories`
- [x] Rename `protocol` → `ports`
- [x] Move `adapter_core` + `ui_core` → `adapters/`
- [x] Refactor `simulation.py` → ✅ COMPLETE
  - ✅ simulation_engine.py (403 lines)
  - ✅ world_builder.py (94 lines)
  - ✅ turn_context.py (134 lines)
  - ✅ simulation_api.py (89 lines)
  - ✅ action_registry.py (43 lines)
  - ✅ npc_processor.py (61 lines)
  - ✅ circle_processor.py (37 lines)
  - ✅ goal_processor.py (43 lines)
- [x] Split `entities.py` (>300 lines) ✅ DONE
  - ✅ ideas.py, person.py, host.py, echo.py, circle.py
  - ✅ faction.py, civ.py, world.py, essence_registry.py
  - ✅ entities.py: Re-exports for backward compatibility
- [ ] Minor cleanup remaining:
  - [ ] `goals.py` → `domain/`
  - [ ] `crisis.py` → `domain/`
  - [ ] `archetype_registry.py` → `domain/`
  - [ ] `goal_factory.py` → `factories/`
  - [ ] `narrative_generator.py` → `core/systems/narrative_system.py`
