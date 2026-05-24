# 19. MVP Implementation Tracking

## 19.1 Registro de Hitos

| Milestone | Commit | Specs Involucradas | Audit | Fecha |
|-----------|--------|---------------------|-------|-------|
| MVP 0 | fa50cc2 | 01, 02, 03, 07, 08 | 8/8 | 2026-05-24 |

## 19.2 Specs → Implementación

| Spec | Nombre | Estado | Version | Notas |
|------|--------|--------|---------|-------|
| 01 | Architecture | deprecated | v0.2.0 | MVP 0 complete - audit passing |
| 02 | Domain | deprecated | v0.2.0 | MVP 0 complete - audit passing |
| 03 | Player Echo | deprecated | v0.2.0 | MVP 0 complete - audit passing |
| 04 | Essences | in_progress | v0.1.0 | Datos en essences.yaml, sin validacion de genealogical_lineage |
| 05 | Ideas y Doctrinas | in_progress | v0.1.0 | Sin generador de tags |
| 06 | Ideological Drift | in_progress | v0.1.0 | Sin implementacion de formulas |
| 07 | Actions | deprecated | v0.2.0 | MVP 0 complete - 5 actions (2 functional + 3 stubs) |
| 08 | Temporal System | deprecated | v0.2.0 | MVP 0 complete - 3 capas temporales |
| 09 | Economy | in_progress | v0.1.0 | Sin derive_pressure |
| 10 | Factions | in_progress | v0.1.0 | Sin Faction Tick System |
| 11 | Autoplayer | in_progress | v0.1.0 | Solo autoplay flag basico (random) |
| 12 | AI Integration | in_progress | v0.1.0 | Sin adapters |
| 13 | Events | draft | v0.1.0 | Sin generador de eventos |
| 14 | Godot Contract | in_progress | v0.1.0 | Snapshot format definido |
| 15 | Debugging | draft | v0.1.0 | Sin tools de debugging |
| 16 | MVP | stable | v0.1.0 | Diseño de fases MVP |
| 17 | Risks | in_progress | v0.1.0 | Sin actualizacion post-implementacion |
| 18 | Game Definition | draft | v0.1.0 | Sin implementacion |

## 19.3 Commits Historicos

| Commit | Descripcion | MVP |
|--------|-------------|-----|
| 7890123 | feat: initial ECO MVP 0 implementation | MVP 0 |
| 6129a1a | chore: remove test runs directory | MVP 0 |
| fa50cc2 | fix: complete MVP 0 audit requirements | MVP 0 |

## 19.4 MVP 0 - Detalle

**Fecha:** 2026-05-24
**Commit:** fa50cc2
**Audit:** 8/8 passing

### Archivos Implementados
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
│   ├── essences.yaml    # 5 essencias
│   └── actions.yaml    # 6 acciones
└── run.py               # CLI entry point
```

### Funcional
- FoundCircle: Crea circulo con ideology_tags del echo
- PropagateIdea: stub (necesita tags en echo para propagar)
- 3 actions stubs: Talk, WriteManifesto, Sabotage, Ritualize
- JSONL logging con state deltas
- Snapshots cada 10 turns
- Reproducibilidad con seed

### Pendiente (para MVP 1)
- Generador de tags para Echo (spec-05)
- Faction Tick System (spec-10)
- Efectos de Essence en genealogical_lineage (spec-04)
- Derive_pressure integration (spec-09)

## 19.5 Proximos Hitos

### MVP 1 - IA controlada
- MockAdapter / OpenAIAdapter opcional
- Generador de NPCs
- Generador de eventos
- propagate_idea funcional con tags reales

### MVP 2 - Autoplayer avanzado
- Goals configurables
- Heuristicas de scoring
- Modo suggest / autoplay / take control

### MVP 3 - Godot read-only
- Carga world_state.json
- Renderiza ciudad y NPCs

---

## Metadata

- Version: 0.1.0
- Created: 2026-05-24
- Depends on: 00-index.md
- Tracking: Este spec se actualiza con cada milestone completado