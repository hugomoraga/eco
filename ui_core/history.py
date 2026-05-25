from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ui_core.interface import Interface


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

    def add(self, action: Action) -> None:
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
            icon = "[green]✓[/green]" if a.success else "[red]✗[/red]"
            lines.append(
                f"{icon} "
                f"[dim]Turn {a.turn:03d}[/dim] "
                f"[yellow]{a.action_type}[/yellow] "
                f"por {a.actor}"
            )
            lines.append(f"   {a.description}")
        return "\n".join(lines)

    def replay(self, n: int = 1) -> str:
        recent = self.actions[-n:]
        if not recent:
            return "[dim]No hay acciones para replay[/dim]"

        lines = ["[cyan]═══ Replay ═══[/cyan]", ""]
        for a in reversed(recent):
            icon = "[green]✓[/green]" if a.success else "[red]✗[/red]"
            lines.append(f"{icon} [yellow]{a.action_type}[/yellow] - {a.result}")
        return "\n".join(lines)

    def clear(self) -> None:
        self.actions.clear()

    def get_action_names(self) -> list[str]:
        return [a.action_type for a in self.actions]

    def get_last_action(self) -> Action | None:
        return self.actions[-1] if self.actions else None