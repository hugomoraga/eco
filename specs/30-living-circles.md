# 30 - Living Circles

**Estado:** draft  
**Fecha:** 2026-05-24  
**Dependencias:** 01, 02, 07, 08, 26, 28  

---

## 1. Contexto

Spec-26 Phase 2: Circles deben almacenar miembros, tener nombres generados, y crecer orgánicamente.

Spec-28 usa circles para NPC spawning: `circles.members_for_npc = 3`

---

## 2. Estructura de Circle

```python
# En domain/entities.py
class Circle(BaseModel):
    id: str
    name: str  # AI-generated: "Circle of the First Garden"
    essence: str  # Dominant essence in this circle
    members: list[str] = []  # Echo IDs + NPC IDs
    founded_turn: int
    influence: float = 10.0  # Ability to attract others
    
    # Growth tracking
    member_count: int = 0  # Cached for quick access
    
    def add_member(self, entity_id: str) -> None:
        if entity_id not in self.members:
            self.members.append(entity_id)
            self.member_count = len(self.members)
            
    def remove_member(self, entity_id: str) -> None:
        if entity_id in self.members:
            self.members.remove(entity_id)
            self.member_count = len(self.members)
```

---

## 3. Nombre de Círculo

Generado por AI al crearse:

```
PROMPT_TEMPLATE = """
Generate a poetic name for a new circle.
Context: This circle represents {essence}.
Theme: {theme_hint}

Examples:
- "Circle of the First Garden"
- "Circle of Burning Echoes"
- "Circle of the Silent Consensus"

Respond with only the name, no quotes or explanation.
"""
```

**Fallback (si AI no responde):**
```
"Circle of the [Noun]"
Nouns: Echo, Garden, Flame, Voice, Root, Threshold, Consensus, Memory
```

---

## 4. Circle Growth Mechanism

```python
def circle_tick(circle: Circle, world: World) -> None:
    """Called each world tick. Circle may grow or shrink."""
    
    # Natural growth chance based on influence
    if circle.influence > 20 and circle.member_count < 8:
        growth_roll = random.random()
        if growth_roll < 0.15:  # 15% chance
            # Attract random echo or wandering NPC
            world.spawn_wanderer_near(circle)
    
    # Member loss chance (social decay)
    if circle.member_count > 3:
        decay_roll = random.random()
        if decay_roll < 0.03:  # 3% chance per turn
            # Member leaves (prefer lower resonance members)
            member_to_leave = circle.get_lowest_resonance_member()
            if member_to_leave:
                circle.remove_member(member_to_leave)
```

---

## 5. NPC Spawning desde Circles

Spec-28: `circles.members_for_npc = 3`

```
TRIGGER: Circle reaches 3+ members
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

When circle.member_count >= 3:
  → 20% chance to spawn NPC in that circle
  → NPC type based on circle's essence
  → NPC name generated from pool
  
Spawned NPC:
  → Joins the circle as member
  → Has essence compatible with circle
  → Has pre-generated dialogue (spec-28 template)
```

---

## 6. Acciones que Crean Círculos

```python
def found_circle(echo: Echo, world: World) -> ActionResult:
    """found_circle action implementation."""
    
    # Generate name
    circle_name = ai_generate_circle_name(echo.essence)
    
    # Create circle
    circle = Circle(
        id=generate_id(),
        name=circle_name,
        essence=echo.essence,
        members=[echo.id],
        founded_turn=world.clock.action_tick,
        influence=15.0
    )
    
    # Register in world
    world.circles[circle.id] = circle
    echo.circles.append(circle.id)
    
    # World metrics impact (spec-29)
    world.legitimacy -= 2
    world.pressure += 1
    
    return ActionResult(
        success=True,
        message=f"Founded {circle_name} with {echo.name} as first member",
        effects={"circle_created": circle.id, "members": 1}
    )
```

---

## 7. Acciones Involucrando Círculos

```
TALK:
  → Can recruit NPC or Echo to player's circle
  → Circle gains member
  → Circle influence increases
  
JOIN_CIRCLE:
  → Echo joins existing circle
  → Requires echo to be near circle (same location)
  
LEAVE_CIRCLE:
  → Echo leaves circle
  → Circle loses member
  → Circle influence decreases
  
TRANSFER:
  → Move member from circle A to circle B
  → Rare action
```

---

## 8. Console Output

```
[Turn 3] ⭕ Founded Circle of the First Garden (1 member)
[Turn 5] 👤 Brother Simón joined Circle of the First Garden
[Turn 6] ⭕ Circle of the First Garden grew to 3 members
[Turn 7] 👤 Dra. Maela Ruun joins — first NPC in the circle
[Turn 9] ⭕ Circle of the First Garden: 5 members now
```

---

## 9. Dependencias

- **spec-28:** Usa circles para NPC spawning
- **spec-29:** Modificaciones a world metrics
- **spec-28:** Templates de NPC con diálogos

---

## 10. Implementación

**Files to modify:**
- `game_core/domain/entities.py` — Circle entity con members
- `game_core/engine/actions/found_circle.py` — crear círculo
- `game_core/engine/actions/talk.py` — reclutar
- `game_core/engine/actions/join_circle.py` — nueva acción
- `game_core/engine/actions/leave_circle.py` — nueva acción
- `game_core/engine/simulation.py` — circle tick evolution

**Files to create:**
- `game_core/engine/actions/join_circle.py`
- `game_core/engine/actions/leave_circle.py`
- `game_core/npc/npc_spawner.py` — spawn logic