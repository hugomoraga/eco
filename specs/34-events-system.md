# 34 - Events System

**Estado:** draft  
**Fecha:** 2026-05-24  
**Dependencias:** 01, 02, 13, 26, 29  

---

## 1. Contexto

spec-13 está en draft. Esta spec implementa el sistema de eventos completo con consecuencias reales en world state (spec-29).

---

## 2. Tipos de Evento

```
EVENT TYPES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CRISIS      → Negative world change, requires response
OPPORTUNITY → Positive world change, can exploit
REVELATION  → New information/tags unlocked
CONFLICT    → Faction vs faction, high impact
CONVERGENCE → Circles merge, stability
```

---

## 3. Event Structure

```python
@dataclass
class GameEvent:
    id: str
    type: EventType  # CRISIS, OPPORTUNITY, etc.
    title: str       # AI-generated title
    summary: str     # AI-generated description
    
    # World state consequences (spec-29)
    pressure_delta: float = 0
    legitimacy_delta: float = 0
    resources_delta: float = 0
    
    # Tags affected
    tags_added: list[str] = []
    tags_removed: list[str] = []
    
    # Event lifecycle
    triggered_turn: int = 0
    duration_turns: int = 0  # 0 = instant, N = lasts N turns
    resolved: bool = False
    
    # Optional: NPC involved
    npc_id: str | None = None
```

---

## 4. Event Triggers

```
TRIGGER CONDITIONS:
━━━━━━━━━━━━━━━━━━━━━━

CRISIS:
  - world.pressure > 75 (threshold crossed)
  - world.legitimacy < 25
  - action sabotage succeeds (40% chance)

OPPORTUNITY:
  - world.resources > 85
  - world.legitimacy > 75
  - echo writes manifesto with rare tag

REVELATION:
  - propagate_idea reaches 5+ targets
  - world.tags exceeds threshold for rare tag
  - ritualize succeeds (15% chance)

CONFLICT:
  - world.pressure > 85
  - two factions have high influence
  - sabotage triggers retaliation

CONVERGENCE:
  - 2+ circles with same essence exist
  - circle membership > 6 total
  - Player action "unite_circles"
```

---

## 5. Event Generation

```python
def generate_event(event_type: EventType, context: dict) -> GameEvent:
    """AI generates event title and summary."""
    
    prompt = f"""
You are generating a narrative event for a game.
Event type: {event_type.value}
Context: {context}

Generate:
1. A short, evocative title (3-5 words)
2. A 1-sentence summary describing what happened

Keep the language mysterious and philosophical.
"""
    
    # Use AI to generate title and summary
    response = ai_generate(prompt)
    
    return GameEvent(
        id=generate_id(),
        type=event_type,
        title=response.title,
        summary=response.summary,
        triggered_turn=current_turn
    )
```

---

## 6. Event Effects on World

```python
# CRISIS default effects
CRISIS_EFFECTS = {
    "pressure_delta": +15,
    "legitimacy_delta": -10,
    "resources_delta": -5
}

# OPPORTUNITY default effects
OPPORTUNITY_EFFECTS = {
    "pressure_delta": -3,
    "legitimacy_delta": +5,
    "resources_delta": +10
}

# CONFLICT default effects
CONFLICT_EFFECTS = {
    "pressure_delta": +20,
    "legitimacy_delta": -8,
    "resources_delta": -15
}

# REVELATION default effects
REVELATION_EFFECTS = {
    "pressure_delta": +5,
    "legitimacy_delta": -3,
    "resources_delta": 0
}

# CONVERGENCE default effects
CONVERGENCE_EFFECTS = {
    "pressure_delta": -5,
    "legitimacy_delta": +3,
    "resources_delta": 0
}
```

---

## 7. Event Processing

```python
def process_events(world: World) -> list[GameEvent]:
    """Called during world tick. Process and trigger events."""
    
    triggered = []
    
    # Check crisis threshold
    if world.pressure > world.crisis_threshold:
        crisis = generate_crisis_event(world)
        apply_event_effects(crisis, world)
        triggered.append(crisis)
        
    # Check opportunity condition
    if world.resources > 85 and world.legitimacy > 70:
        if random.random() < 0.1:  # 10% chance
            opportunity = generate_opportunity_event(world)
            apply_event_effects(opportunity, world)
            triggered.append(opportunity)
    
    # Check conflict
    if world.pressure > 85 and len(world.factions) > 1:
        if random.random() < 0.15:
            conflict = generate_conflict_event(world)
            apply_event_effects(conflict, world)
            triggered.append(conflict)
            
    return triggered
```

---

## 8. Applied Events Storage

```python
class World(BaseModel):
    # ... existing fields ...
    
    # Events
    active_events: list[GameEvent] = []
    event_history: list[GameEvent] = []
```

Events are stored in history for replay and narrative context.

---

## 9. Counter-Events

Some events trigger counter-events:

```
SABOTAGE → 40% chance → RETALIATION event
  → Authority punishes the circle
  → pressure += 5, legitimacy -= 3

HIGH_TENSION → 20% chance → EXPLOSION event
  → Random outbreak of violence
  → pressure += 15, resources -= 10

RITUAL_ABUSE → 10% chance → AUTHORITY_CRACKDOWN
  → Authority raids ritual site
  → legitimacy -= 5, circle members -1
```

---

## 10. Event Templates

Pre-defined event templates that AI can use as base:

```yaml
# data/events/crisis_templates.yaml
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CRISIS_TEMPLATES:
  authority_bans_assembly:
    title: "Authority Bans Assembly"
    summary: "The council has declared public gatherings illegal."
    pressure_delta: +15
    legitimacy_delta: -10
    resources_delta: 0
    
  resource_shortage:
    title: "Resource Shortage"
    summary: "Supplies run low as winter approaches."
    pressure_delta: +10
    legitimacy_delta: -5
    resources_delta: -20

OPPORTUNITY_TEMPLATES:
  open_laboratory:
    title: "The Open Laboratory"
    summary: "New protocols for horizontal coordination are discovered."
    pressure_delta: -5
    legitimacy_delta: +3
    resources_delta: +10
    
  collective_growth:
    title: "Collective Growth"
    summary: "New members join the circles in response to crisis."
    pressure_delta: -3
    legitimacy_delta: +2
    resources_delta: +5
```

---

## 11. Event Console Output

```
[Turn 5] ⚡ CRISIS: "Authority Bans Assembly"
         The council has declared public gatherings illegal.
         → Pressure +15, Legitimacy -10

[Turn 7] ⚡ OPPORTUNITY: "The Open Laboratory"
         New protocols for horizontal coordination discovered.
         → Resources +10, Pressure -5

[Turn 9] ⚡ CONFLICT: "Faction War Ignites"
         Two factions dispute control of eastern districts.
         → Pressure +20, Resources -15
```

---

## 12. Dependencies

- **spec-13:** Event templates (draft)
- **spec-26:** Event types definition
- **spec-29:** World state metrics (for triggers and effects)
- **spec-28:** World activity summary (shows events)

---

## 13. Implementation

**Files to modify:**
- `game_core/domain/events.py` — GameEvent class
- `game_core/engine/simulation.py` — event processing in world tick
- `game_core/engine/world_tick.py` — event trigger checks

**Files to create:**
- `game_core/events/event_generator.py` — AI event generation
- `game_core/events/event_processor.py` — trigger checks and processing
- `game_core/events/event_templates.yaml` — pre-defined templates
- `game_core/events/effects.py` — apply_event_effects function