from datetime import datetime
from typing import Any

from rich.text import Text

from ui_core.console import Console
from ui_core.styles import s
from ui_core.components import Components
from ui_core.history import History, Action
from ui_core.session import Session


class Interface:
    def __init__(self, world: Any, config: dict):
        self.world = world
        self.config = config
        self.console = Console.get()
        self.history = History()
        self.session = Session(world, self.history, config)
        self.running = True
        self._turn = 0

    def main_menu(self) -> str:
        self.console.print()
        self.console.print_panel(
            "[cyan]ECO - Memetic Simulation Engine[/cyan]\n\n"
            "1. Nueva Partida\n"
            "2. Continuar\n"
            "3. Cargar Partida\n"
            "4. Salir",
            title="ECO",
            border_style="cyan",
        )

        from ui_core.input import CommandInput, COMMANDS

        choice = CommandInput.get_choice(
            ["Nueva Partida", "Continuar", "Cargar", "Salir"]
        )
        options = ["new", "continue", "load", "quit"]
        return options[choice] if choice is not None else "quit"

    def turn_loop(self, turn: int) -> dict[str, Any]:
        self._turn = turn

        self.console.print()
        self.console.print(Components.turn_header(turn), justify="center")

        metrics = self._get_world_metrics()
        self.console.print(Components.world_metrics_table(metrics))

        actions = self._get_available_actions()
        self.console.print()
        self._show_action_menu(actions)

        from ui_core.input import CommandInput, COMMANDS

        cmd = CommandInput.get_command()

        if cmd.startswith("/"):
            return self._handle_command(cmd)
        elif cmd.isdigit():
            idx = int(cmd) - 1
            if 0 <= idx < len(actions):
                return self._do_action(actions[idx])
        elif cmd == "q":
            self.running = False

        return {"action": None, "result": ""}

    def _get_world_metrics(self) -> dict[str, float]:
        return {
            "Civil Unrest": getattr(self.world, "pressure", 0),
            "Authority": getattr(self.world, "legitimacy", 0),
            "Resources": getattr(self.world, "resources_global", 0),
            "Influence": getattr(self.world, "influence", 0),
            "Echoes": len(getattr(self.world, "echoes", [])),
            "Circles": len(getattr(self.world, "circles", [])),
        }

    def _get_available_actions(self) -> list[str]:
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

    def _show_action_menu(self, actions: list[str]) -> None:
        self.console.print("[bold]Acciones:[/bold]")
        for i, action in enumerate(actions, 1):
            self.console.print(f"  [cyan]{i}.[/cyan] {action}")
        self.console.print()
        self.console.print("[dim]Numero para actuar · /comando · q para menu[/dim]")

    def _handle_command(self, cmd: str) -> dict[str, Any]:
        from game_core.interface.input import COMMANDS

        parts = cmd[1:].split()
        name = parts[0] if parts else ""
        args = parts[1:]

        if name in COMMANDS:
            result = COMMANDS[name](self, args)
            self.console.print(result)
        else:
            self.console.print(f"[red]Comando desconocido: {name}[/red]")
            result = f"Comando desconocido: {name}"

        return {"action": f"/{name}", "result": result}

    def _do_action(self, action_name: str) -> dict[str, Any]:
        result_msg = f"Ejecutando {action_name}..."
        success = True

        self.history.add(Action(
            turn=self._turn,
            timestamp=datetime.now(),
            action_type=action_name,
            actor="Player",
            description=f"Player executed {action_name}",
            result=result_msg,
            success=success,
        ))

        self.console.print(
            Components.action_result(action_name, result_msg, success)
        )

        return {"action": action_name, "result": result_msg, "success": success}

    def show_event(self, event_type: str, title: str, summary: str = "") -> None:
        self.console.print()
        self.console.print(Components.event_banner(event_type, title, summary))

    def show_replay(self, n: int = 5) -> None:
        self.console.print()
        self.console.print(self.history.replay(n))

    def show_metrics_delta(
        self, old_metrics: dict[str, float], new_metrics: dict[str, float]
    ) -> None:
        table = Components.metrics_delta_table(old_metrics, new_metrics)
        self.console.print(table)

    def print_action_result(
        self,
        turn: int,
        action_type: str,
        message: str,
        details: dict | None = None,
    ) -> None:
        from ui_core.styles import CYAN, YELLOW, RED, GREEN

        emoji_map = {
            "found_circle": "⭕",
            "join_circle": "⭕",
            "leave_circle": "➖",
            "write_manifesto": "📜",
            "propagate_idea": "📣",
            "sabotage": "⚔️",
            "ritualize": "🔮",
            "talk": "💬",
            "event": "⚡",
        }
        emoji = emoji_map.get(action_type, "•")
        self.console.print(f"  {emoji} [dim][Turn {turn}][/dim] [bold]{message}[/bold]")

        if details:
            for key, value in details.items():
                self.console.print(Components.action_detail(key, value))

        self.console.print()

    def print_status_line(self, turn: int, world: Any) -> None:
        wt = getattr(world.clock, "world_tick", 0) if world else 0
        echoes = len(getattr(world, "echoes", []))
        circles = len(getattr(world, "circles", []))
        factions = len(getattr(world, "factions", []))
        influence = int(getattr(world, "influence", 0))

        self.console.print(Components.status_line(turn, wt, echoes, circles, factions, influence))