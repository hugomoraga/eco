# 19. MVP Implementation Tracking

## 19.1 Registro de Hitos

| Milestone | Commit | Specs Involucradas | Audit | Fecha |
|-----------|--------|---------------------|-------|-------|
| MVP 0 | fa50cc2 | 01, 02, 03, 07, 08 | 8/8 | 2026-05-24 |
| MVP 1 (parcial) | 2b777c8 | 05, 10 | 8/8 | 2026-05-24 |

## 19.2 Specs → Implementación

| Spec | Nombre | Estado | Version | Notas |
|------|--------|--------|---------|-------|
| 01 | Architecture | deprecated | v0.2.0 | MVP 0 complete - audit passing |
| 02 | Domain | deprecated | v0.2.0 | MVP 0 complete - audit passing |
| 03 | Player Echo | deprecated | v0.2.0 | MVP 0 complete - audit passing |
| 04 | Essences | in_progress | v0.1.0 | Datos en essences.yaml, sin validacion de genealogical_lineage |
| 05 | Ideas y Doctrinas | deprecated | v0.2.0 | TagGenerator implementado |
| 06 | Ideological Drift | in_progress | v0.1.0 | Sin implementacion de formulas |
| 07 | Actions | deprecated | v0.2.0 | MVP 0 complete - 5 actions (2 functional + 3 stubs) |
| 08 | Temporal System | deprecated | v0.2.0 | MVP 0 complete - 3 capas temporales |
| 09 | Economy | in_progress | v0.1.0 | Sin derive_pressure |
| 10 | Factions | deprecated | v0.2.0 | FactionTickSystem basico implementado |
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
| d4dfc8a | feat(specs): add spec-19 implementation tracking | - |
| 2b777c8 | feat(mvp1): tag generator, propagate_idea, faction tick system | MVP 1 |

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

### Pendiente (para MVP 2)
- MockAdapter / OpenAIAdapter
- Generador de eventos
- Goals configurables en autoplayer

## 19.5 MVP 1 - Detalle (parcial)

**Fecha:** 2026-05-24
**Commit:** 2b777c8
**Audit:** 8/8 passing

### Archivos Implementados
```
game_core/
├── domain/
│   └── tag_generator.py   # TagGenerator con templates para 5 esencias
└── engine/
    └── faction_tick.py    # FactionTickSystem con scoring heuristico
```

### Funcional
- TagGenerator: templates para anarchism, technocracy, absurdism, thelema, ecology
- PropagateIdea: funcional con multiples targets (factions + circles)
- FactionTickSystem: actions (recruit_npc, spread_doctrine, support_infrastructure, radicalize_members)
- Faction ticks cada 3 turns en simulacion

### Pendiente (para MVP 1 completo)
- MockAdapter / OpenAIAdapter opcional
- Generador de NPCs
- Generador de eventos
- Efectos de Essence en genealogical_lineage (spec-04)
- Derive_pressure integration (spec-09)

## 19.6 Proximos Hitos

### MVP 1 completo
- MockAdapter / OpenAIAdapter opcional
- Generador de NPCs
- Generador de eventos
- Efectos de Essence en genealogical_lineage
- Derive_pressure integration

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