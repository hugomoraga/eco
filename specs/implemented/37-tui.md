# Spec 37: ECO Game Interface — rich + prompt_toolkit

## Status
- **created**: 2024-05-24
- **stage**: deprecated
- **replaces**: spec-33 (colors), spec-41 (interactive menu)
- **replaced by**: [spec-43](../43-ui.md)

---

## Deprecación

Este spec contenía el diseño original de ui_core/ con rich + prompt_toolkit. Fue incorporado y mejorado en [spec-43](../43-ui.md) que es la fuente de verdad actual.

Las secciones de código que defined aquí fueron movidas a `ui_core/` (ya implementado).

## Goal

Reemplazar el sistema de display/input actual (que usa blessed y tiene bugs en macOS) con `rich` + `prompt_toolkit` para tener una interfaz de agente real donde el jugador pueda:

- **Navegar** con selectores (flechas + enter)
- **Ejecutar comandos** tipo REPL
- **Ver replay** de acciones pasadas
- **Guardar/cargar partidas**
- **Volver a jugar** desde el menú

Inspirado en Hermes Agent CLI.

## Dependencies
- spec-01 (architecture)
- spec-19 (mvp-implementation)

## Libraries

### prompt_toolkit
- **Uso**: Input interactivo (selectores, prompts, historial)
- **Docs**: https://python-prompt-toolkit.readthedocs.io/
- **Instalación**: `prompt_toolkit==3.0.52`

### rich
- **Uso**: Output formateado (colores, tablas, panels, layouts)
- **Docs**: https://rich.readthedocs.io/
- **Instalación**: `rich==14.3.3`

## Architecture

```
game_core/
├── interface/                  # Nuevo paquete
│   ├── __init__.py
│   ├── console.py              # Rich Console singleton
│   ├── styles.py               # Colores y estilos predefinidos
│   ├── components.py           # Widgets reutilizables (panels, tables)
│   ├── selector.py             # Selectores con flechas
│   ├── input.py                # Input helpers (comandos, prompts)
│   ├── history.py              # Historial de acciones + replay
│   └── session.py              # Guardar/cargar partida
│
└── run.py                      # Entry point usa interface/
```

## Components

### 1. console.py — Rich Console singleton

```python
from rich.console import Console as RichConsole
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.live import Live

class Console:
    _instance = None

    def __init__(self):
        self._console = RichConsole()
        self._live: Live | None = None

    @classmethod
    def get(cls) -> "Console":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # --- Layout helpers ---

    def print(self, *args, **kwargs):
        self._console.print(*args, **kwargs)

    def print_panel(self, content: str | Text, title: str = "", border_style: str = "green"):
        self._console.print(Panel(content, title=title, border_style=border_style))

    def print_table(self, title: str, rows: list[list[str]], columns: list[str]):
        table = Table(title=title)
        for col in columns:
            table.add_column(col)
        for row in rows:
            table.add_row(*row)
        self._console.print(table)

    def print_divider(self, char="─", color="cyan"):
        self._console.print(f"[{color}]{char * 60}[/{color}]")

    def clear(self):
        self._console.clear()

    # --- Live mode (updatable display) ---

    def start_live(self, renderable):
        self._live = Live(renderable, console=self._console, refresh_per_second=4)
        self._live.start()

    def update_live(self, renderable):
        if self._live:
            self._live.update(renderable)

    def stop_live(self):
        if self._live:
            self._live.stop()
            self._live = None
```

### 2. styles.py — Colores y estilos

```python
from rich.style import Style

# Paleta ECO
CYAN = "#00D4FF"
YELLOW = "#FFD700"
GREEN = "#00FF88"
RED = "#FF4444"
MAGENTA = "#FF00FF"
GRAY = "#666666"
WHITE = "#FFFFFF"

# Estilos reutilizables
STYLES = {
    "header": Style(color=CYAN, bold=True),
    "title": Style(color=YELLOW, bold=True),
    "success": Style(color=GREEN),
    "warning": Style(color=YELLOW),
    "error": Style(color=RED, bold=True),
    "dim": Style(color=GRAY, dim=True),
    "info": Style(color=MAGENTA),
    "metric_positive": Style(color=GREEN, bold=True),
    "metric_negative": Style(color=RED, bold=True),
    "action": Style(color=CYAN),
    "prompt": Style(color=WHITE, bold=True),
    "echo": Style(color=GREEN, italic=True),
    "circle": Style(color=YELLOW),
    "faction": Style(color=MAGENTA),
}

def s(name: str) -> Style:
    """Get style by name."""
    return STYLES.get(name, Style.empty())
```

### 3. components.py — Widgets reutilizables

```python
from rich.text import Text
from .styles import s, CYAN, YELLOW, GREEN, RED

class Components:
    @staticmethod
    def turn_header(turn: int) -> Text:
        return Text.assemble(
            (f"═══ TURN {turn:03d} ═══", s("header"))
        )

    @staticmethod
    def world_metrics_table(metrics: dict) -> Table:
        """Build world state table."""
        from rich.table import Table
        table = Table(title="Estado del Mundo", border_style=CYAN)
        table.add_column("Métrica", style="cyan")
        table.add_column("Valor", style="magenta")
        table.add_column("Δ", style="")

        for key, value in metrics.items():
            # Color based on value type
            if "pressure" in key.lower() or "unrest" in key.lower():
                style = "metric_positive" if value > 0.7 else "metric_negative" if value < 0.3 else ""
            elif "legitimacy" in key.lower() or "resources" in key.lower():
                style = "metric_positive" if value > 0.5 else "metric_negative"
            else:
                style = ""
            table.add_row(key, f"{value:.2f}", "")

        return table

    @staticmethod
    def event_banner(event_type: str, title: str, summary: str = "") -> Panel:
        emoji_map = {
            "crisis": "⚠️",
            "opportunity": "✨",
            "echo_created": "🌱",
            "circle_founded": "⭕",
            "faction_formed": "🔱",
            "sabotage": "💥",
            "ritual": "🔮",
        }
        emoji = emoji_map.get(event_type, "📢")
        content = f"[bold]{emoji} {title}[/bold]"
        if summary:
            content += f"\n[dim]{summary}[/dim]"

        border = {"crisis": "red", "opportunity": "green"}.get(event_type, "yellow")
        return Panel(content, border_style=border)

    @staticmethod
    def action_result(action: str, result: str, success: bool = True) -> Text:
        icon = "✓" if success else "✗"
        color = "success" if success else "error"
        return Text.assemble(
            (f"{icon} ", s(color)),
            (action, s("action")),
            (f": {result}", "")
        )
```

### 4. selector.py — Selectores con flechas

```python
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import Window, HSplit
from prompt_toolkit.widgets import CheckboxList, RadioList
from prompt_toolkit.styles import Style
from rich.text import Text

class Selector:
    """Selection menu with arrow keys + enter."""

    def __init__(self, title: str, options: list[str], format_func=None):
        self.title = title
        self.options = options
        self.format_func = format_func or (lambda x: x)
        self.selected = 0
        self._result = None

    def _build_ui(self):
        """Build the selector UI."""
        from prompt_toolkit.widgets import Label
        from prompt_toolkit.layout.containers import VSplit, WindowAlign

        lines = []
        lines.append(f"  {self.title}  ")
        lines.append("  " + "─" * 40)

        for i, opt in enumerate(self.options):
            marker = "▶" if i == self.selected else " "
            prefix = f"[cyan]{marker}[/cyan]" if i == self.selected else "  "
            text = self.format_func(opt)
            lines.append(f"{prefix} {text}")

        lines.append("")
        lines.append("[dim]↑↓ navegar · Enter seleccionar · q cancelar[/dim]")

        return Text("\n".join(lines))

    def run(self) -> str | None:
        """Run selector. Returns selected option or None if cancelled."""
        from prompt_toolkit import PromptSession
        from prompt_toolkit.keys import Keys
        from prompt_toolkit.input import Input
        from prompt_toolkit.output import Output

        kb = KeyBindings()

        @kb.add("c-c", eager=True)
        def cancel(event):
            self._result = None
            event.app.exit()

        @kb.add("q", eager=True)
        def quit(event):
            self._result = None
            event.app.exit()

        @kb.add("s", eager=True)
        @kb.add(Keys.Down)
        def down(event):
            self.selected = (self.selected + 1) % len(self.options)

        @kb.add("w", eager=True)
        @kb.add(Keys.Up)
        def up(event):
            self.selected = (self.selected - 1) % len(self.options)

        @kb.add(Keys.Enter, eager=True)
        def select(event):
            self._result = self.options[self.selected]
            event.app.exit()

        from prompt_toolkit.application import Application
        app = Application(
            layout=Layout(),
            key_bindings=kb,
            render=self._build_ui,
        )
        app.run()

        return self._result
```

### 5. input.py — Comandos y prompts

```python
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory

class CommandInput:
    """REPL-style command input with history."""

    _session: PromptSession | None = None

    @classmethod
    def get_session(cls) -> PromptSession:
        if cls._session is None:
            cls._session = PromptSession(
                history=InMemoryHistory(),
                vi_mode=False,
                enable_history_search=True,
                message="► ",
            )
        return cls._session

    @classmethod
    def get_command(cls, prompt: str = "► ") -> str:
        """Get single line command."""
        session = cls.get_session()
        try:
            return session.prompt(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            return ""

    @classmethod
    def get_number(cls, prompt: str = "► ") -> int | None:
        """Get numeric input. Returns None for non-numeric."""
        cmd = cls.get_command(prompt)
        try:
            return int(cmd)
        except ValueError:
            return None

    @classmethod
    def get_choice(cls, options: list[str], prompt: str = "► ") -> int | None:
        """Get choice by number (1-indexed). Returns None for empty."""
        cmd = cls.get_command(prompt)
        if not cmd:
            return None
        try:
            idx = int(cmd) - 1
            if 0 <= idx < len(options):
                return idx
        except ValueError:
            pass
        return None

# Command registry for REPL
COMMANDS = {}

def command(name: str):
    """Decorator to register a command handler."""
    def decorator(func):
        COMMANDS[name] = func
        return func
    return decorator

@command("help")
def cmd_help(interface, args):
    """Show available commands."""
    lines = ["[cyan]Comandos disponibles:[/cyan]", ""]
    for name, func in COMMANDS.items():
        doc = func.__doc__ or ""
        lines.append(f"  [yellow]{name}[/yellow] — {doc.strip()}")
    return "\n".join(lines)

@command("history")
def cmd_history(interface, args):
    """Show action history."""
    return interface.history.format()

@command("replay")
def cmd_replay(interface, args):
    """Replay last N actions."""
    try:
        n = int(args[0]) if args else 1
    except ValueError:
        return "[red]Uso: replay [n][/red]"
    return interface.history.replay(n)

@command("quit")
def cmd_quit(interface, args):
    """Exit game."""
    interface.running = False
    return "Saliendo..."

@command("save")
def cmd_save(interface, args):
    """Save current game."""
    path = args[0] if args else None
    return interface.session.save(path)

@command("load")
def cmd_load(interface, args):
    """Load saved game."""
    path = args[0] if args else None
    return interface.session.load(path)
```

### 6. history.py — Historial + replay

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Action:
    turn: int
    timestamp: datetime
    action_type: str
    actor: str
    description: str
    result: str
    success: bool

class History:
    def __init__(self, max_items: int = 100):
        self.actions: list[Action] = []
        self.max_items = max_items

    def add(self, action: Action):
        self.actions.append(action)
        if len(self.actions) > self.max_items:
            self.actions.pop(0)

    def get_recent(self, n: int = 10) -> list[Action]:
        return self.actions[-n:]

    def format(self) -> str:
        if not self.actions:
            return "[dim]Sin acciones registradas[/dim]"

        lines = ["[cyan]═══ Historial de Acciones ═══[/cyan]", ""]
        for a in self.get_recent(10):
            icon = "✓" if a.success else "✗"
            color = "green" if a.success else "red"
            lines.append(
                f"[{color}]{icon}[/{color}] "
                f"[dim]Turn {a.turn:03d}[/dim] "
                f"[yellow]{a.action_type}[/yellow] "
                f"por {a.actor}"
            )
            lines.append(f"   {a.description}")
        return "\n".join(lines)

    def replay(self, n: int = 1) -> str:
        """Return description of last N actions."""
        recent = self.actions[-n:]
        if not recent:
            return "[dim]No hay acciones para replay[/dim]"

        lines = ["[cyan]═══ Replay ═══[/cyan]", ""]
        for a in reversed(recent):
            lines.append(f"[yellow]{a.action_type}[/yellow] — {a.result}")
        return "\n".join(lines)

    def clear(self):
        self.actions.clear()
```

### 7. session.py — Guardar/cargar partida

```python
import json
from pathlib import Path
from datetime import datetime

class Session:
    """Save/load game state."""

    def __init__(self, world, history, config):
        self.world = world
        self.history = history
        self.config = config
        self.save_dir = Path("saves")
        self.save_dir.mkdir(exist_ok=True)

    def save(self, name: str | None = None) -> str:
        """Save current game state to JSON."""
        if name is None:
            name = datetime.now().strftime("%Y%m%d_%H%M%S")

        path = self.save_dir / f"{name}.json"

        data = {
            "name": name,
            "timestamp": datetime.now().isoformat(),
            "turn": getattr(self.world, 'turn', 0),
            "world": self.world.model_dump() if hasattr(self.world, 'model_dump') else str(self.world),
            "config": self.config,
        }

        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)

        return f"[green]Partida guardada: {path}[/green]"

    def load(self, path: str | None = None) -> str:
        """Load game state from JSON."""
        if path is None:
            # List available saves
            saves = list(self.save_dir.glob("*.json"))
            if not saves:
                return "[red]No hay partidas guardadas[/red]"
            path = str(saves[-1])  # Load most recent

        with open(path) as f:
            data = json.load(f)

        # Restore state
        if "world" in data:
            # Would need proper restoration logic
            pass

        return f"[green]Partida cargada: {path}[/green]"

    def list(self) -> list[str]:
        """List available save files."""
        return [f.stem for f in self.save_dir.glob("*.json")]
```

### 8. interface.py — Main game interface

```python
from .console import Console
from .styles import s
from .components import Components
from .selector import Selector
from .input import CommandInput, COMMANDS, command
from .history import History, Action
from .session import Session

class Interface:
    """
    Main game interface.
    Coordinates all UI components and game flow.
    """

    def __init__(self, world, config):
        self.world = world
        self.config = config
        self.console = Console.get()
        self.history = History()
        self.session = Session(world, self.history, config)
        self.running = True
        self._turn = 0

    def main_menu(self) -> str:
        """Show main menu and return choice."""
        self.console.print()
        self.console.print_panel(
            "[cyan]ECO — Memetic Simulation Engine[/cyan]\n\n"
            "1. Nueva Partida\n"
            "2. Continuar\n"
            "3. Cargar Partida\n"
            "4. Salir",
            title="ECO",
            border_style="cyan"
        )

        choice = CommandInput.get_choice(["Nueva Partida", "Continuar", "Cargar", "Salir"])
        options = ["new", "continue", "load", "quit"]
        return options[choice] if choice is not None else "quit"

    def turn_loop(self, turn: int):
        """Main turn loop."""
        self._turn = turn

        # Render turn header
        self.console.print()
        self.console.print(Components.turn_header(turn), justify="center")

        # Render world state
        metrics = self._get_world_metrics()
        self.console.print(Components.world_metrics_table(metrics))

        # Show action menu
        actions = self._get_available_actions()
        self.console.print()
        self._show_action_menu(actions)

        # Get player input
        cmd = CommandInput.get_command()

        # Handle commands vs actions
        if cmd.startswith("/"):
            return self._handle_command(cmd)
        elif cmd.isdigit():
            idx = int(cmd) - 1
            if 0 <= idx < len(actions):
                return self._do_action(actions[idx])
        elif cmd == "q":
            self.running = False

        return {"action": None, "result": ""}

    def _get_world_metrics(self) -> dict:
        """Extract current metrics from world state."""
        return {
            "Civil Unrest": getattr(self.world, 'pressure', 0),
            "Authority": getattr(self.world, 'legitimacy', 0),
            "Resources": getattr(self.world, 'resources_global', 0),
            "Influence": getattr(self.world, 'influence', 0),
            "Echoes": len(getattr(self.world, 'echoes', [])),
            "Circles": len(getattr(self.world, 'circles', [])),
        }

    def _get_available_actions(self) -> list[str]:
        """Get list of available actions for current state."""
        return [
            "found_circle",
            "write_manifesto",
            "propagate_idea",
            "talk",
            "sabotage",
            "ritualize",
            "join_circle",
            "leave_circle",
        ]

    def _show_action_menu(self, actions: list[str]):
        """Display action menu."""
        self.console.print("[bold]Acciones:[/bold]")
        for i, action in enumerate(actions, 1):
            self.console.print(f"  [cyan]{i}.[/cyan] {action}")
        self.console.print()
        self.console.print("[dim]Número para actuar · /comando · q para menú[/dim]")

    def _handle_command(self, cmd: str) -> dict:
        """Process slash command."""
        parts = cmd[1:].split()
        name = parts[0] if parts else ""
        args = parts[1:]

        if name in COMMANDS:
            result = COMMANDS[name](self, args)
            self.console.print(result)
        else:
            self.console.print(f"[red]Comando desconocido: {name}[/red]")

        return {"action": f"/{name}", "result": result if 'result' in locals() else ""}

    def _do_action(self, action_name: str) -> dict:
        """Execute an action and record it."""
        result = f"Ejecutando {action_name}..."
        success = True

        # Record in history
        self.history.add(Action(
            turn=self._turn,
            timestamp=datetime.now(),
            action_type=action_name,
            actor="Player",
            description=f"Player executed {action_name}",
            result=result,
            success=success,
        ))

        # Print result
        self.console.print(Components.action_result(action_name, result, success))

        return {"action": action_name, "result": result, "success": success}

    def show_event(self, event_type: str, title: str, summary: str = ""):
        """Display a world event."""
        self.console.print()
        self.console.print(Components.event_banner(event_type, title, summary))

    def show_replay(self, n: int = 5):
        """Show replay of last N actions."""
        self.console.print()
        self.console.print(self.history.replay(n))
```

## Game Flow

```
┌─────────────────────────────────────┐
│           MAIN MENU                 │
│  Nueva Partida / Continuar / Cargar  │
└──────────────┬──────────────────────┘
               │
    ┌──────────┴──────────┐
    ▼                     ▼
┌─────────┐          ┌─────────┐
│  NEW    │          │  LOAD   │
│  GAME   │          │  SAVE   │
└────┬────┘          └────┬────┘
     │                    │
     └────────┬───────────┘
              ▼
     ┌────────────────┐
     │   TURN LOOP    │
     │ 1. Render turn │
     │ 2. Show metrics│
     │ 3. Show actions│
     │ 4. Get input   │
     │   - Number     │
     │   - /command   │
     │   - q (menu)   │
     └───────┬────────┘
             │
    ┌────────┼────────┐
    ▼        ▼        ▼
┌──────┐ ┌──────┐ ┌──────┐
│ACTION│ │ CMD  │ │ QUIT │
│EXEC  │ │HANDLR│ │MENU  │
└──────┘ └──────┘ └──────┘
```

## Reemplazos

| Antes | Después | Notes |
|-------|---------|-------|
| `engine/tui.py` (C class + TUIRenderer + InteractiveMenu) | `interface/` package | Display + input separados |
| `blessed` | `prompt_toolkit` + `rich` | No más bugs de arrow keys |
| `InteractiveMenu` con raw mode | `Selector` con prompt_toolkit | Funciona en macOS |
| ANSI strings `\033[92m` | Rich `Style` objects | Más limpio y mantenible |
| Sin historial | `History` con replay | Replay de acciones |
| Sin guards | `Session` save/load | Guardar partidas |

## Migration Plan

1. **Fase 1**: Crear `interface/` con `console.py`, `styles.py`
2. **Fase 2**: Implementar `components.py` con widgets reutilizables
3. **Fase 3**: Implementar `selector.py` con prompt_toolkit
4. **Fase 4**: Implementar `input.py` con CommandInput + registry
5. **Fase 5**: Implementar `history.py` y `session.py`
6. **Fase 6**: Crear `interface.py` que coordina todo
7. **Fase 7**: Actualizar `run.py` para usar `Interface`
8. **Fase 8**: Eliminar `engine/tui.py` y código de `blessed`

## References

- Hermes Agent TUI: usa `prompt_toolkit.PromptSession` + `rich.Console`
- prompt_toolkit docs: https://python-prompt-toolkit.readthedocs.io/en/stable/
- rich docs: https://rich.readthedocs.io/en/stable/