# SPEC Index

Guía de lectura y dependencias entre especificaciones.

## Tabla de specs

| # | Spec | Descripción | Dependencias |
|---|------|-------------|--------------|
| 00 | [index](00-index.md) | Este índice | - |
| 01 | [architecture](01-architecture.md) | Stack, estructura carpetas, principios | - |
| 02 | [domain](02-domain.md) | Modelo de entidades World, Civilizations | 01 |
| 03 | [player-echo](03-player-echo.md) | Atributos, encarnación, reencarnación | 01, 02 |
| 04 | [essences](04-essences.md) | Esencias, matriz de afinidades | 01 |
| 05 | [ideas-doctrines](05-ideas-doctrines.md) | Ideas, doctrinas, genealogía memética | 04 |
| 06 | [ideological-drift](06-ideological-drift.md) | Sistema de deriva (4 capas) | 04, 05 |
| 07 | [actions](07-actions.md) | Acciones humanas, efectos, duración | 01, 02 |
| 08 | [temporal-system](08-temporal-system.md) | ActionTick, WorldTick, HistoricalTick | 01, 07 |
| 09 | [economy](09-economy.md) | Economía estructural, coste social | 01, 02 |
| 10 | [factions](10-factions.md) | Faction Tick System, agency limitada | 01, 02, 04 |
| 11 | [autoplayer](11-autoplayer.md) | Goals, evaluación multiobjetivo, personalidad | 01, 03, 06, 07 |
| 12 | [ai-integration](12-ai-integration.md) | Roles IA, validación 3 capas | 01, 06 |
| 13 | [events](13-events.md) | Plantillas sistémicas, emergencia | 01, 02, 09, 12 |
| 14 | [godot-contract](14-godot-contract.md) | Snapshots genéricos, VisualRegistry | 01, 02, 03, 08 |
| 15 | [debugging](15-debugging.md) | Logs JSONL, inspector, replay | 01 |
| 16 | [mvp](16-mvp.md) | MVP propsetos, criterios de éxito | 01, todos |
| 17 | [risks](17-risks.md) | Riesgos, mitigaciones | 01, todos |
| 18 | [game-definition](18-game-definition.md) | Definición corta, visión | - |

## Gráfico de dependencias

```
         ┌─────────────────────────────────────────────────────────┐
         │                          01                             │
         │                    [architecture]                        │
         └────────────────┬────────────────────────┬──────────────┘
                          │                        │
            ┌─────────────┼──────────┐            ┌┼──────────────┐
            ▼            ▼          ▼            ▼              ▼
         ┌────┐       ┌────┐     ┌────┐       ┌────┐          ┌────┐
         │ 02 │       │ 04 │     │ 07 │       │ 09 │          │ 15 │
         │    │       │    │     │    │       │    │          │    │
         └────┘       └────┘     └────┘       └────┘          └────┘
            │            │          │            │
            │            │          │            │
            ▼            ▼          │            │
         ┌────┐       ┌────┐        │            │
         │ 03 │       │ 05 │        │            │
         │    │       │    │        │            │
         └────┘       └────┘        │            │
            │            │          │            │
            │            ▼          ▼            ▼
            │         ┌────┐     ┌────┐       ┌────┐
            │         │ 06 │     │ 08 │       │ 10 │
            │         │    │     │    │       │    │
            │         └────┘     └────┘       └────┘
            │            │
            ▼            ▼
         ┌────┐       ┌────┐
         │ 11 │       │ 12 │
         │    │       │    │
         └────┘       └────┘
            │
            ▼
         ┌────┐       ┌────┐       ┌────┐
         │ 13 │       │ 14 │       │ 16 │
         │    │       │    │       │    │
         └────┘       └────┘       └────┘
```

## Guía de uso

### Para desarrollo incremental

1. Empezar con `01-architecture.md` y `02-domain.md`
2. Continuar con `03-player-echo.md` y `04-essences.md`
3. Trabajar `05-ideas-doctrines.md` antes de `06-ideological-drift.md`
4. `08-temporal-system.md` requiere `07-actions.md` completo
5. `10-factions.md` requiere conocer esencias antes

### Para revisión de spec individual

Cada spec es autocontenido:
- Tiene su propia numeración local (ej: `# 7.3` dentro de spec-06)
- Incluye notas de versión original del spec.md
- Las referencias a otras specs usan links relativos

### Para entender el sistema completo

Seguir el orden topológico: 01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09 → 10 → 11 → 12 → 13 → 14 → 15 → 16 → 17 → 18

## Estado de specs

| # | Spec | Status | Última revisión |
|---|------|--------|-----------------|
| 00 | [index](00-index.md) | ✅ | 2026-05-24 |
| 01 | [architecture](01-architecture.md) | ✅ Corregido | 2026-05-24 |
| 02 | [domain](02-domain.md) | ✅ Corregido | 2026-05-24 |
| 03 | [player-echo](03-player-echo.md) | ✅ Corregido | 2026-05-24 |
| 04 | [essences](04-essences.md) | ✅ Corregido | 2026-05-24 |
| 05 | [ideas-doctrines](05-ideas-doctrines.md) | ✅ Corregido | 2026-05-24 |
| 06 | [ideological-drift](06-ideological-drift.md) | ✅ Corregido | 2026-05-24 |
| 07 | [actions](07-actions.md) | ✅ Corregido | 2026-05-24 |
| 08 | [temporal-system](08-temporal-system.md) | ✅ Corregido | 2026-05-24 |
| 09 | [economy](09-economy.md) | ✅ Corregido | 2026-05-24 |
| 10 | [factions](10-factions.md) | ✅ Corregido | 2026-05-24 |
| 11 | [autoplayer](11-autoplayer.md) | ✅ Corregido | 2026-05-24 |
| 12 | [ai-integration](12-ai-integration.md) | ✅ Corregido | 2026-05-24 |
| 13 | [events](13-events.md) | ✅ Corregido | 2026-05-24 |
| 14 | [godot-contract](14-godot-contract.md) | ✅ Corregido | 2026-05-24 |
| 15 | [debugging](15-debugging.md) | ✅ Corregido | 2026-05-24 |
| 16 | [mvp](16-mvp.md) | ✅ Corregido | 2026-05-24 |
| 17 | [risks](17-risks.md) | ✅ Corregido | 2026-05-24 |
| 18 | [game-definition](18-game-definition.md) | ✅ Corregido | 2026-05-24 |

## Convenciones

- Cada spec empieza con `# [Número] - [Título]`
- Los ejemplos de código mantienen indentación original
- Las referencias cruzadas: `[spec-nombre](spec-XX.md)`
- Metadatos al final de cada spec: fecha creación, fuente, dependencias

## Estado

- En desarrollo: todas las specs derivan del spec.md original unificado
- Objetivo: spec-driven development con specs independientes y versionables