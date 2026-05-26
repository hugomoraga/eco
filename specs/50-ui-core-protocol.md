# SPEC-50: UI-Core Protocol (v1)

**Estado:** draft
**Creado:** 2026-05-25
**Última actualización:** 2026-05-25

---

## 0. Dependencias

```
# game_core dependencies (solo stdlib)
- Sin dependencias externas

# ui_core dependencies
- textual>=0.50.0
- rich>=14.0.0
```

---

## 1. Objetivo

Separar `game_core` y `ui_core` en procesos independientes communicating через JSON por stdin/stdout. Esto permite:

- **Swappable UIs**: Cualquier UI que hable el protocolo puede controlar game_core
- **Textual TUI**: Primera implementación con Textual
- **Testing**: Puedo enviar mensajes con `echo '{"type":"action"...}'` y verificar respuestas
- **Replay**: El log de eventos es本身就是 un replay del juego

---

## 2. Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    ui_core (Textual)                       │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  GameApp (Textual)                                   │  │
│  │  - Captures keyboard input                           │  │
│  │  - Renders TUI layout                               │  │
│  │  - Sends commands to game_core subprocess           │  │
│  │  - Receives events and renders                      │  │
│  └─────────────────────────────────────────────────────┘  │
│                          │                                  │
│                          │ stdin/stdout                   │
│                          ▼                                  │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ JSON messages (pipe)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    game_core (Pure Engine)                  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  SimulationEngine + GameCoreCLI                      │  │
│  │  - Runs simulation loop                              │  │
│  │  - Emits events (turn_start, action_result, etc.)  │  │
│  │  - Receives commands (action, quit, query)         │  │
│  │  - No knowledge of UI                                │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Protocolo de Mensajes

### 3.1 Formato General

Todos los mensajes son objetos JSON separados por newline (`\n`).

```
{"type": "...", ...}
```

### 3.2 Mensajes UI → Game Core (Comandos)

| Tipo | Campos | Descripción |
|------|--------|-------------|
| `action` | `turn`, `action` | Ejecuta acción del Echo |
| `query` | `query_type`, `params` | Pide información al engine |
| `quit` | - | Termina la simulación |

#### `action`
```json
{"type": "action", "turn": 1, "action": "write_manifesto"}
```

#### `query`
```json
{"type": "query", "query_type": "world_state", "turn": 0}
{"type": "query", "query_type": "available_actions", "turn": 1}
{"type": "query", "query_type": "metric_history", "metric": "stability"}
```

#### `quit`
```json
{"type": "quit"}
```

---

### 3.3 Mensajes Game Core → UI (Eventos y Respuestas)

| Tipo | Campos | Descripción |
|------|--------|-------------|
| `ready` | `initial_state` | Engine inicializado, listo para recibir comandos |
| `turn_start` | `turn`, `world_tick`, `world_state` | Comienzo de turno |
| `action_result` | `turn`, `action`, `success`, `message`, `delta` | Resultado de acción |
| `turn_end` | `turn`, `world_tick`, `action_taken` | Fin de turno |
| `event` | `turn`, `event_type`, `title`, `summary` | Evento generado (crisis, opportunity, etc.) |
| `query_response` | `query_id`, `data` | Respuesta a query |
| `crisis` | `turn`, `metric`, `value` | Threshold de crisis cruzado |
| `world_state` | `turn`, `civ`, `echo`, `metrics`, `entities` | Estado completo del mundo |
| `tick` | `turn`, `world_tick`, `action_result` | Tick individual |
| `terminated` | `reason` | Engine停止了 |
| `error` | `message` | Error occurred |

#### `ready`
```json
{
  "type": "ready",
  "initial_state": {
    "civ": {"id": "default", "name": "Default Civilization", ...},
    "echo": {"id": "...", "name": "First Echo", "phase": "active", ...},
    "persons": [...],
    "config": {"max_turns": 100, "seed": 42, ...}
  }
}
```

#### `turn_start`
```json
{
  "type": "turn_start",
  "turn": 1,
  "world_tick": 0,
  "world_state": {
    "stability": 50.0,
    "pressure": 30.0,
    "legitimacy": 60.0,
    "resources_global": 70.0,
    "population": 10000,
    "echoes": 1,
    "circles": 0,
    "factions": 1
  }
}
```

#### `action_result`
```json
{
  "type": "action_result",
  "turn": 1,
  "action": "write_manifesto",
  "success": true,
  "message": "Manifesto written successfully",
  "delta": {
    "clarity": {"old": 70.0, "new": 75.0, "change": 5.0},
    "influence": {"old": 10.0, "new": 12.0, "change": 2.0}
  }
}
```

#### `query_response`
```json
{
  "type": "query_response",
  "query_id": "uuid-1234",
  "query_type": "world_state",
  "data": {
    "turn": 0,
    "civ": {...},
    "echo": {...},
    "metrics": {...}
  }
}
```

---

## 4. Flujo de Comunicación

### 4.1 Inicialización

```
UI                           GameCore
 │                             │
 │                             │ (spawns subprocess)
 │ ──────── handshake? ────────►│
 │                             │
 │ ◄──────── ready ────────────│
 │        (initial_state)       │
 │                             │
```

### 4.2 Turno Típico

```
UI                           GameCore
 │                             │
 │ ──────── action ───────────►│
 │        (turn, action)         │
 │                             │
 │ ◄────── turn_start ─────────│
 │        (new state)           │
 │                             │
 │ ─────── [engine runs] ──────►
 │                             │
 │ ◄────── action_result ───────│
 │ ◄────── turn_end ────────────│
 │                             │
```

### 4.3 Query

```
UI                           GameCore
 │                             │
 │ ─────── query ─────────────►│
 │        (query_type)          │
 │                             │
 │ ◄──── query_response ───────│
 │        (data)               │
 │                             │
```

---

## 5. Estados del Engine

```
                    ┌──────────────┐
                    │   STARTING   │
                    └──────┬───────┘
                           │ emit ready
                           ▼
                    ┌──────────────┐
              ┌─────►│   WAITING   │◄─────┐
              │      └──────┬───────┘      │
              │             │              │
              │   input     │  input       │
              │   action    │  action      │
              │             ▼              │
              │      ┌──────────────┐      │
              │      │  PROCESSING │      │
              │      └──────┬───────┘      │
              │             │              │
              │             │ all done      │
              │             ▼              │
              │      ┌──────────────┐      │
              │      │  TERMINATED  │──────┘
              │      └──────────────┘ quit
              │
              │ quit
              ▼
      ┌──────────────┐
      │    QUIT      │
      └──────────────┘
```

---

## 6. Consideraciones de Diseño

### 6.1 Why JSON over binary?
- Human readable para debugging
- Fácil de testear con echo/scripting
- Textual puede usar asyncio con streams

### 6.2 Por qué no HTTP/WebSocket?
- Overkill para proceso local
- Requiere setup extra
- JSON por pipe es suficiente

### 6.3 Error handling
- Mensajes inválidos: engine responde con `{"type": "error", "message": "..."}`
- Conexión cortada: engine termina gracefully

### 6.4 Backward Compatibility
- `run.py` actual sigue funcionando (invoca engine directamente)
- `python -m game_core.cli` es el nuevo entry point para modo headless con UI externa
- Logs `simulation.jsonl` siguen igual (pueden servir para replay)

---

## 7. Estructura de Archivos

```
game_core/
├── __init__.py
├── systems/
│   ├── simulation.py      # SimulationEngine (sin cambios en interface publica)
│   └── observer.py         # SimulationObserver ABC
├── protocol/
│   ├── __init__.py
│   ├── messages.py         # Message types, dataclasses
│   └── codec.py           # encode/decode JSON messages
├── cli.py                 # Entry point: python -m game_core.cli [opts]
└── ...

ui_core/
├── textual/               # Nueva implementación Textual
│   ├── __init__.py
│   ├── app.py            # GameApp (Textual)
│   ├── widgets/           # Componentes TUI
│   │   ├── __init__.py
│   │   ├── layout.py     # Layout principal
│   │   ├── metrics.py     # Panel de métricas
│   │   ├── actions.py     # Selector de acciones
│   │   └── log.py         # Activity log
│   └── subprocess.py      # Communicates with game_core
└── ...
```

---

## 8. Implementación en Fases

### Fase 1: Protocolo Base
- [ ] `game_core/protocol/messages.py` - Definir todos los tipos de mensajes
- [ ] `game_core/protocol/codec.py` - Encoder/decoder JSON
- [ ] Modificar `SimulationEngine` para generar eventos estructurados

### Fase 2: CLI Entry Point
- [ ] `game_core/cli.py` - Lee stdin, escribe stdout
- [ ] Integrar con engine loop
- [ ] Testear con `echo '{"type":"action"...}' | python -m game_core.cli`

### Fase 3: Textual UI (Nuevo ui_core)
- [ ] `ui_core/textual/app.py` - App principal
- [ ] `ui_core/textual/subprocess.py` - Wrapper para subprocess
- [ ] Layout con widgets existentes

### Fase 4: Integración
- [ ] Conectar Textual app con game_core subprocess
- [ ] Selector de acciones (flechas/números)
- [ ] Renderizado de estado en tiempo real

---

## 9. Compatibilidad con runs/

Los archivos `simulation.jsonl` ya existentes pueden servir como:
- **Replay**: UI puede leer un simulation.jsonl y reproducir el juego
- **Logs**: Formato similar al nuevo protocolo (difieren en estructura pero no en concepto)
- **Refactor**: No es necesario cambiar los logs existentes; el nuevo protocolo es para comunicación runtime

**Decisión**: Mantener `simulation.jsonl` como archivo de log (append-only), el nuevo protocolo es para stdin/stdout.

---

## Status History

- 2026-05-25: v1 — Initial draft

---

## Metadata

- Dependencies: spec-43 (UI actual), spec-47 (Civs), game_core actual
- Replaces: spec-43 ( частично - nuevo protocolo para UI)
- Status: draft