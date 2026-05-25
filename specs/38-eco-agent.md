# Spec 44: ECO Agent — Terminal Interaction Layer

## Status
- **created**: 2024-05-24
- **stage**: draft
- **replaces**: part of spec-33 (colors/display), spec-41 (interactive menu)

## Goal

Implementar una capa de interacción terminal para ECO donde el usuario pueda:
1. Jugar la simulación de forma interactiva (menú numerado, no arrow keys)
2. Hablar con el "ECO Agent" (un CLI agent) para consultar el estado, pedir ayuda, o delegar tareas

Inspirado en Hermes Agent (nousresearch/hermes-agent) que usa STDIO transport + prompt_toolkit + rich.

## Architecture

```
                    ┌─────────────────────────┐
                    │     User Terminal       │
                    │  (STDIO interactivo)    │
                    └───────────┬─────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │   ECO Agent CLI         │
                    │   (prompt_toolkit REPL) │
                    └──┬──────────────────┬──┘
                       │                  │
            ┌──────────▼──┐      ┌───────▼──────┐
            │  Simulation  │      │  Agent Brain │
            │   Engine     │      │  (via tools) │
            └──────────────┘      └──────────────┘
```

## Components

### 1. `eco_agent/` — Nuevo paquete

```
game_core/
├── eco_agent/
│   ├── __init__.py
│   ├── cli.py              # Entry point: python -m eco_agent
│   ├── repl.py             # prompt_toolkit REPL session
│   ├── protocol.py         # JSON message handling
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── simulation.py   # Tools para interactuar con la simulación
│   │   ├── world.py        # Consultar estado del mundo
│   │   └── actions.py     # Ejecutar acciones
│   └── formatting/
│       ├── __init__.py
│       └── rich_helpers.py  # Rich rendering helpers
```

### 2. Dependencies (agregar a pyproject.toml)

```
prompt_toolkit==3.0.52  # CLI input interactivo
rich==14.3.3            # Terminal formatting
```

### 3. Modo de operación

**Dos modos:**

1. **Simulation Mode** (juego) — `--play`
   ```
   $ python -m eco_agent --play --turns 10
   ```
   - REPL muestra estado cada turno
   - Usuario selecciona acción (1-8) o habla con agente
   - Agente puede sugerir acciones, explicar qué pasó

2. **Agent Mode** (chat con agente) — `--agent`
   ```
   $ python -m eco_agent --agent
   ```
   - Chat interactivo con el agente
   - El agente tiene tools para inspectar la simulación
   - Puede mostrar estado, sugerir próximos pasos, o ejecutar acciones

### 4. Tools del Agente

```python
#eco_agent/tools/simulation.py
available_tools = [
    {
        "name": "get_world_state",
        "description": "Get current simulation state (metrics, circles, NPCs, echoes)",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "get_turn_history",
        "description": "Get history of past turns with actions and outcomes",
        "parameters": {"type": "object", "properties": {"turns": {"type": "integer"}}}
    },
    {
        "name": "do_action",
        "description": "Execute a game action (found_circle, write_manifesto, etc.)",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["found_circle", "write_manifesto", ...]}
            }
        }
    },
    {
        "name": "get_events",
        "description": "Get world events from last N turns",
        "parameters": {"type": "object", "properties": {"since_turn": {"type": "integer"}}}
    },
    {
        "name": "suggest_next",
        "description": "Agent suggests the best next action given current state",
        "parameters": {"type": "object", "properties": {}}
    }
]
```

### 5. Protocolo de comunicación

El REPL usa JSONLines para comunicar con el agente:

```json
// User message
{"type": "user", "content": "¿qué debería hacer ahora?", "turn": 5}

// Agent response
{"type": "agent", "content": "Basándome en el estado actual... te sugiero write_manifesto porque...", "tool_calls": []}

// Agent with tool call
{"type": "agent", "content": "Voy a consultar el estado del mundo...", "tool_calls": [{"name": "get_world_state", "id": "call_1"}]}

// Tool result
{"type": "tool", "tool_call_id": "call_1", "result": {...}}
```

### 6. Rich formatting

```python
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# Tabla de métricas
table = Table(title="Estado del Mundo")
table.add_column("Métrica", style="cyan")
table.add_column("Valor", style="magenta")
table.add_row("Civil unrest", "30.0")
table.add_row("Authority", "60.0")

console.print(table)

# Panel de ayuda
console.print(Panel("[bold]ECO Agent[/bold]\n\nComandos:\n- help\n- status\n- action <nombre>\n- suggest", border_style="green"))
```

## Implementation Plan

### Phase 1: Infrastructure
- [ ] Crear `eco_agent/` paquete
- [ ] Agregar dependencies a pyproject.toml
- [ ] Implementar `rich_helpers.py` (colores, tablas, panels)
- [ ] Implementar `protocol.py` (JSON handling)

### Phase 2: REPL
- [ ] Implementar `repl.py` con prompt_toolkit
- [ ] Session loop: leer input → procesar → responder
- [ ] Modo `--play` (simulation)
- [ ] Modo `--agent` (chat)

### Phase 3: Tools
- [ ] Implementar `tools/simulation.py` — get_world_state, get_turn_history
- [ ] Implementar `tools/actions.py` — do_action
- [ ] Implementar `tools/world.py` — get_events

### Phase 4: Integration
- [ ] Conectar tools con SimulationEngine existente
- [ ] Hook para que el agente pueda observar la simulación
- [ ] Tests de integración

## Notes

- **No usar blessed** — tiene bugs con arrow keys en macOS (problema conocido)
- **prompt_toolkit** maneja input interactivo correctamente (incluye history, auto-complete)
- **rich** para todo el formatting (reemplaza prints ANSI crudos)
- El agente es "dumb" — delega a SimulationEngine, no tiene IA propia (salvo que se conecte a un LLM)
- Para el chat con IA real, se podría agregar un `--llm` flag que use el AI adapter existente

## References

- Hermes Agent: https://github.com/nousresearch/hermes-agent
- prompt_toolkit: https://github.com/prompt-toolkit/python-prompt-toolkit
- rich: https://github.com/Textualize/rich