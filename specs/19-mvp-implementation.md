# 19. MVP Implementation Tracking

## 19.1 Milestone Registry

| Milestone | Commit | Specs | Audit | Date |
|-----------|--------|-------|-------|------|
| MVP 0 | fa50cc2 | 01, 02, 03, 07, 08 | 8/8 | 2026-05-24 |
| MVP 1 | e799f15 | 04, 05, 06, 09, 10, 12 | 8/8 | 2026-05-24 |

## 19.2 Spec Status Definitions

| Status | Meaning |
|--------|---------|
| `draft` | Initial draft, needs review |
| `in_progress` | Being actively developed |
| `implemented` | Fully implemented and passing audit |
| `deprecated` | Badly written or replaced by another spec |
| `stable` | Design approved, frozen |

## 19.3 Specs → Implementation

| Spec | Name | State | Version | Notes |
|------|------|-------|---------|-------|
| 01 | Architecture | implemented | v0.2.0 | MVP 0 complete |
| 02 | Domain | implemented | v0.2.0 | MVP 0 complete |
| 03 | Player Echo | implemented | v0.2.0 | MVP 0 complete |
| 04 | Essences | implemented | v0.2.0 | EssenceRegistry + EssenceEffects |
| 05 | Ideas y Doctrinas | implemented | v0.2.0 | TagGenerator implemented |
| 06 | Ideological Drift | implemented | v0.2.0 | DerivePressureCalculator |
| 07 | Actions | implemented | v0.2.0 | MVP 0 - 2 functional + 3 stubs |
| 08 | Temporal System | implemented | v0.2.0 | MVP 0 - 3 temporal layers |
| 09 | Economy | implemented | v0.2.0 | Derive_pressure integration |
| 10 | Factions | implemented | v0.2.0 | FactionTickSystem |
| 11 | Autoplayer | in_progress | v0.1.0 | Random autoplay only |
| 12 | AI Integration | implemented | v0.2.0 | MockAdapter + OpenAIAdapter |
| 13 | Events | in_progress | v0.1.0 | EventGenerator implemented |
| 14 | Godot Contract | in_progress | v0.1.0 | Snapshot format defined |
| 15 | Debugging | draft | v0.1.0 | Tools pending |
| 16 | MVP | stable | v0.1.0 | Phases design |
| 17 | Risks | in_progress | v0.1.0 | Needs update |
| 18 | Game Definition | draft | v0.1.0 | Implementation pending |

## 19.4 Historical Commits

| Commit | Description | MVP |
|--------|-------------|-----|
| 7890123 | feat: initial ECO MVP 0 implementation | MVP 0 |
| 6129a1a | chore: remove test runs directory | MVP 0 |
| fa50cc2 | fix: complete MVP 0 audit requirements | MVP 0 |
| d4dfc8a | feat(specs): add spec-19 implementation tracking | - |
| 2b777c8 | feat(mvp1): tag generator, propagate_idea, faction tick system | MVP 1 |
| 921972a | feat(ai): add MockAdapter and OpenAIAdapter | MVP 1 |
| 53f16ac | feat(mvp1): add NPCGenerator and update NPC model | MVP 1 |
| 6a09da4 | feat(mvp1): add EventGenerator with EffectTagValidator | MVP 1 |
| 408ed3a | feat(essences): add EssenceEffects and affinity matrix | MVP 1 |
| e799f15 | feat(economy): add DerivePressureCalculator and EconomyPressure | MVP 1 |

## 19.5 MVP 0 - Detail

**Date:** 2026-05-24
**Commit:** fa50cc2
**Audit:** 8/8 passing

### Implemented Files
```
game_core/
├── domain/
│   ├── entities.py      # Echo, Circle, Faction, World, WorldClock
│   ├── city.py          # District, City
│   └── npc.py           # NPC
├── engine/
│   ├── simulation.py    # SimulationEngine
│   └── random.py        # SeededRandom + deterministic methods
├── actions/
│   ├── base.py          # Action, ActionContext, ActionResult
│   └── echo_actions.py  # FoundCircle, PropagateIdea, Talk, WriteManifesto, Sabotage, Ritualize
├── data/
│   ├── essences.yaml    # 5 essences
│   └── actions.yaml    # 6 actions
└── run.py               # CLI entry point
```

### Functional
- FoundCircle: Creates circle with echo's ideology_tags
- PropagateIdea: stub (needs echo tags to propagate)
- 3 action stubs: Talk, WriteManifesto, Sabotage, Ritualize
- JSONL logging with state deltas
- Snapshots every 10 turns
- Reproducibility with seed

## 19.6 MVP 1 - Detail

**Date:** 2026-05-24
**Commit:** e799f15
**Audit:** 8/8 passing

### Implemented Files
```
game_core/
├── ai/
│   ├── __init__.py
│   ├── base.py              # AIAdapter ABC, AIResponse, MockAdapter
│   └── adapters/
│       ├── __init__.py
│       └── openai_adapter.py  # OpenAIAdapter (GPT-4)
├── domain/
│   ├── essence_effects.py   # EssenceEffects class
│   ├── npc_generator.py     # NPCGenerator
│   └── npc.py               # Extended with role, archetype, essence
├── engine/
│   ├── event_generator.py   # EventGenerator, GameEvent, EffectTagValidator
│   ├── faction_tick.py      # FactionTickSystem
│   └── pressure.py          # DerivePressureCalculator, EconomyPressure
└── data/
    └── essences.yaml        # Extended with affinities matrix
```

### Functional
- **AI Adapters:** MockAdapter (sequential/loop), OpenAIAdapter (GPT-4)
- **NPC Generator:** AI-powered or fallback procedural generation
- **Event Generator:** AI-powered with EffectTagValidator (canonical/emergent)
- **Essence Effects:** apply_to_echo, calculate_drift_risk, check_crystallization
- **Affinity Matrix:** All 5 essences have bidirectional affinities
- **Derive Pressure:** Weighted sum formula with compatibility modifier, mutation risk bonus
- **Economy Pressure:** Material and social pressure calculation

### Pending (for MVP 2)
- Configurable goals in autoplayer
- Advanced scoring heuristics
- Suggest / autoplay / take control modes
- Event generator integration with simulation loop
- Faction tick integration with DerivePressure

## 19.7 Next Milestones

### MVP 2 - Advanced Autoplayer
- Configurable goals
- Scoring heuristics
- Suggest / autoplay / take control modes

### MVP 3 - Godot read-only
- Load world_state.json
- Render city and NPCs

---

## Metadata

- Version: 0.2.0
- Created: 2026-05-24
- Updated: 2026-05-24
- Depends on: 00-index.md
- Tracking: Updated after MVP 1 completion