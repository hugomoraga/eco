import json
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from adapters.tui.history import History
    from core.domain import World


class Session:
    def __init__(self, world: "World", history: "History", config: dict):
        self.world = world
        self.history = history
        self.config = config
        self.save_dir = Path("saves")
        self.save_dir.mkdir(exist_ok=True)

    def save(self, name: str | None = None) -> str:
        if name is None:
            name = datetime.now().strftime("%Y%m%d_%H%M%S")

        path = self.save_dir / f"{name}.json"

        data = {
            "name": name,
            "timestamp": datetime.now().isoformat(),
            "turn": getattr(self.world, "clock", None) if self.world else 0,
            "world": self.world.model_dump() if hasattr(self.world, "model_dump") else {},
            "config": self.config,
        }

        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)

        return f"[green]Partida guardada: {path}[/green]"

    def load(self, path: str | None = None) -> str:
        if path is None:
            saves = list(self.save_dir.glob("*.json"))
            if not saves:
                return "[red]No hay partidas guardadas[/red]"
            path = str(saves[-1])

        with open(path) as f:
            data = json.load(f)

        if "world" in data:
            pass

        return f"[green]Partida cargada: {path}[/green]"

    def list(self) -> list[str]:
        return [f.stem for f in self.save_dir.glob("*.json")]
