# 54 - Adapter Core Architecture

**Estado:** draft
**Fecha:** 2026-05-26
**Dependencias:** 01, 02, 07, 08, 33, 36

---

## 1. Motivation

### 1.1 Problem

Currently, `game_core.simulation.SimulationEngine` has direct coupling to input sources:

```python
# simulation.py (current)
if input_source is not None:
    self.input_source = input_source
else:
    from player_core import create_input_source
    self.input_source = create_input_source(autoplay=self.autoplay)
```

This creates tight coupling:
- Human input → UI dependencies
- AI autoplay → embedded in engine
- NPCs → handled differently
- Multiplayer → not possible

### 1.2 Goal

Enable:
- Human players via TUI/CLI
- AI players via LLM adapters
- Network/multiplayer players
- NPC agents connected to AI backends
- Any combination of the above

---

## 2. Architecture Overview

### 2.1 Hexagonal Architecture (Ports and Adapters)

```
┌─────────────────────────────────────────────────────────────────┐
│                         game_core                                │
│                                                                 │
│  ┌─────────────┐    ┌──────────────┐    ┌───────────────┐   │
│  │  Simulation │    │  World State │    │   Entities    │   │
│  │   Engine   │◄──►│   (pure)     │◄──►│  (Echo,Circle │   │
│  │             │    │              │    │   ,Person...)  │   │
│  └─────────────┘    └──────────────┘    └───────────────┘   │
│         ▲                                                           │
│         │ Events/Commands                                         │
│         │                                                           │
└─────────┼─────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      adapter_core                               │
│                                                                 │
│  ┌─────────────────┐         ┌─────────────────┐             │
│  │   GameAdapter   │◄────────│  InputSource    │             │
│  │   (port/interface)      │   (strategy)     │             │
│  └─────────────────┘         └─────────────────┘             │
│          │                                                           │
│          ├──────────────────┬──────────────────┬──────────────┤
│          ▼                  ▼                  ▼              ▼      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐
│  │   Human    │  │    AI     │  │  Network   │  │    NPC    │
│  │  Adapter   │  │  Adapter  │  │  Adapter   │  │  Adapter  │
│  └────────────┘  └────────────┘  └────────────┘  └──────────┘
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

```
Turn N:
  1. SimulationEngine → emits WorldStateEvent to all adapters
  2. Each adapter processes events independently
  3. Adapter calls engine.execute_action(action)
  4. Engine processes action → notifies observers
  5. World metrics evolve
  6. Repeat
```

---

## 3. Core Interfaces

### 3.1 InputSource (Strategy Pattern)

```python
class InputSource(ABC):
    """Strategy for obtaining player/NPC decisions."""
    
    @abstractmethod
    def get_action(self, turn: int, world: World) -> str | None:
        """
        Returns action name (e.g., 'found_circle') or None for no action.
        Called by GameAdapter when it needs a decision.
        """
        ...
    
    @property
    @abstractmethod
    def mode(self) -> str:
        """Returns: 'player' | 'autoplay' | 'hybrid'"""
        ...
    
    def supports_realtime_override(self) -> bool:
        return False
    
    def inject_action(self, action: str) -> None:
        """For TUI: inject action mid-turn."""
        raise NotImplementedError
```

**Existing implementations:**
- `PlayerInputSource` - human via Selector/TUI
- `AutoplayInputSource` - always returns None (autoplay fallback)
- `HybridInputSource` - mixed mode

### 3.2 GameAdapter (Port/Interface)

```python
class GameAdapter(ABC):
    """
    Main entry point for game control.
    Owns the connection to the simulation engine.
    Receives events, sends commands.
    """
    
    def __init__(self, input_source: InputSource):
        self._input_source = input_source
        self._engine: SimulationEngine | None = None
        self._running = False
    
    @abstractmethod
    def connect(self, engine: SimulationEngine) -> None:
        """Connect this adapter to a simulation engine."""
        ...
    
    @abstractmethod
    def on_world_state(self, turn: int, world_state: dict) -> None:
        """Called when engine sends world state."""
        ...
    
    @abstractmethod
    def on_event(self, event_type: str, data: dict) -> None:
        """Called when engine sends an event (crisis, echo_spawned, etc)."""
        ...
    
    @abstractmethod
    def on_action_result(self, turn: int, action: str, success: bool, message: str) -> None:
        """Called when player's action completes."""
        ...
    
    @abstractmethod
    def get_action(self, turn: int) -> str | None:
        """
        Request a decision from the underlying InputSource.
        Adapter can intercept/transform/reject.
        """
        return self._input_source.get_action(turn, self._engine.world)
    
    @abstractmethod
    def start(self) -> None:
        """Begin the game loop."""
        ...
    
    @abstractmethod
    def stop(self) -> None:
        """Stop the game loop."""
        ...
```

### 3.3 Relationship

```
GameAdapter owns InputSource
       │
       ├── has a reference to SimulationEngine
       ├── receives all events from engine
       ├── decides when to request actions from InputSource
       └── can transform/modify/filter before sending to engine
```

---

## 4. Concrete Adapters

### 4.1 HumanGameAdapter

```python
class HumanGameAdapter(GameAdapter):
    """
    Adapter for human players via TUI.
    InputSource: PlayerInputSource
    """
    
    def __init__(self, selector: Selector):
        super().__init__(PlayerInputSource(selector=selector))
        self._ui_callbacks: list[Callable] = []
    
    def on_world_state(self, turn: int, world_state: dict):
        # Update UI
        self._ui.refresh(world_state)
    
    def on_event(self, event_type: str, data: dict):
        # Display event in UI
        self._ui.display_event(event_type, data)
    
    def get_action(self, turn: int) -> str | None:
        # Request action from player
        action = self._input_source.get_action(turn, self._engine.world)
        if action:
            self._engine.execute_action(turn, action)
        return action
```

### 4.2 AIGameAdapter

```python
class AIGameAdapter(GameAdapter):
    """
    Adapter for AI-controlled players (LLM backend).
    InputSource: AutoplayInputSource (AI decides internally)
    """
    
    def __init__(self, ai_backend: "AIBackend", style: str = "balanced"):
        super().__init__(AutoplayInputSource())
        self._ai = ai_backend
        self._style = style
        self._pending_decision = None
    
    def on_world_state(self, turn: int, world_state: dict):
        # AI processes world state asynchronously
        self._ai.analyze(world_state)
    
    def on_event(self, event_type: str, data: dict):
        # AI generates response to event
        self._ai.process_event(event_type, data)
    
    def get_action(self, turn: int) -> str | None:
        # AI generates action based on current analysis
        action = self._ai.decide_action(turn, self._engine.world)
        if action:
            self._engine.execute_action(turn, action)
        return action
```

### 4.3 NetworkGameAdapter

```python
class NetworkGameAdapter(GameAdapter):
    """
    Adapter for multiplayer - receives actions from network.
    InputSource: reads from network socket/queue
    """
    
    def __init__(self, host: str, port: int):
        super().__init__(NetworkInputSource(host, port))
        self._players: dict[int, PlayerInfo] = {}
    
    def on_world_state(self, turn: int, world_state: dict):
        # Broadcast state to all network players
        self._network.broadcast({
            "type": "world_state",
            "turn": turn,
            "state": world_state
        })
```

### 4.4 NPCGameAdapter

```python
class NPCGameAdapter(GameAdapter):
    """
    Adapter for NPC agents - connects to AI backend.
    Multiple NPCs can share one adapter, each with own AI instance.
    """
    
    def __init__(self, npc_id: str, ai_backend: "AIBackend"):
        super().__init__(AutoplayInputSource())
        self._npc_id = npc_id
        self._ai = ai_backend
```

---

## 5. Engine Changes

### 5.1 Current Flow

```
SimulationEngine.run()
    ├── loop: turn < max_turns
    │   ├── advance_clock()
    │   ├── notify("on_turn_start")
    │   ├── get_action() ← InputSource
    │   ├── execute_action()
    │   ├── evolve_metrics()
    │   ├── notify("on_turn_end")
    │   └── loop
    └── return result
```

### 5.2 New Flow (with Adapter)

```
# Old: Engine owned the loop
SimulationEngine.run()

# New: Adapter owns the loop
Adapter.start()
    ├── while _running:
    │   ├── engine.turn_start()
    │   ├── world_state = engine.get_world_state()
    │   ├── adapter.on_world_state(turn, world_state)
    │   ├── action = adapter.get_action(turn)
    │   ├── if action: engine.execute_action(action)
    │   ├── engine.turn_end()
    │   └── check termination
    └── cleanup
```

### 5.3 SimulationEngine API Additions

```python
class SimulationEngine:
    def turn_start(self) -> dict:
        """Begin turn, return world state for adapters."""
        self.turn += 1
        self.world.clock.advance(1)
        self._notify("on_turn_start", self.turn, self.world)
        return self._serialize_world()
    
    def turn_end(self) -> None:
        """End current turn."""
        self._notify("on_turn_end", self.turn, self.world, self._last_action)
        self.world.evolve_metrics(self.rng)
    
    def execute_action(self, turn: int, action_name: str) -> ActionResult:
        """Execute an action (called by adapter)."""
        ...
    
    def get_world_state(self) -> dict:
        """Return current world state for adapters."""
        return self._serialize_world()
    
    def is_running(self) -> bool:
        """Check if simulation is active."""
        return self._running
    
    def stop(self) -> None:
        """Signal simulation to stop."""
        self._running = False
```

---

## 6. Event Protocol

### 6.1 Events from Engine → Adapter

| Event | Payload | Description |
|-------|---------|-------------|
| `world_state` | `{turn, pressure, legitimacy, resources, ...}` | Full state snapshot |
| `action_result` | `{turn, action, success, message}` | Player action outcome |
| `event` | `{turn, title, summary}` | World event (crisis, discovery) |
| `echo_spawned` | `{parent, daughter}` | Reincarnation |
| `crisis` | `{metric, value}` | Crisis triggered |

### 6.2 Commands from Adapter → Engine

| Command | Payload | Description |
|--------|---------|-------------|
| `action` | `{turn, action}` | Player chose an action |
| `quit` | `{}` | End simulation |

---

## 7. Usage Examples

### 7.1 Single Human Player

```python
from adapter_core import HumanGameAdapter
from ui_core.textual import EcoTextualApp

engine = SimulationEngine(max_turns=100)
adapter = HumanGameAdapter(selector)

adapter.connect(engine)
adapter.start()  # Blocks until game ends
```

### 7.2 AI vs Human (2 adapters?)

```python
# Not supported yet - needs multi-adapter support
# Future: adapter_for_player_1, adapter_for_player_2
```

### 7.3 AI Autoplay

```python
from adapter_core import AIGameAdapter
from game_core.ai import MiniMaxAdapter

backend = MiniMaxAdapter(model="MiniMax-Text-01")
adapter = AIGameAdapter(ai_backend=backend, style="revolutionary")

adapter.connect(engine)
adapter.start()
```

---

## 8. Directory Structure

```
eco/
├── adapter_core/
│   ├── __init__.py          # exports GameAdapter, etc
│   ├── base.py              # GameAdapter ABC
│   ├── human.py             # HumanGameAdapter
│   ├── ai.py                # AIGameAdapter  
│   ├── network.py           # NetworkGameAdapter
│   ├── npc.py               # NPCGameAdapter
│   └── input_source/        # (existing player_core.modes becomes this)
│       ├── __init__.py
│       ├── base.py          # InputSource ABC
│       ├── player.py
│       ├── autoplay.py
│       └── hybrid.py
├── game_core/
│   └── systems/
│       └── simulation.py    # Refactored to not import player_core
```

---

## 9. Migration Plan

### Phase 1: Extract adapter_core from player_core
- Rename `player_core` → `adapter_core.input_source`
- Create `adapter_core.base.GameAdapter`
- Test: existing human player still works

### Phase 2: Refactor SimulationEngine
- Add `turn_start()`, `turn_end()`, `execute_action()` methods
- Remove direct `input_source.get_action()` call
- Test: engine runs without input source

### Phase 3: Implement HumanGameAdapter
- Connect TUI to new adapter
- Test: TUI displays events correctly

### Phase 4: Implement AIGameAdapter
- Connect AI backend to adapter
- Test: AI can play game

### Phase 5: (Future) Multi-adapter support
- Multiple players
- Network multiplayer

---

## 10. Open Questions

1. **Who owns the game loop?** Adapter owns it (recommended) vs Engine owns it
2. **Synchronous vs Async?** Currently synchronous. Async needed for network.
3. **Multiple adapters?** Single player now, multiplayer later.
4. **State ownership?** Engine has canonical state. Adapters have local caches.

---

## 11. Status

- [x] Architecture designed
- [ ] SPEC approved
- [ ] Phase 1: Extract adapter_core
- [ ] Phase 2: Refactor SimulationEngine
- [ ] Phase 3: HumanGameAdapter
- [ ] Phase 4: AIGameAdapter
