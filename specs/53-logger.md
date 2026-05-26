# SPEC-53: Logger/Observabilidad

## Context / Problema

Necesitamos observabilidad en el motor de simulación para:
1. **Debuggear hangs/crashes** - especialmente en mechanics de systems y actions
2. **Entender flujo de ejecución** - trace de entrada/salida en funciones críticas
3. **Capacidad de edge cases** - try/except con contexto, condiciones "esto no debería pasar"
4. **Separación de canales** - logs van a stderr (consola) y archivo, NO a stdout (protocolo TUI)

## Decisiones

### Librería
- `structlog` - structured logging, JSON output, processors chain
- Instalar como dependency `structlog>=25.0`

### Ubicación
- `game_core/utils/logger.py` - módulo centralizado

### Output
- **stderr** (consola) - visible durante ejecución, NO mezcla con protocolo JSON
- **`runs/{run_id}/debug.log`** - archivo persistente por run para análisis post-mortem

### Configuración
- `ECO_LOG_LEVEL=DEBUG|INFO|WARNING|ERROR` en `.env`
- Default: `DEBUG` en desarrollo

### Semántica de niveles

```
INFO:  Eventos normales del juego (turn_start, player_death, action_executed, reincarnation, circle_created)
DEBUG: Traceo detallado para debugging (entrada/salida de funciones, queue states, decision reasoning)
ERROR: Excepciones reales (API timeout, file not found, bugs, asserts fallidos)
```

### API

```python
from game_core.utils.logger import get_logger

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

### Archivos a modificar (prioridad alta - FULL logging)

**systems/**
- `simulation.py` - loop principal, action execution, NPC damage, reincarnation
- `reincarnation.py` - find_candidate, reincarnate_echo, preserve_legacy
- `faction_tick.py` - faction updates
- `event_pool.py` - event selection
- `event_generator.py` - AI adapter calls

**actions/**
- `base.py` - execute, can_execute
- `social_actions.py` - sabotage, spread_rumor, talk, ritualize
- `circle_actions.py` - found_circle, join_circle, leave_circle
- `manifesto_actions.py` - write_manifesto
- `propagation_actions.py` - propagate_idea

**autoplayer/**
- `npc_engine.py` - decision scoring, action selection
- `autoplayer_engine.py` - strategy decisions

### Reemplazos
- Eliminar `game_core/utils/debug_log.py` completamente
- Reemplazar todos los `from game_core.utils.debug_log import DebugLog, dbg` con `from game_core.utils.logger import get_logger`

## Edge Cases a Loggear

1. **get_action timeout** - cuando queue está vacía y usa autoplay
2. **NPC damage to player** - cada instance, con before/after vitality
3. **Player death** - trigger, legacy preservation, candidate search, reincarnation result
4. **Reincarnation failure** - no candidate found
5. **AI adapter calls** - entrada/salida, timeout, exceptions
6. **Circle member_count >= 3** - NPC generation trigger
7. **Conditionals "esto no debería pasar"** - log.warning con contexto

## Testing

1. `python -m game_core.cli --max-turns 5 --autoplay` debe correr sin hang
2. `runs/{run_id}/debug.log` debe existir y tener contenido
3. stderr debe mostrar logs durante ejecución
4. JSON válido en debug.log (parseable post-run)
