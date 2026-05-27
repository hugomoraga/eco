# SPEC Index

Guía de lectura y dependencias entre especificaciones.

## Tabla de specs

| # | Spec | Descripción | Dependencias |
|---|------|-------------|--------------|
| 00 | [index](00-index.md) | Este índice | - |
| 01 | [architecture](implemented/01-architecture.md) | Stack, estructura carpetas, principios | - |
| 02 | [domain](implemented/02-domain.md) | Modelo de entidades World, Civilizations | 01 |
| 03 | [player-echo](implemented/03-player-echo.md) | Atributos, encarnación, reencarnación | 01, 02 |
| 07 | [actions](implemented/07-actions.md) | Acciones humanas, efectos, duración | 01, 02 |
| 08 | [temporal-system](implemented/08-temporal-system.md) | ActionTick, WorldTick, HistoricalTick | 01, 07 |
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
| 19 | [mvp-implementation](19-mvp-implementation.md) | Tracking de implementaciones MVP | 16 |
| 20 | [integration](20-integration.md) | Conectar sistemas desconectados | 04, 09, 13 |
| 21 | [testing-coverage](21-testing-coverage.md) | Tests para 10 sistemas | 01-12 |
| 22 | [ai-manifesto](22-ai-manifesto.md) | Manifesto genera tags + influencia | 07, 12 |
| 23 | [i18n](23-i18n.md) | Sistema de idiomas (es/en) | 01 |
| 24 | [configuration](24-configuration.md) | .env, config.yaml, API keys centralizadas | 01 |
| 25 | [console-logging](25-console-logging.md) | Output consola + logs detallados | 19 |
| 26 | [dynamism](26-dynamism.md) | Diminishing returns + world evolution | 19 |
| 27 | [tuning](27-tuning-diminishing-returns.md) | tuning.yaml + diminishing returns | 19 |
| 28 | [turn-system-npc-templates](28-turn-system-npc-templates.md) | Turno jugador + NPC templates con diálogos i18n | 01, 02, 07, 08 |
| 29 | [world-state-metrics](29-world-state-metrics.md) | World metrics: pressure, legitimacy, resources | 01, 02, 07, 08, 26 |
| 30 | [living-circles](30-living-circles.md) | Circle members, growth, NPC spawning | 01, 02, 07, 08, 26, 28, 29 |
| 31 | [actions-with-consequences](31-actions-with-consequences.md) | Actions modify world state, real effects | 01, 02, 07, 08, 26, 29 |
| 32 | [echo-spawning](32-echo-spawning.md) | Daughter echoes, essence mutation | 01, 02, 07, 08, 26, 27, 29 |
| 33 | ~~[console-display](33-console-display.md)~~ | Observer pattern, DebugLog, colors | 01, 02 | **deprecated** → superseded by 43 |
| 34 | [events-system](34-events-system.md) | Event types, triggers, consequences on world | 01, 02, 13, 26, 29 |
| 35 | [circle-system](35-circle-system.md) | Circle identity, members, names, history, growth | 01, 02, 07, 08, 26, 28, 29, 30 |
| 36 | [player-input-system](36-player-input-system.md) | Input modes: autoplay, hybrid, player via .env | 01, 02, 07, 24 |
| 37 | ~~[tui](implemented/37-tui.md)~~ | Terminal UI con rich + prompt_toolkit | 01, 19 | **deprecated** → reemplazada por 43 |
| 38 | ~~[eco-agent](implemented/38-eco-agent.md)~~ | ~~CLI agent~~ → merged into 37 | - | **deprecated** |
| 39 | [circle-names](39-circle-names.md) | Name generator + i18n | 01, 07, 23 |
| 40 | [event-categorization](40-event-categorization.md) | 4 categorías eventos con consecuencias | 01, 02, 13, 26, 29 |
| 41 | ~~[tui](implemented/41-tui.md)~~ | TUI legacy → refactor notes | - | **deprecated** → reemplazada por 43 |
| 42 | ~~[refactor-jerarquia](implemented/42-refactor-jerarquia.md)~~ | Reorganizar: game_core/ motor, ui_core/ output, player_core/ input | 37, 11 | **deprecated** → reemplazada por 43 |
| 43 | [ui](43-ui.md) | Sistema UI unificado — fuente de verdad (reemplaza 33, 37, 41, 42) | 01, 19, 24, 42 | **active** |
| 44 | ~~[domain-entities](implemented/44-domain-entities.md)~~ | Duplicado de 02-domain → deprecated | 01 | **deprecated** |
| 45 | ~~[domain-refactor](implemented/45-domain-refactor.md)~~ | Refactor incompleto → merge en 43 | 01, 02 | **deprecated** |
| 46 | [world-generation](46-world-generation.md) | Civilization templates + Person dataset + IA generation | 01, 02, 03, 19, 28, 30, 43 | draft |
| 47 | [essence-system-v2](47-essence-system-v2.md) | EssenceProfile, 20 essencias, matriz compatibilidades, mutación | 01 | **active** |
| 48 | [world-start-screen](48-world-start-screen.md) | World start screen UI | 01, 43 | draft |
| 50 | [ui-core-protocol](50-ui-core-protocol.md) | UI ↔ game_core protocol | 01, 43 | draft |
| 51 | [code-patterns](51-code-patterns.md) | Factory & systems patterns, naming conventions | 01 | draft |
| 52 | [person-host-echo](52-person-host-echo.md) | Person/Host/Echo refactor con herencia OOP | 51 | draft |
| 53 | [logger](53-logger.md) | Structured logging con structlog, dual output (stderr + file) | 01 | active |
| 55 | [defensive-error-handling](55-defensive-error-handling.md) | Try-except en engine threads para loggear excepciones | 01, 53 | draft |
| 56 | [cli-refactor](56-cli-refactor.md) | GameConfig + Launcher pattern, default HumanPlayer, --autoplay flag | 01, 53, 55 | draft |

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

| # | Spec | Status | Última revisión | Impl |
|---|------|--------|-----------------|------|
| 00 | [index](00-index.md) | stable | 2026-05-24 | - |
| 01 | [architecture](01-architecture.md) | deprecated | 2026-05-24 | 100% |
| 02 | [domain](02-domain.md) | deprecated | 2026-05-24 | 100% |
| 03 | [player-echo](03-player-echo.md) | deprecated | 2026-05-24 | 100% |
| 04 | [essences](04-essences.md) | in_progress | 2026-05-24 | 50% |
| 05 | [ideas-doctrines](05-ideas-doctrines.md) | in_progress | 2026-05-24 | 0% |
| 06 | [ideological-drift](06-ideological-drift.md) | in_progress | 2026-05-24 | 0% |
| 07 | [actions](07-actions.md) | deprecated | 2026-05-24 | 100% |
| 08 | [temporal-system](08-temporal-system.md) | deprecated | 2026-05-24 | 100% |
| 09 | [economy](09-economy.md) | in_progress | 2026-05-24 | 0% |
| 10 | [factions](10-factions.md) | in_progress | 2026-05-24 | 0% |
| 11 | [autoplayer](11-autoplayer.md) | in_progress | 2026-05-24 | 20% |
| 12 | [ai-integration](12-ai-integration.md) | in_progress | 2026-05-24 | 0% |
| 13 | [events](13-events.md) | draft | 2026-05-24 | 0% |
| 14 | [godot-contract](14-godot-contract.md) | in_progress | 2026-05-24 | 30% |
| 15 | [debugging](15-debugging.md) | draft | 2026-05-24 | 0% |
| 16 | [mvp](16-mvp.md) | stable | 2026-05-24 | - |
| 17 | [risks](17-risks.md) | in_progress | 2026-05-24 | 0% |
| 18 | [game-definition](18-game-definition.md) | draft | 2026-05-24 | 0% |
| 19 | [mvp-implementation](19-mvp-implementation.md) | stable | 2026-05-24 | - |

## Convenciones

- Cada spec empieza con `# [Número] - [Título]`
- Los ejemplos de código mantienen indentación original
- Las referencias cruzadas: `[spec-nombre](spec-XX.md)`
- Metadatos al final de cada spec: fecha creación, fuente, dependencias

## Estados

- **draft**: Sin implementar
- **in_progress**: Parcialmente implementado
- **deprecated**: Implementado y obsoleto
- **stable**: Implementado y congelado

## Estructura de carpetas

- `specs/` — Specs activas o pendientes
- `specs/implemented/` — Specs implementadas y deprecated (historical reference)

## Implementacion

- Specs 01, 02, 03, 07, 08: MVP 0 complete (audit 8/8)
- Ver spec-19 para tracking detallado de implementaciones