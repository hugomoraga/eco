# SPEC-53: Logger/Observabilidad

## Status: Implemented

## Context / Problema

Necesitamos observabilidad en el motor de simulación para:
1. **Debuggear hangs/crashes** - especialmente en mechanics de systems y actions
2. **Entender flujo de ejecución** - trace de entrada/salida en funciones críticas
3. **Capacidad de edge cases** - try/except con contexto, condiciones "esto no debería pasar"
4. **Separación de canales** - logs van a stderr (consola) y archivo, NO a stdout (protocolo TUI)

## Arquitectura Implementada

### Hexagonal Architecture

```
core/
├── ports/logger.py          # Logger protocol (interface)
├── utils/logger.py          # Logger shim (delega a infra)
└── application/
    └── processors/          # Usa core.utils.logger

infra/
└── logging/__init__.py     # structlog implementation

adapters/
├── cli/launcher.py         # Llama init_logger ANTES de crear engine
└── ...
```

### Principios

1. **core/ NO importa de infra/** - usa `core.utils.logger`
2. **init_logger() se llama en adapter layer** - antes de crear el engine
3. **Logs van a stderr Y debug.log** - dual output
4. **stdout es solo para protocolo JSON** - comunicación core↔adapters↔TUI

## Decisiones

### Librería
- `structlog>=25.0` - structured logging, processors chain, ConsoleRenderer

### Ubicación
- `infra/logging/__init__.py` - implementación con structlog
- `core/utils/logger.py` - shim que permite a core usar logging sin depender de infra
- `core/ports/logger.py` - protocolo Logger (interfaz)

### Output

**Dual output:**
- **stderr** - logs visibles durante ejecución (formato ConsoleRenderer legible)
- **`runs/{run_id}/debug.log`** - archivo persistente por run para análisis post-mortem

**No stdout** - stdout es reservado para protocolo JSON de comunicación con TUI

### Configuración
- `ECO_LOG_LEVEL=DEBUG|INFO|WARNING|ERROR` en `.env`
- Default: `DEBUG`

### Semántica de niveles

```
INFO:  Eventos normales del juego (turn_start, player_death, action_executed, reincarnation, circle_created)
DEBUG: Traceo detallado para debugging (entrada/salida de funciones, queue states, decision reasoning)
ERROR: Excepciones reales (API timeout, file not found, bugs, asserts fallidos)
```

### API

```python
# En core/application/ - usar core.utils.logger (NO infra.logging)
from core.utils.logger import get_logger

log = get_logger(__name__)  # module-aware logger

# Flujo normal
log.info("turn_start", turn=1, pressure=30.0, legitimacy=60.0)
log.info("action_executed", turn=1, action="sabotage", success=True)
log.info("player_death", player="Carmen", vitality=0, trigger="npc_damage")
log.info("reincarnation_complete", echo="Eco Primordial", new_host="María")

# Edge cases / debugging
log.debug("get_action", turn=1, queue_size=0, using_autoplay=True)
log.debug("reincarnation_candidate", echo_id="abc", candidate="María", score=85.5)
log.exception("api_timeout", error=exc, context={"adapter": "openai", "method": "generate_event"})
log.error("file_not_found", path="data/events.yaml")

# Autoplayer
log.debug("autoplay_decision", turn=1, archetype="propagator", scores={"sabotage": 20, "talk": 85}, selected="talk")
```

```python
# En adapters/ - usar infra.logging directamente
from infra.logging import init_logger, get_logger

init_logger(run_dir)  # Una vez, antes de crear engine
log = get_logger(__name__)
```

## Implementación

### `infra/logging/__init__.py`

```python
_log_file_path: Path | None = None
_file_handle = None

def init_logger(run_dir: Path | None = None) -> None:
    """Dual output: stderr + debug.log si run_dirProvided."""
    if run_dir:
        _log_file_path = run_dir / "debug.log"
        _file_handle = open(_log_file_path, "a", encoding="utf-8")

        def console_and_file_renderer(logger, method_name, event_dict):
            rendered = console_renderer(logger, method_name, event_dict)
            if rendered:
                _file_handle.write(rendered + "\n")
                _file_handle.flush()
            return rendered

        structlog.configure(
            processors=processors + [console_and_file_renderer],
            ...
        )
    else:
        # Solo stderr
        structlog.configure(
            processors=processors + [console_only_renderer],
            ...
        )
```

### `core/utils/logger.py`

```python
"""Shim que permite a core usar logging sin importar de infra."""

def get_logger(name: str) -> Logger:
    from infra.logging import get_logger as _get_logger
    return _get_logger(name)

def init_logger(run_dir: Path | None = None) -> None:
    from infra.logging import init_logger as _init_logger
    _init_logger(run_dir)
```

## Testing

```bash
# Test integración
uv run pytest tests/test_logging_integration.py -v

# Verificar debug.log existe y tiene contenido
uv run python run.py --headless --turns 3
ls runs/run_*/debug.log  # Debe existir
cat runs/run_*/debug.log | head -20  # Debe tener logs
```

## Archivos

| Archivo | Rol |
|---------|-----|
| `infra/logging/__init__.py` | Implementación structlog |
| `core/utils/logger.py` | Shimp para core |
| `core/ports/logger.py` | Protocolo Logger |
| `tests/test_logging_integration.py` | Tests de integración |

## Status History

- 2026-05-26: Implementado con arquitectura hexagonal
- 2026-05-26: Fix bug closure - ahora usa `_file_handle` global con flush
- 2026-05-26: Dual output (stderr + debug.log)
