from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_core.domain.entities import World


class ConsoleOutput:
    EMOJIS = {
        "event": "⚡",
        "manifesto": "📜",
        "circle_founded": "⭕",
        "ritual": "🔮",
        "propagate": "📣",
        "propagate_idea": "📣",
        "sabotage": "⚔️",
        "npc": "👤",
        "influence_up": "📈",
        "influence_down": "📉",
        "tag_change": "🏷️",
        "error": "❌",
        "warning": "⚠️",
        "talk": "💬",
        "found_circle": "⭕",
        "write_manifesto": "📜",
        "recruit": "👥",
        "ritualize": "🔮",
    }

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self._last_influence: int | None = None

    def status_line(self, turn: int, world: World) -> None:
        total_influence = 0
        for echo in world.echoes:
            clarity_attr = echo.get_attribute("clarity")
            if clarity_attr:
                total_influence += int(clarity_attr.value)
        print(
            f"[Turn {turn:3}] WT={world.clock.world_tick} | "
            f"Echoes={len(world.echoes)} | "
            f"Circles={len(world.circles)} | "
            f"Factions={len(world.factions)} | "
            f"Influence={total_influence}"
        )

    def event_occurred(self, turn: int, event_title: str) -> None:
        from game_core.i18n import t
        print(f"[Turn {turn}] ⚡ {t('messages:event')}: \"{event_title}\"")

    def action_executed(
        self, turn: int, action_type: str, details: dict
    ) -> None:
        emoji = self.EMOJIS.get(action_type, "•")
        print(f"[Turn {turn}] {emoji} {details}")

    def influence_change(
        self, turn: int, old_value: int, new_value: int
    ) -> None:
        delta = new_value - old_value
        sign = "+" if delta >= 0 else ""
        emoji = self.EMOJIS["influence_up"] if delta >= 0 else self.EMOJIS["influence_down"]
        print(f"[Turn {turn}] {emoji} Influencia: {old_value} → {new_value} ({sign}{delta})")
        self._last_influence = new_value

    def tag_change(self, turn: int, tags: list[str]) -> None:
        if tags:
            tags_str = ", ".join(tags[:5])
            if len(tags) > 5:
                tags_str += f" (+{len(tags) - 5} more)"
            print(f"[Turn {turn}] 🏷️ Tags: {tags_str}")

    def npc_created(self, turn: int, npc_name: str, npc_role: str) -> None:
        print(f"[Turn {turn}] 👤 NPC generado: {npc_name} ({npc_role})")

    def circle_founded(self, turn: int, circle_name: str, members: int) -> None:
        print(f"[Turn {turn}] ⭕ Círculo fundado: \"{circle_name}\" (miembros: {members})")

    def manifesto_written(self, turn: int, echo_name: str, tags: list[str]) -> None:
        tags_str = ", ".join(tags[:3]) if tags else "sin tags"
        print(f"[Turn {turn}] 📜 Manifesto escrito por {echo_name} ({tags_str})")

    def error(self, turn: int, message: str) -> None:
        print(f"[Turn {turn}] ❌ Error: {message}")

    def warning(self, turn: int, message: str) -> None:
        print(f"[Turn {turn}] ⚠️ Warning: {message}")

    def verbose_log(self, turn: int, message: str) -> None:
        if self.verbose:
            print(f"[Turn {turn}] [VERBOSE] {message}")

    def log_to_jsonl(
        self, log_file, turn: int, event_type: str, data: dict
    ) -> None:
        import json

        entry = {
            "timestamp": datetime.now().isoformat(),
            "turn": turn,
            "event_type": event_type,
            **data,
        }
        log_file.write(json.dumps(entry) + "\n")
        log_file.flush()