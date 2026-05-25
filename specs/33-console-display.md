# 33 - Console Display + Debug System

**Estado:** implemented
**Fecha:** 2026-05-24 (refactored)
**Dependencias:** 01, 02

---

## 1. Arquitectura General

Tres sistemas independientes que se conectan al `SimulationEngine`:

```
┌─────────────────────────────────────────────────────────┐
│                 SimulationEngine (core)                │
│  - Solo lógica, world state                            │
│  - Notifica observers via _notify()                    │
│  - No sabe nada de display ni input                    │
└───────────────────────┬─────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
   ┌─────────┐    ┌───────────┐   ┌───────────┐
   │DebugLog │    │  Input    │   │ Observers │
   │(file)   │    │  Source   │   │(display)  │
   └─────────┘    └───────────┘   └───────────┘
```

### Responsabilidades

| Sistema | Responsabilidad | Output |
|---------|-----------------|--------|
| `DebugLog` | Logger estructural para debugging | `run_*/debug.log` (archivo) |
| `InputSource` | Devuelve action name string | `"found_circle"`, `None` |
| `SimulationObserver` | Renderiza output para humanos | `stdout` (ConsoleDisplay) |

### Principios

- El engine NO renderiza output — solo notifica observers
- `InputSource.get_action()` devuelve string, no hace display
- `DebugLog` es archivo solo — cero stdout
- El engine puede correr headless sin ConsoleDisplay

---

## 2. DebugLog (`game_core/debug_log.py`)

### Propósito

Logger estructural para debugging. Escribe a `run_*/debug.log` — NO a stdout. El stdout es responsabilidad del observer/display.

### API

```python
from game_core.debug_log import DebugLog, dbg

# Inicialización (una vez, al inicio del engine)
DebugLog.init(run_dir: Path)

# Acceso (singleton)
log = dbg()
log.debug("mensaje debug")
log.info("mensaje info")
log.warn("mensaje warning")
log.error("mensaje error", exc: Exception | None = None)
```

### Niveles

| Nivel | Prefix | Sale a stdout? | Sale a archivo? |
|-------|--------|----------------|-----------------|
| DEBUG | `[DBG]` | No | Sí |
| INFO | `[INF]` | Sí | Sí |
| WARN | `[WRN]` | Sí | Sí |
| ERROR | `[ERR]` | Sí | Sí |

### Formato

```
2026-05-24 19:34:33.451 [INFO] Turn 1 started — pressure=30.0 legitimacy=60.0
```

### Helpers de contexto

```python
log.turn_start(turn, world)
log.turn_end(turn, action)
log.input_mode(mode, input_class)
log.menu_interactive(interactive, reason)
log.key_captured(key_desc, raw)
log.menu_selection(action, index)
log.fallback_to_text(reason)
log.fallback_to_autoplay(reason)
```

### Qué loguear

**Siempre:**
- Turn start/end
- Input source mode + class
- Fallback triggers (interactive → text → autoplay)
- Excepciones con traceback

**En verbose mode:**
- Método entry/exit
- Cada key capturada
- Estados del terminal (raw mode on/off)

---

## 3. SimulationObserver (`game_core/engine/observer.py`)

### Interface

```python
class SimulationObserver(ABC):
    def on_turn_start(self, turn: int, world: World) -> None: pass
    def on_turn_end(self, turn: int, world: World, action_taken: str | None) -> None: pass
    def on_action_selected(self, turn: int, action_name: str | None) -> None: pass
    def on_action_result(self, turn: int, action_name: str, result: ActionResult) -> None: pass
    def on_metric_changed(self, turn: int, metric: str, old_val: float, new_val: float) -> None: pass
    def on_event(self, turn: int, event_type: str, title: str, summary: str) -> None: pass
    def on_crisis(self, turn: int, metric: str, value: float) -> None: pass
    def on_circle_founded(self, turn: int, circle_name: str, members: int) -> None: pass
    def on_npc_created(self, turn: int, npc_name: str, npc_role: str) -> None: pass
    def on_echo_spawned(self, turn: int, parent_name: str, daughter_name: str) -> None: pass
    def on_world_state(self, turn: int, world: World) -> None: pass
    def on_circle_activity(self, turn: int, circle_name: str, activity: str) -> None: pass
```

Todos los métodos son opcionales — observers implementan solo lo que necesitan.

### Uso en Engine

```python
class SimulationEngine:
    def __init__(self):
        self._observers: list[SimulationObserver] = []

    def register_observer(self, observer: SimulationObserver):
        self._observers.append(observer)

    def _notify(self, method_name: str, *args, **kwargs):
        for obs in self._observers:
            method = getattr(obs, method_name, None)
            if callable(method):
                try:
                    method(*args, **kwargs)
                except Exception as e:
                    self._dbg.error(f"Observer {type(obs).__name__}.{method_name} failed", e)
```

---

## 4. ConsoleDisplay (`game_core/engine/console_display.py`)

### Propósito

Observer que renderiza a stdout con colores ANSI. No maneja input — solo display.

### Color Palette (on black background)

| Token | ANSI | Uso |
|-------|------|-----|
| `C.RESET` | `\033[0m` | Reset |
| `C.BOLD` | `\033[1m` | Texto importante |
| `C.DIM` | `\033[2m` | Secundario, labels |
| `C.CYAN` | `\033[96m` | Turn headers, WT, valores clave |
| `C.YELLOW` | `\033[93m` | Títulos de eventos |
| `C.GREEN` | `\033[92m` | Deltas positivos |
| `C.RED` | `\033[91m` | Deltas negativos, crisis |
| `C.WHITE` | `\033[97m` | Texto principal |
| `C.GRAY` | `\033[90m` | Bordes, separadores |
| `C.MAGENTA` | `\033[95m` | NPCs, eventos especiales |

### Semántica de colores

```
Evento (neutral)    → YELLOW
Delta positivo      → GREEN + prefix+
Delta negativo      → RED + prefix-
Crisis              → RED + BOLD
Turn header         → CYAN + BOLD
Label de métrica    → DIM
Valor de métrica    → color según threshold
  pressure > 60     → RED (peligro)
  pressure 40-60    → YELLOW (warning)
  pressure < 40     → GREEN (estable)
Acción exitosa      → GREEN + emoji
Acción fallida      → RED
Stub action         → GRAY + [TODO]
NPC speech          → MAGENTA
Circle founded      → GREEN
Echo spawned        → CYAN
```

### Box-drawing

```
╔ ═ ╗ ╠ ╣ ╚ ╝  (bordes)
│ ─                     (separadores)
```

Colores de bordes: `C.GRAY`

### Input Display

El ConsoleDisplay NO maneja input. El TUI renderer (`TUIRenderer`) se encarga de mostrar el prompt y las acciones disponibles. La separación es clara:

- `ConsoleDisplay` — observer, solo output
- `TUIInputSource` — input, devuelve action string

---

## 5. InputSource (`game_core/input/`)

### Contrato

```python
class InputSource(ABC):
    @property
    def mode(self) -> str: ...

    def get_action(self, turn: int, world: World) -> str | None:
        """Returns action name string or None (autoplay)."""
        ...
```

### Implementaciones

| Clase | Modo | Uso |
|-------|------|-----|
| `AutoplayInputSource` | `autoplay` | Siempre devuelve None (autoplay) |
| `PlayerInputSource` | `player` | `input()` plain con timeout |
| `TUIInputSource` | `player` | Arrow key menu + fallback text |
| `HybridInputSource` | `hybrid` | Interactivo cada N turns |

### TUIInputSource (player mode con arrows)

`get_action()`:
1. Renderiza frame vía `TUIRenderer.render_full()`
2. Intenta `InteractiveMenu.run()` (arrow keys)
3. Si falla → `input()` de texto
4. Si EOF → `None` (autoplay)

**Nunca renderiza dentro del input source** — el frame ya fue renderizado por el observer antes de llamar a `get_action()`.

---

## 6. Archivos

```
game_core/
├── debug_log.py              # DebugLog singleton (archivo only)
├── engine/
│   ├── observer.py           # SimulationObserver interface
│   ├── console_display.py   # ConsoleDisplay (stdout renderer)
│   └── tui.py                # TUIRenderer + InteractiveMenu
└── input/
    ├── base.py               # InputSource ABC
    ├── factory.py            # create_input_source()
    ├── player.py             # PlayerInputSource (plain input)
    ├── tui.py                # TUIInputSource (arrow keys)
    ├── autoplay.py           # AutoplayInputSource
    └── hybrid.py             # HybridInputSource
```

---

## 7. Flujo de un Turno

```
Engine.run():
  1. _notify("on_turn_start", turn, world)  → ConsoleDisplay render frame
  2. old_metrics = _snapshot_metrics()
  3. (event generation)
  4. _notify("on_event", ...)               → ConsoleDisplay print event
  5. action_name = input_source.get_action() → TUIInputSource arrow/enter
  6. _notify("on_action_selected", ...)
  7. (execute action)
  8. _notify("on_action_result", ...)
  9. (faction/cirlce/NPC processing)
 10. new_metrics = _snapshot_metrics()
 11. for each metric change:
       _notify("on_metric_changed", ...)
 12. _notify("on_turn_end", ...)
```

---

## 8. Headless Mode

```bash
uv run python game_core/run.py --headless --turns 10
```

`--headless` no registra `ConsoleDisplay` — el engine corre sin output a stdout. Útil para:
- Server mode
- Batch processing
- Testing

El `debug.log` sigue escribiéndose normalmente.

---

## 9. Configuración

```yaml
# En tuning.yaml
input:
  mode: "autoplay"           # autoplay | hybrid | player
  hybrid_interval: 5         # turns between interactive moments
  arrow_keys: true           # enable arrow key navigation (player mode)
```

---

## Status History

- 2026-05-24: created (refactored from 33 + 41 + 42 messy state)
- 2026-05-24: implemented observer pattern + DebugLog + ConsoleDisplay