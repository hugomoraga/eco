# SPEC Index

Guía de lectura y dependencias entre especificaciones.

## Especificaciones

| # | Spec | Descripción | Dependencias | Status |
|---|------|-------------|--------------|--------|
| 00 | [index](00-index.md) | Este índice | - | stable |
| 01 | ~~[architecture](implemented/01-architecture.md)~~ | Stack, estructura carpetas, principios | - | ready |
| 02 | ~~[domain](implemented/02-domain.md)~~ | Modelo de entidades World, Civilizations | 01 | ready |
| 03 | ~~[player-echo](implemented/03-player-echo.md)~~ | Atributos, encarnación, reencarnación | 01, 02 | ready |
| 04 | [essences](04-essences.md) | Modelo de esencias original | 01 | superseded |
| 05 | [ideas-doctrines](05-ideas-doctrines.md) | Sistema de ideas y doctrinas | 01, 02 | ready |
| 06 | [ideological-drift](06-ideological-drift.md) | Drift ideológico de civilizations | 01, 04, 05 | in_progress |
| 07 | ~~[actions](implemented/07-actions.md)~~ | Acciones humanas, efectos, duración | 01, 02 | ready |
| 08 | ~~[temporal-system](implemented/08-temporal-system.md)~~ | ActionTick, WorldTick, HistoricalTick | 01, 07 | ready |
| 09 | [economy](09-economy.md) | Economía estructural, coste social | 01, 02 | in_progress |
| 10 | [factions](10-factions.md) | Faction Tick System, agency limitada | 01, 02, 04 | in_progress |
| 11 | [autoplayer](11-autoplayer.md) | Goals, evaluación multiobjetivo, personalidad | 01, 03, 06, 07 | ready |
| 12 | [ai-integration](12-ai-integration.md) | Roles IA, validación 3 capas | 01, 06 | ready |
| 13 | [events](13-events.md) | Plantillas sistémicas, emergencia | 01, 02, 09, 12 | ready |
| 14 | [godot-contract](14-godot-contract.md) | Snapshots genéricos, VisualRegistry | 01, 02, 03, 08 | draft |
| 15 | [debugging](15-debugging.md) | Logs JSONL, inspector, replay | 01 | in_progress |
| 16 | [mvp](16-mvp.md) | MVP propsetos, criterios de éxito | 01, todos | stable |
| 17 | [risks](17-risks.md) | Riesgos, mitigaciones | 01, todos | draft |
| 18 | [game-definition](18-game-definition.md) | Definición corta, visión | - | draft |
| 19 | [mvp-implementation](19-mvp-implementation.md) | Tracking de implementaciones MVP | 16 | stable |
| 20 | [integration](20-integration.md) | Conectar sistemas desconectados | 04, 09, 13 | in_progress |
| 21 | [testing-coverage](21-testing-coverage.md) | Tests para 10 sistemas | 01-12 | in_progress |
| 22 | [ai-manifesto](22-ai-manifesto.md) | Manifesto genera tags + influencia | 07, 12 | ready |
| 23 | [i18n](23-i18n.md) | Sistema de idiomas (es/en) | 01 | ready |
| 24 | [configuration](24-configuration.md) | .env, config.yaml, API keys centralizadas | 01 | ready |
| 25 | [console-logging](25-console-logging.md) | Output consola + logs detallados | 19 | in_progress |
| 26 | [dynamism](26-dynamism.md) | Diminishing returns + world evolution | 19 | in_progress |
| 27 | [tuning-diminishing-returns](27-tuning-diminishing-returns.md) | tuning.yaml + diminishing returns | 19 | ready |
| 28 | [turn-system-npc-templates](28-turn-system-npc-templates.md) | Turno jugador + NPC templates con diálogos i18n | 01, 02, 07, 08 | ready |
| 29 | [world-state-metrics](29-world-state-metrics.md) | World metrics: pressure, legitimacy, resources | 01, 02, 07, 08, 26 | ready |
| 30 | [living-circles](30-living-circles.md) | Circle members, growth, NPC spawning | 01, 02, 07, 08, 26, 28, 29 | in_progress |
| 31 | [actions-with-consequences](31-actions-with-consequences.md) | Actions modify world state, real effects | 01, 02, 07, 08, 26, 29 | ready |
| 32 | [echo-spawning](32-echo-spawning.md) | Daughter echoes, essence mutation | 01, 02, 07, 08, 26, 27, 29 | ready |
| 33 | ~~[console-display](33-console-display.md)~~ | Observer pattern, DebugLog, colors | 01, 02 | superseded |
| 41 | ~~[tui-refactor](implemented/41-tui.md)~~ | TUI legacy → refactor notes | - | deprecated |
| 42 | ~~[refactor-jerarquia](implemented/42-refactor-jerarquia.md)~~ | Reorganizar: game_core/ motor, ui_core/ output, player_core/ input | 37, 11 | deprecated |
| 43 | ~~[ui](implemented/43-ui.md)~~ | Sistema UI unificado — fuente de verdad | 01, 19, 24, 42 | superseded |
| 44 | ~~[domain-entities](implemented/44-domain-entities.md)~~ | Duplicado de 02-domain | 01 | deprecated |
| 45 | ~~[domain-refactor](implemented/45-domain-refactor.md)~~ | Refactor incompleto → merge en 43 | 01, 02 | deprecated |
| 46 | ~~[world-generation](implemented/46-world-generation.md)~~ | Civilization templates + Person dataset + IA generation | 01, 02, 03, 19, 28, 30, 43 | ready |
| 47 | ~~[essence-system-v2](implemented/47-essence-system-v2.md)~~ | EssenceProfile, 20 essencias, matriz compatibilidades, mutación | 01 | ready |
| 48 | ~~[world-start-screen](implemented/48-world-start-screen.md)~~ | World start screen UI | 01, 43 | ready |
| 50 | ~~[ui-core-protocol](implemented/50-ui-core-protocol.md)~~ | UI ↔ game_core protocol | 01, 43 | ready |
| 51 | [code-patterns](51-code-patterns.md) | Factory & systems patterns, naming conventions | 01 | ready |
| 52 | [person-host-echo](52-person-host-echo.md) | Person/Host/Echo refactor con herencia OOP | 51 | in_progress |
| 53 | ~~[logger](implemented/53-logger.md)~~ | Structured logging con structlog, dual output (stderr + file) | 01 | ready |
| 54 | ~~[adapter-core-architecture](implemented/54-adapter-core-architecture.md)~~ | Hexagonal: core/, infra/, adapters/ | 01 | ready |
| 55 | ~~[defensive-error-handling](implemented/55-defensive-error-handling.md)~~ | Try-except en engine threads | 01, 53 | ready |
| 56 | ~~[cli-refactor](implemented/56-cli-refactor.md)~~ | GameConfig + Launcher pattern, default HumanPlayer, --autoplay flag | 01, 53, 55 | ready |
| 57 | [domain-normalization](57-domain-normalization.md) | Normalización: entities/, data/, definitions/, value_objects/ | 01 | in_progress |

## Convenciones

- **~~strikethrough~~** = specs implementadas y deprecadas (moved to `implemented/`)
- **draft** = Sin implementar
- **stable** = Implementado y congelado
- Las specs deprecadas están en `specs/implemented/` como referencia histórica

## Estados

- **draft**: Sin implementar
- **in_progress**: Implementación parcial, código existe pero incompleto
- **ready**: Implementada, es la versión vigente
- **deprecated**: Fue ready pero fue reemplazada por spec más nueva
- **superseded**: Reemplazada (normalmente por versión v2 de la misma spec)
- **stable**: Congelada, no cambia (solo índices y visiones)

## Estructura de carpetas

- `specs/` — Specs activas o pendientes
- `specs/implemented/` — Specs implementadas y deprecated (historical reference)

## Resumen de estados

- **ready / implemented**: 01, 02, 03, 05, 07, 08, 11, 12, 13, 22, 23, 24, 27, 28, 29, 31, 32, 34, 40, 46, 47, 48, 50, 51, 53, 54, 55, 56 (28 specs)
- **in_progress**: 06, 09, 10, 15, 20, 21, 25, 26, 30, 52, 57 (11 specs)
- **draft**: 14, 17, 18 (3 specs)
- **stable**: 00, 16, 19 (3 specs)
- **superseded**: 04, 33 (2 specs)
- **deprecated**: 41, 42, 43, 44, 45 (5 specs)
