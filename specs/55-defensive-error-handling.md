# 55-defensive-error-handling.md

## Status: Draft

## Problem

Exceptions in engine threads die silently. When `_save_snapshot`, `_get_player_action`, or other critical methods raise exceptions, the thread dies without logging. The main thread has no idea an error occurred.

**Example**: Turn 10 crash with `TypeError: Object of type UUID is not JSON serializable` - exception occurred but was invisible in debug.log because:
1. Exception happened after `turn_end` log
2. No try-except around `_save_snapshot`
3. Thread died silently
4. Main thread kept waiting for HumanPlayer input

## Principle

**"Fail loudly, not silently"** - All exceptions in engine code MUST be logged before propagating or crashing.

## Pattern

### Basic Pattern

```python
def critical_method(self, ...):
    try:
        # ... dangerous code ...
    except Exception as e:
        self._log.error(
            "method_name_failed",
            error=str(e),
            error_type=type(e).__name__,
            # ... other context ...
        )
        raise  # Re-raise after logging
```

### Fire-and-Forget Pattern (for non-critical failures)

When a failure shouldn't stop the simulation:

```python
def non_critical_method(self, ...):
    try:
        # ... dangerous code ...
    except Exception as e:
        self._log.warning(
            "method_name_failed_continuing",
            error=str(e),
            error_type=type(e).__name__,
        )
        # Continue execution - don't re-raise
```

## Locations to Apply

### SimulationEngine.run() - TOP PRIORITY

The main loop must never die silently:

```python
# In run() main loop
while self.turn < self.max_turns:
    try:
        self._execute_turn(...)
    except Exception as e:
        self._log.error("execute_turn_failed", turn=self.turn, error=str(e), error_type=type(e).__name__)
        self._running = False
        raise

# Finale
try:
    finale_data = self._generate_finale()
    self._notify("on_finale", finale_data)
except Exception as e:
    self._log.error("finale_generation_failed", error=str(e))
    finale_data = {"error": str(e)}
```

### _save_snapshot()

```python
def _save_snapshot(self, world: World, turn: int) -> str:
    try:
        path = self.snapshots_dir / f"snapshot_{turn:05d}.json"
        with open(path, "w") as f:
            json.dump(world.model_dump(mode="json"), f, indent=2)
        return str(path)
    except Exception as e:
        self._log.error("snapshot_failed", turn=turn, error=str(e), error_type=type(e).__name__)
        raise
```

### _get_player_action()

```python
def _get_player_action(self, echo):
    try:
        available_actions = list(ACTION_CLASSES.keys())
        action_name = self._player.select_action(self.turn, self.world, available_actions)
        self._log.debug("get_action", turn=self.turn, action_name=action_name)
        if action_name:
            self._notify("on_action_selected", self.turn, action_name)
        return action_name
    except Exception as e:
        self._log.error("get_player_action_failed", turn=self.turn, error=str(e), error_type=type(e).__name__)
        raise
```

### _execute_player_action()

```python
def _execute_player_action(self, echo, action_name, should_deal_damage_fn):
    try:
        # ... existing code ...
    except Exception as e:
        self._log.error("execute_player_action_failed", turn=self.turn, action=action_name, error=str(e), error_type=type(e).__name__)
        raise
```

### Threaded Adapters

For TUI and other threaded adapters:

```python
def _run_engine(self) -> None:
    if self._engine:
        try:
            self._engine.run()
            self._game_over = True
            log.info("engine_finished", turns=self._engine.turn)
        except Exception as e:
            log.error("engine_thread_crash", error=str(e), error_type=type(e).__name__)
            self._game_over = True  # Signal main thread
            raise
```

### Processors (npc_processor, circle_processor, etc.)

```python
def process_npc_turns(...):
    try:
        # ... existing code ...
    except Exception as e:
        log.error("process_npc_turns_failed", turn=turn, error=str(e), error_type=type(e).__name__)
        raise
```

## Log Format

All error logs MUST include:
- `error`: The exception message as string
- `error_type`: The exception class name
- Context fields (turn, action, etc.)

Optional for debugging:
- `error_details`: Full traceback string (use `traceback.format_exc()`)

## Anti-Patterns to Avoid

1. **Silent except**: `except:` without logging
2. **Bare except + pass**: `except: pass` (swallows all errors)
3. **except Exception + return None**: Without logging, makes debugging hard
4. **Logging and not re-raising**: Only for non-critical failures

## Testing

Add test `test_engine_never_dies_silently` that:
1. Mocks a method to raise an exception
2. Verifies exception is logged
3. Verifies error_type is in log output

## References

- Related: `specs/53-logger.md` for logging conventions
- Related: `specs/01-architecture.md` for engine architecture
