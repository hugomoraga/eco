# 19. MVP Implementation Tracking

## 19.1 Registro de Hitos

| Milestone | Commit | Specs Involucradas | Audit | Fecha |
|-----------|--------|---------------------|-------|-------|
| MVP 0 | fa50cc2 | 01, 02, 03, 07, 08 | 8/8 | 2026-05-24 |
| MVP 1 (parcial) | 2b777c8 | 05, 10 | 8/8 | 2026-05-24 |

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
| 04 | Essences | in_progress | v0.1.0 | genealogical_lineage pending |
| 05 | Ideas y Doctrinas | implemented | v0.2.0 | TagGenerator implemented |
| 06 | Ideological Drift | in_progress | v0.1.0 | Formulas pending |
| 07 | Actions | implemented | v0.2.0 | MVP 0 - 2 functional + 3 stubs |
| 08 | Temporal System | implemented | v0.2.0 | MVP 0 - 3 temporal layers |
| 09 | Economy | in_progress | v0.1.0 | derive_pressure pending |
| 10 | Factions | implemented | v0.2.0 | FactionTickSystem basic |
| 11 | Autoplayer | in_progress | v0.1.0 | Random autoplay only |
| 12 | AI Integration | in_progress | v0.1.0 | Adapters pending |
| 13 | Events | draft | v0.1.0 | Generator pending |
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

### Pending (for MVP 2)
- MockAdapter / OpenAIAdapter
- Event generator
- Configurable goals in autoplayer

## 19.6 MVP 1 - Detail (partial)

**Date:** 2026-05-24
**Commit:** 2b777c8
**Audit:** 8/8 passing

### Implemented Files
```
game_core/
├── domain/
│   └── tag_generator.py   # TagGenerator with templates for 5 essences
└── engine/
    └── faction_tick.py    # FactionTickSystem with heuristic scoring
```

### Functional
- TagGenerator: templates for anarchism, technocracy, absurdism, thelema, ecology
- PropagateIdea: functional with multiple targets (factions + circles)
- FactionTickSystem: actions (recruit_npc, spread_doctrine, support_infrastructure, radicalize_members)
- Faction ticks every 3 turns in simulation

### Pending (for complete MVP 1)
- MockAdapter / OpenAIAdapter optional
- NPC generator
- Event generator
- Essence effects on genealogical_lineage (spec-04)
- Derive_pressure integration (spec-09)

## 19.7 Next Milestones

### Complete MVP 1
- MockAdapter / OpenAIAdapter optional
- NPC generator
- Event generator
- Essence effects on genealogical_lineage
- Derive_pressure integration

### MVP 2 - Advanced Autoplayer
- Configurable goals
- Scoring heuristics
- Suggest / autoplay / take control modes

### MVP 3 - Godot read-only
- Load world_state.json
- Render city and NPCs

---

## Metadata

- Version: 0.1.0
- Created: 2026-05-24
- Depends on: 00-index.md
- Tracking: Este spec se actualiza con cada milestone completado