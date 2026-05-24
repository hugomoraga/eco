# 25 - Console & Logging Output

## Metadata

- Status: draft
- Created: 2026-05-24
- Priority: medium
- Depends on: 19 (MVP)

## Context

Currently console output is minimal and unclear:
```
[Turn    1] WT=0 Echoes=1 Circles=0 Factions=1
[Turn    2] WT=0 Echoes=1 Circles=0 Factions=1
```

User cannot tell what's happening in the simulation without inspecting logs.

## Proposal

### 1. Dual Output System

**Console (summary):** Minimal, clear, human-readable with emojis
**Logs (simulation.jsonl):** Complete, structured, machine-readable

### 2. Console Output Format

#### Base Line (every turn)
```
[Turn 5] WT=0 | Echoes=1 | Circles=0 | Factions=1 | Influence=31
```
Short status line with key metrics.

#### Event Lines (when events occur)
```
[Turn 5] ⚡ Evento: "El Consejo de Barrias se reúne en secreto"
```

#### Action Lines (when actions execute)
```
[Turn 6] 📜 Manifesto escrito por Echo #1 (anarquismo, colectivismo)
[Turn 7] ⭕ Círculo fundado: "Los Sin Nombre" (miembros: 3)
[Turn 8] 🔮 Ritual completado: +2 esencialidad
[Turn 9] 📣 Idea propagada a 3.echos
[Turn 10] ⚔️ Sabotaje ejecutado contra objetivo
```

#### NPC Lines (when NPCs created)
```
[Turn 12] 👤 NPC generado: Dra. Maela Ruun (título)
```

#### Influence/Tag Changes
```
[Turn 8] 📈 Influencia: 31 → 38 (+7)
[Turn 9] 🏷️ Tags: anarquismo (+2), colectivismo (+1)
```

#### Error/Warning Lines
```
[Turn 5] ❌ Error: Falló conexión con API de IA
[Turn 7] ⚠️ Warning: Círculo sin miembros por 3 turnos
```

### 3. Emoji Key

| Emoji | Meaning |
|-------|---------|
| ⚡ | Evento generado |
| 📜 | Manifesto escrito |
| ⭕ | Círculo fundado |
| 🔮 | Ritual completado |
| 📣 | Idea propagada |
| ⚔️ | Sabotaje ejecutado |
| 👤 | NPC generado |
| 📈 | Aumento de influencia |
| 📉 | Pérdida de influencia |
| 🏷️ | Tags cambiados |
| ❌ | Error |
| ⚠️ | Warning |

### 4. Log Output (simulation.jsonl)

Every action, event, and state change is logged with full detail:

```json
{
  "timestamp": "2026-05-24T15:59:16",
  "turn": 8,
  "event_type": "action_executed",
  "action": "write_manifesto",
  "actor_id": "echo_001",
  "result": {
    "success": true,
    "manifesto_id": "manifesto_001",
    "tags_extracted": ["anarquismo", "colectivismo"],
    "influence_delta": 3
  }
}
```

```json
{
  "timestamp": "2026-05-24T15:59:16",
  "turn": 8,
  "event_type": "influence_change",
  "entity_id": "echo_001",
  "from": 31,
  "to": 38,
  "delta": 7,
  "reasons": ["manifesto_written", "tag_extracted"]
}
```

### 5. Log Levels (Optional Verbose)

**Default:** Summary console, full JSONL logs
**Verbose:** Extra console output for debugging

```bash
uv run python game_core/run.py --verbose
```

### 6. Implementation

Add `game_core/engine/console_output.py`:

```python
class ConsoleOutput:
    """Handles console and log output."""

    EMOJIS = {
        "event": "⚡",
        "manifesto": "📜",
        "circle_founded": "⭕",
        "ritual": "🔮",
        "propagate": "📣",
        "sabotage": "⚔️",
        "npc": "👤",
        "influence_up": "📈",
        "influence_down": "📉",
        "tag_change": "🏷️",
        "error": "❌",
        "warning": "⚠️",
    }

    def status_line(self, turn: int, world: World):
        print(f"[Turn {turn:3}] WT={world.clock.tick} | Echoes={len(world.echoes)} | Circles={len(world.circles)} | Factions={len(world.factions)}")

    def action_executed(self, turn: int, action_type: str, details: dict):
        emoji = self.EMOJIS.get(action_type, "•")
        print(f"[Turn {turn}] {emoji} {action_type}: {details}")

    def event_occurred(self, turn: int, event: GameEvent):
        print(f"[Turn {turn}] ⚡ Evento: \"{event.title}\"")
```

Modify `SimulationEngine.run()` to call `ConsoleOutput` methods.

### 7. Example Full Output

```
[Turn  1] WT=0 | Echoes=1 | Circles=0 | Factions=1 | Influence=20
[Turn  2] WT=0 | Echoes=1 | Circles=0 | Factions=1 | Influence=20
[Turn  3] WT=0 | Echoes=1 | Circles=0 | Factions=1 | Influence=20
[Turn  4] WT=0 | Echoes=1 | Circles=0 | Factions=1 | Influence=20
[Turn  5] ⚡ Evento: "El Consejo de Barrias se reúne en secreto"
[Turn  5] WT=0 | Echoes=1 | Circles=0 | Factions=1 | Influence=20
[Turn  6] 📜 Manifesto escrito por Echo #1 (anarquismo, colectivismo)
[Turn  6] WT=0 | Echoes=1 | Circles=0 | Factions=1 | Influence=23
[Turn  7] ⭕ Círculo fundado: "Los Sin Nombre" (miembros: 3)
[Turn  7] WT=0 | Echoes=1 | Circles=1 | Factions=1 | Influence=23
[Turn  8] 📈 Influencia: 20 → 23 (+3)
[Turn  8] WT=0 | Echoes=1 | Circles=1 | Factions=1 | Influence=23
...
```

## Status History

- 2026-05-24: draft created