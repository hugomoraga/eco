# Spec 42: Refactor — Jerarquía de carpetas

## Status
- **created**: 2024-05-24
- **stage**: draft
- **replaces**: spec-41 (tui legacy)

## Goal

Reorganizar la estructura del proyecto para que las responsabilidades estén claramente separadas. `game_core/` es el motor puro sin dependencias de UI o input.

## Estructura Deseada

```
eco/
├── game_core/            # MOTOR PURO — sin UI, sin input
│   ├── domain/           # Entidades: World, Echo, Circle, NPC, Essence, Faction
│   │   ├── __init__.py
│   │   ├── world.py
│   │   ├── echo.py
│   │   ├── circle.py
│   │   ├── npc.py
│   │   ├── essence.py
│   │   └── faction.py
│   │
│   ├── systems/          # Lógica de simulación
│   │   ├── __init__.py
│   │   ├── simulation.py
│   │   ├── pressure.py
│   │   ├── events.py
│   │   ├── faction_tick.py
│   │   └── observer.py
│   │
│   ├── actions/         # Acciones del juego
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── echo_actions.py
│   │
│   ├── ai/              # AI brain (base, adapters)
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── adapters/
│   │
│   ├── data/            # Carga de datos
│   │   ├── __init__.py
│   │   └── yaml_loader.py
│   │
│   └── utils/           # Utilidades del motor
│       ├── __init__.py
│       ├── config.py
│       ├── tuning.py
│       ├── debug_log.py
│       └── random.py
│
├── ui_core/              # OUTPUT — rich, colors, panels, widgets
│   ├── __init__.py
│   ├── console.py        # Rich Console singleton
│   ├── styles.py         # Paleta ECO, estilos
│   ├── components.py     # turn_header, world_metrics_table, event_banner
│   ├── selector.py       # Flechas + Enter (prompt_toolkit)
│   ├── commands.py       # /help, /history, /replay, /save, /load, /quit
│   ├── history.py        # Historial de acciones + replay
│   └── session.py        # Guardar/cargar partida
│
├── player_core/          # INPUT — modos de jugador
│   ├── __init__.py
│   ├── modes/
│   │   ├── __init__.py
│   │   ├── player.py     # Humano
│   │   ├── autoplay.py   # IA (usa game_core.ai)
│   │   └── hybrid.py     # Mixto
│   ├── base.py
│   └── factory.py
│
├── scripts/              # Dev scripts (audit, tests)
├── specs/               # Especificaciones
├── run.py                # Entry point (RAÍZ, único)
└── pyproject.toml
```

## Decisions

### 1. game_core/ = Motor puro
- **No tiene dependencias** de ui_core ni player_core
- Solo sabe de sí mismo + datos externos (yaml, env)
- Domain: entidades del mundo
- Systems: lógica de simulación
- Actions: acciones ejecutables
- AI: brain reusable (usado por autoplay y NPCs)
- Utils: config, tuning, debug, random

### 2. ui_core/ = Output
- Solo sabe de game_core (para display)
- No sabe de player_core
- rich + prompt_toolkit para output bonito
- Commands para interacción (/help, /history, etc)
- Session para guardar/cargar

### 3. player_core/ = Input
- Depende de game_core (usa AI brain)
- Depende de ui_core (muestra output)
- Modes: player, autoplay, hybrid
- Factory para crear el modo correcto

### 4. run.py = Entry point único
- En la raíz, no dentro de ningún módulo
- Lee .env, configura, elige modo via factory, lanza

## Archivos a Eliminar (reemplazados por ui_core/)

| Archivo | Líneas | Razón |
|---------|--------|-------|
| `engine/tui.py` | 623 | Reemplazado por ui_core/selector.py |
| `engine/console_output.py` | 373 | Reemplazado por ui_core/console.py |
| `engine/console_display.py` | 139 | Reemplazado por ui_core/components.py |

## Archivos a Dividir

| Archivo | Líneas | Acción |
|---------|--------|--------|
| `domain/entities.py` | 316 | Dividir en `domain/echo.py`, `domain/circle.py`, etc |
| `actions/echo_actions.py` | 438 | Dividir por tipo de acción |

## Archivos a Mover

| Origen | Destino |
|--------|---------|
| `engine/simulation.py` | `systems/simulation.py` |
| `engine/pressure.py` | `systems/pressure.py` |
| `engine/events.py` | `systems/events.py` |
| `engine/faction_tick.py` | `systems/faction_tick.py` |
| `engine/observer.py` | `systems/observer.py` |
| `engine/random.py` | `utils/random.py` |
| `config.py` | `utils/config.py` |
| `tuning.py` | `utils/tuning.py` |
| `debug_log.py` | `utils/debug_log.py` |

## Migration Plan

### Fase 1: Crear estructura
```bash
mkdir -p game_core/systems game_core/utils
mkdir -p ui_core
mkdir -p player_core/modes
```

### Fase 2: Mover archivos de engine/ → systems/
- simulation.py, pressure.py, events.py, faction_tick.py, observer.py

### Fase 3: Mover archivos sueltos → utils/
- config.py, tuning.py, debug_log.py, engine/random.py

### Fase 4: Crear ui_core/ (basado en spec-37)
- console.py, styles.py, components.py
- selector.py, commands.py, history.py, session.py

### Fase 5: Crear player_core/modes/
- player.py, autoplay.py, hybrid.py, base.py, factory.py

### Fase 6: Dividir archivos grandes
- domain/entities.py → archivos separados
- actions/echo_actions.py → por tipo

### Fase 7: Eliminar duplicados
- engine/tui.py, engine/console_output.py, engine/console_display.py
- engine/__init__.py (si quedó obsoleto)

### Fase 8: Consolidar run.py
- Un solo run.py en la raíz
- Eliminar game_core/run.py

### Fase 9: Actualizar imports
- Buscar todos los imports que apunten a rutas viejas
- Actualizar a nuevas rutas

### Fase 10: Verificar
- `pytest` pasa
- `python run.py` funciona

## Criteria

- `game_core/` no importa `ui_core/` ni `player_core/`
- Cada archivo ≤ 200 líneas (idealmente ≤ 100)
- Jerarquía obvia: si es lógica del juego → game_core, si es output → ui_core, si es input → player_core
- Tests pasan después del refactor
- Un solo entry point en la raíz

## Dependencies
- spec-37 (ui_core design)
- spec-11 (autoplay design)
- spec-19 (mvp tracking)