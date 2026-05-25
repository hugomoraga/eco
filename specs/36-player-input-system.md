# 36 - Player Input System

**Estado:** draft  
**Fecha:** 2026-05-24  
**Dependencias:** 01, 02, 07, 24  

---

## 1. Contexto

Actualmente simulation solo tiene autoplay. El jugador no puede intervenir ni jugar. Este spec implementa un sistema de input que permite tres modos: autoplay, hybrid, y player.

El sistema es agnóstico de UI — TUI consume las mismas interfaces después.

---

## 2. Modos de Input

```
MODOS:
━━━━━━

AUTOPLAY (ECO_INPUT_MODE=autoplay)
  → AutoplayerEngine siempre decide
  → No hay intervención de jugador
  → Default behavior (backwards compatible)
  → .env: ECO_INPUT_MODE=autoplay

HYBRID (ECO_INPUT_MODE=hybrid)
  → Autoplay por defecto
  → Cada N turns (ECO_INTERACTIVE_TURNS), simulation pausa y pide input
  → Jugador puede: elegir acción, o delegar a autoplay
  → Puede intervenir en cualquier momento via flag
  → .env: ECO_INPUT_MODE=hybrid, ECO_INTERACTIVE_TURNS=5

PLAYER (ECO_INPUT_MODE=player)
  → Cada turno pregunta al jugador
  → Input requerido (fallback: autoplay si no responde o timeout)
  → .env: ECO_INPUT_MODE=player
```

---

## 3. Architecture

```
INPUT SOURCE INTERFACE:
━━━━━━━━━━━━━━━━━━━━━━━━

                    ┌─────────────────────┐
                    │   InputSource (ABC) │
                    │  ─────────────────  │
                    │ +get_action()       │
                    │ +mode()             │
                    │ +supports_realtime()│
                    └─────────┬───────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
    ┌─────┴─────┐       ┌─────┴─────┐       ┌─────┴─────┐
    │ Autoplay  │       │  Hybrid   │       │  Player   │
    │InputSource│       │InputSource│       │InputSource│
    └───────────┘       └───────────┘       └───────────┘
```

```python
from abc import ABC, abstractmethod

class InputSource(ABC):
    """Abstract base class for player input sources."""
    
    @abstractmethod
    def get_action(self, turn: int, world: World) -> str | None:
        """
        Returns action name (e.g., "found_circle", "write_manifesto")
        or None for autoplay fallback.
        """
        pass
    
    @property
    @abstractmethod
    def mode(self) -> str:
        """Returns: 'autoplay' | 'hybrid' | 'player'"""
        pass
    
    def supports_realtime_override(self) -> bool:
        """Whether input can be injected mid-simulation (for TUI)."""
        return False
    
    def inject_action(self, action: str) -> None:
        """TUI calls this to inject player action."""
        raise NotImplementedError
```

---

## 4. AutoplayInputSource

```python
class AutoplayInputSource(InputSource):
    """Full autoplay — never asks for player input."""
    
    @property
    def mode(self) -> str:
        return "autoplay"
    
    def get_action(self, turn: int, world: World) -> str | None:
        return None  # Always delegate to autoplay
```

---

## 5. HybridInputSource

```python
class HybridInputSource(InputSource):
    """
    Hybrid mode: autoplay by default, interactive at intervals.
    Player can also take control at any time.
    """
    
    def __init__(self, interactive_turns: int = 5):
        self.interactive_turns = interactive_turns
        self._player_override = False
        self._pending_action: str | None = None
    
    @property
    def mode(self) -> str:
        return "hybrid"
    
    def supports_realtime_override(self) -> bool:
        return True
    
    def get_action(self, turn: int, world: World) -> str | None:
        # Check for injected action from TUI
        if self._pending_action is not None:
            action = self._pending_action
            self._pending_action = None
            return action
        
        # Check for player override
        if self._player_override:
            self._player_override = False
            return self._request_player_input(turn, world)
        
        # Periodic interactive turn
        if turn % self.interactive_turns == 0:
            return self._request_player_input(turn, world)
        
        return None  # Autoplay fallback
    
    def inject_action(self, action: str) -> None:
        """Called by TUI to force player input this turn."""
        self._player_override = True
        self._pending_action = action
    
    def player_take_control(self) -> None:
        """Explicit player request to take control."""
        self._player_override = True
    
    def _request_player_input(self, turn: int, world: World) -> str | None:
        """CLI prompt for player decision."""
        # Shows world state, asks for action
        # Returns action or None for autoplay
        pass
```

---

## 6. PlayerInputSource

```python
class PlayerInputSource(InputSource):
    """
    Player mode: always asks for input.
    No autoplay unless player explicitly chooses it or times out.
    """
    
    def __init__(self, timeout_seconds: int = 30):
        self.timeout_seconds = timeout_seconds
        self._pending_action: str | None = None
    
    @property
    def mode(self) -> str:
        return "player"
    
    def supports_realtime_override(self) -> bool:
        return True
    
    def get_action(self, turn: int, world: World) -> str | None:
        # Check for injected action from TUI
        if self._pending_action is not None:
            action = self._pending_action
            self._pending_action = None
            return action
        
        return self._request_player_input(turn, world)
    
    def inject_action(self, action: str) -> None:
        """Called by TUI to inject action."""
        self._pending_action = action
    
    def _request_player_input(self, turn: int, world: World) -> str | None:
        """CLI prompt — always required, waits for input."""
        # If no input after timeout, use fallback (autoplay)
        # Player can type "autoplay" to explicitly delegate
        pass
```

---

## 7. CLI Input (Shared)

Both Hybrid and Player use shared CLI input logic:

```python
def _show_world_state(self, turn: int, world: World) -> None:
    """Display current world state for player decision."""
    print(f"\n{'='*50}")
    print(f"TURN {turn} — WORLD STATE")
    print(f"{'='*50}")
    print(f"Pressure: {world.pressure:.1f} | Legitimacy: {world.legitimacy:.1f}")
    print(f"Resources: {world.resources:.1f}")
    print(f"Circles: {len(world.circles)} | Echoes: {len(world.echoes)}")
    
    if world.active_events:
        print(f"Recent events: {[e.title for e in world.active_events[-3:]]}")
    
    print(f"\nYour circles: {[c.name for c in world.circles if echo_id in c.members]}")
    print(f"{'='*50}")

def _show_available_actions(self) -> None:
    """Display available actions."""
    print("\nAVAILABLE ACTIONS:")
    print("  1. found_circle   — Create new circle")
    print("  2. write_manifesto — Write ideas to world")
    print("  3. propagate_idea  — Spread ideas to factions")
    print("  4. talk           — Speak with NPC or Echo")
    print("  5. sabotage       — Sabotage faction infrastructure")
    print("  6. ritualize      — Perform ritual")

def _parse_action_input(self, choice: str) -> str | None:
    """Parse player input to action name."""
    actions_map = {
        "1": "found_circle",
        "2": "write_manifesto",
        "3": "propagate_idea",
        "4": "talk",
        "5": "sabotage",
        "6": "ritualize",
        "found_circle": "found_circle",
        "write_manifesto": "write_manifesto",
        "propagate_idea": "propagate_idea",
        "talk": "talk",
        "sabotage": "sabotage",
        "ritualize": "ritualize",
        "autoplay": None,  # Explicit delegation
        "": None,          # Empty = autoplay (hybrid only)
    }
    return actions_map.get(choice.strip().lower())
```

---

## 8. Factory

```python
# game_core/input/factory.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import os

def create_input_source() -> InputSource:
    """
    Factory to create input source based on .env configuration.
    
    ECO_INPUT_MODE: autoplay | hybrid | player (default: autoplay)
    ECO_INTERACTIVE_TURNS: N for hybrid mode (default: 5)
    """
    mode = os.getenv("ECO_INPUT_MODE", "autoplay")
    
    if mode == "player":
        from game_core.input.player import PlayerInputSource
        return PlayerInputSource()
    
    elif mode == "hybrid":
        from game_core.input.hybrid import HybridInputSource
        turns = int(os.getenv("ECO_INTERACTIVE_TURNS", "5"))
        return HybridInputSource(interactive_turns=turns)
    
    else:  # autoplay
        from game_core.input.autoplay import AutoplayInputSource
        return AutoplayInputSource()
```

---

## 9. Integration with Simulation

```python
# game_core/engine/simulation.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

from game_core.input import create_input_source

class SimulationEngine:
    def __init__(self, ...):
        self.input_source = create_input_source()
        ...
    
    def run(self, max_turns: int):
        for turn in range(1, max_turns + 1):
            # Get action from input source
            action_name = self.input_source.get_action(turn, self.world)
            
            if action_name is None:
                # Autoplay fallback
                action_name = self.autoplayer.choose_action(turn, self.world)
            
            # Execute action
            self.execute_action(action_name, turn)
            
            # World tick
            self.world_tick()
```

---

## 10. File Structure

```
game_core/input/
├── __init__.py
├── base.py          # InputSource ABC
├── autoplay.py      # AutoplayInputSource
├── hybrid.py        # HybridInputSource
├── player.py        # PlayerInputSource
└── factory.py       # create_input_source()
```

---

## 11. Environment Variables

```bash
# .env
ECO_INPUT_MODE=autoplay        # autoplay | hybrid | player
ECO_INTERACTIVE_TURNS=5         # Only for hybrid mode
```

---

## 12. Testing

```bash
# Autoplay (default, backwards compatible)
ECO_INPUT_MODE=autoplay uv run python game_core/run.py --seed 42 --turns 20

# Hybrid, asks every 5 turns
ECO_INPUT_MODE=hybrid ECO_INTERACTIVE_TURNS=5 uv run python game_core/run.py --seed 42 --turns 20

# Player, always asks (timeout fallback to autoplay)
ECO_INPUT_MODE=player uv run python game_core/run.py --seed 42 --turns 20
```

---

## 13. TUI Integration

After this spec, TUI will use the same InputSource interface:

```python
class TuiInputSource(InputSource):
    """TUI captures player input and injects via inject_action()."""
    
    def __init__(self):
        self._queue = queue.Queue()
    
    def get_action(self, turn, world):
        # Check queue first (injected from TUI)
        if not self._queue.empty():
            return self._queue.get_nowait()
        
        # If no TUI input, check if player wants autoplay
        return self._check_tui_input()
    
    def inject_action(self, action: str):
        """TUI calls this to inject player action."""
        self._queue.put(action)
    
    def supports_realtime_override(self) -> bool:
        return True
```

The InputSource interface is designed so TUI can sit on top without modifying simulation.

---

## 14. Dependencies

- **spec-24:** Configuration via .env (ECO_INPUT_MODE, ECO_INTERACTIVE_TURNS)
- **spec-33:** Console output (for CLI prompts)
- **simulation.py:** Uses InputSource to get actions

---

## 15. Status History

- 2026-05-24: draft created