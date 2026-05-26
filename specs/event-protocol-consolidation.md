# SPEC: Event Protocol Consolidation

## Problem

Currently, adding a new event type requires changes in 4 places:
1. `SimulationObserver` - define the event method
2. `ProtocolObserver` - implement and convert to protocol message
3. `messages.py` - define the protocol message class
4. `codec.py` - add decode logic

This violates DRY and makes adding events tedious and error-prone.

## Solution

Create a unified event system where:

1. **`SimulationObserver`** defines events with typed data classes
2. **Each observer method returns a `ProtocolEvent`** (or None)
3. **`ProtocolObserver`** re-emits these events to the protocol
4. **`messages.py`** uses the same typed events (no duplication)

## Architecture

### Event Flow
```
SimulationEngine
    ↓ notifies
SimulationObserver.on_*()
    ↓ returns
ProtocolEvent (data class with to_dict())
    ↓ ProtocolObserver._emit()
Protocol (JSON via stdin/stdout)
    ↓ TUI app receives
_display_
```

### Key Design

- `SimulationObserver.on_*()` methods return `ProtocolEvent | None`
- Events are just data classes with a `to_dict()` method
- `ProtocolObserver.on_*()` methods delegate to `_emit(event)` for simple events
- Custom handling only needed for events that aggregate data (like world_state)

### Benefits

- Adding a new event = add one data class + one observer method
- No duplication between observer and protocol
- Type-safe event handling
- Easy to test events in isolation

## Changes

### messages.py
- Keep `ActionCommand`, `QueryCommand`, `QuitCommand` (CLI commands from TUI)
- Keep `MessageType` enum
- All simulation events become `ProtocolEvent` subclasses

### observer.py
- Events return `ProtocolEvent | None`
- Generic `on_event(turn, event_type, data)` for extensibility

### ProtocolObserver
- Simple events: `self._emit(event)` where event is already a ProtocolEvent
- Complex events (world_state): manual handling

## Example: Adding NPC_ACTION

**Before (4 files):**
```python
# observer.py
def on_npc_action(self, turn, npc_name, action, message): ...

# cli.py
def on_npc_action(self, turn, npc_name, action, message):
    self._emit(NPcActionEvent(...))  # duplicate fields!

# messages.py
class NPcActionEvent: ...  # duplicate of on_npc_action params!

# codec.py
elif mt == NPC_ACTION: return NPcActionEvent(...)  # duplicate decode!
```

**After (1 file):**
```python
# observer.py
@dataclass
class NpcActionEvent(ProtocolEvent):
    npc_name: str
    action: str
    message: str

    def on_turn_start(self, turn: int, npc_name: str, action: str, message: str):
        return NpcActionEvent(turn=turn, npc_name=npc_name, action=action, message=message)
```
