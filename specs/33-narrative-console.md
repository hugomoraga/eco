# 33 - Narrative Console Output

**Estado:** draft  
**Fecha:** 2026-05-24  
**Dependencias:** 01, 02, 26, 28, 29, 30, 31  

---

## 1. Contexto

Spec-26 Phase 6: El output por turno debe ser legible como narrativa, no como spreadsheet. Cada línea tell part of a story con personajes nombrados y consecuencias.

---

## 2. Formato por Tipo

```
TURNO COMPLETO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

═══════════════════════════════════════════
TURN 7 — WORLD ACTIVITY
═══════════════════════════════════════════
• Sister Elena spreads collectivist ideas in the eastern quarter
• Crisis: Authority banned public assembly (Legitimacy -10)
───────────────────────────────────────────

📜 First Echo wrote manifesto on anarchism
   Tags: anarchism, collectivism, resistance
   → Pressure +3, Clarity +5

⭕ Founded Circle of the First Garden (1 member)
   → Legitimacy -3, Authority watches

👤 Brother Simón: "The seeds are planted."
   Joined Circle of the First Garden

═══════════════════════════════════════════
TURN 8 — WORLD ACTIVITY
═══════════════════════════════════════════
• Circle of the First Garden grew to 3 members
• Brother Simón speaks: "This path leads to isolation"
───────────────────────────────────────────
```

---

## 3. Emoji System

```
EMOJI MEANINGS:
━━━━━━━━━━━━━━━

📜 Action      → manifesto, propagate (ideas)
⭕ Circle      → founded, joined, grew
👤 NPC         → speaks, acts, joins
⚡ Event       → crisis, opportunity, revelation
📣 Propagation → spread to districts
🔮 Ritual      → performed
⚔️ Conflict    → sabotage, attack
📈/📉 State    → major metric change
🌱 Echo        → spawn, daughter born
🏷️ Tag         → acquired, lost
❌ Failure     → action failed
```

---

## 4. NPC Dialogue Format

```
NPC SPEAKING:
━━━━━━━━━━━━━━

[Turn N] 👤 {npc.name}: "{dialogue}"
          → Context: what triggered this
```

**Diálogo proviene de spec-28 templates:**
- ASK_MEANING → "¿Qué es la libertad?"
- REACT_CRISIS → "Even fire refines gold."
- NPC_CONVERTS → "Light passes from lamp to lamp."

---

## 5. Action Output Format

```
ACTION LINE:
━━━━━━━━━━━━

[Turn N] 📜 {echo.name} wrote manifesto on {tag}
         Tags: {tag1}, {tag2}
         → Pressure +3, Clarity +5

[Turn N] ⚔️ {echo.name} sabotaged {target} infrastructure
         → Authority -8, Conflict rising

[Turn N] 🔮 {echo.name} performed ritual of {essence}
         → Pressure -5, Resonance +3
```

---

## 6. Event Output Format

```
EVENT LINE:
━━━━━━━━━━━━

[Turn N] ⚡ CRISIS: "{event.title}"
         "{event.summary}"
         → {metric_change} ({delta})

[Turn N] ⚡ OPPORTUNITY: "{event.title}"
         "{event.summary}"
         → {metric_change} ({delta})

[Turn N] ⚡ REVELATION: "{event.title}"
         "{event.summary}"
         → New information unlocked
```

---

## 7. World State Change Output

```
METRIC CHANGES:
━━━━━━━━━━━━━━━

Cuando cambio > 10 puntos o cruza threshold:

[Turn N] 📉 Authority legitimacy: 60 → 52 (-8)
[Turn N] 📈 Civil unrest rising: 45 → 58 (+13)
[Turn N] ⚠️ Crisis threshold crossed (pressure: 76)
[Turn N] ⚠️ Regime collapse imminent (legitimacy: 18)
```

---

## 8. Turn Separator

```
VISUAL SEPARATOR:
━━━━━━━━━━━━━━━━━

═══════════════════════════════════════════
TURN {N} — WORLD ACTIVITY
═══════════════════════════════════════════
{activity lines}
───────────────────────────────────────────

{action output}

{more output...}

═══════════════════════════════════════════
```

---

## 9. Console Class

```python
class NarrativeConsole:
    """Handles all narrative output to console."""
    
    def print_turn_header(self, turn: int, world_activity: list[str]) -> None:
        """Print turn separator + world activity summary."""
        pass
        
    def print_action(self, turn: int, action_type: str, 
                    subject: str, details: dict) -> None:
        """Print action with emoji, subject, details."""
        pass
        
    def print_npc_speak(self, turn: int, npc_name: str, 
                        dialogue: str, context: str) -> None:
        """Print NPC speaking."""
        pass
        
    def print_event(self, turn: int, event_type: str,
                    title: str, summary: str, 
                    metric_changes: dict) -> None:
        """Print event with consequences."""
        pass
        
    def print_metric_change(self, turn: int, metric: str,
                           old_val: float, new_val: float) -> None:
        """Print significant metric change."""
        pass
        
    def print_echo_spawn(self, turn: int, parent: str, daughter: str,
                        mutation: str) -> None:
        """Print new echo spawned."""
        pass
```

---

## 10. World Activity Summary

Spec-28 Section 2: Al inicio de cada turno, mostrar 0-3 líneas de actividad mundial:

```
• Sister Elena joined Circle of the First Garden
• Brother Simón spreads ideas in eastern quarter
• Crisis: Authority banned assembly → Legitimacy -10
```

**Reglas:**
- Máx 3 líneas
- Formato: "[Name] [verb] [description]"
- Si no hay actividad: "• Silence in the streets..."
- Incluye consecuencias de eventos

---

## 11. Implementation

**Files to modify:**
- `game_core/console/narrative_console.py` — nueva clase
- `game_core/engine/simulation.py` — usar NarrativeConsole
- `game_core/engine/actions/*.py` — usar NarrativeConsole para output

**Files to create:**
- `game_core/console/__init__.py`
- `game_core/console/narrative_console.py`
- `game_core/console/formatters.py` — emoji, formatting utils