# 31 - Actions with Consequences

**Estado:** draft  
**Fecha:** 2026-05-24  
**Dependencias:** 01, 02, 07, 08, 26, 29  

---

## 1. Contexto

Spec-26 Phase 1: Las acciones son stubs que no cambian nada. Necesitamos acciones con dientes — cada acción modifica el world state, crea efectos, y genera output narrativo.

---

## 2. Acciones y sus Efectos

### 2.1 write_manifesto

```
EFFECTS:
━━━━━━━━━

World state:
  → pressure += 3 (ideas spread unrest)
  → legitimacy -= 1

Echo:
  → clarity += 5
  → tags += extracted from manifesto (2-4 tags)

Output:
  → "📜 {echo.name} wrote manifesto on {dominant_tag}"
  → "   Tags: {tag1}, {tag2}, {tag3}"
  → "   → Pressure +3, Clarity +5"
```

### 2.2 propagate_idea

```
EFFECTS:
━━━━━━━━━

World state:
  → pressure += 2 per target
  → legitimacy -= 1 per target

Echo:
  → resonance += 1 per successful propagation

Tags:
  → propagated_tag += 3 in world state

Output:
  → "📣 {echo.name} propagates {tag} to {target}"
  → "   → {target} influenced, Pressure +{n}"
```

### 2.3 ritualize

```
EFFECTS:
━━━━━━━━━

World state:
  → pressure -= 5 (rituals calm masses)
  → legitimacy -= 2 (authority dislikes rituals)
  → resources -= 3 (ritual costs energy)

Echo:
  → resonance += 3
  → clarity += 2

Event chance:
  → 15% chance to trigger minor event

Output:
  → "🔮 {echo.name} performs ritual of {essence}"
  → "   → Pressure -5, Resonance +3"
  → "   [Optional] Mystical resonance detected..."
```

### 2.4 sabotage

```
EFFECTS:
━━━━━━━━━

World state:
  → legitimacy -= 8 (authority retaliates)
  → resources -= 8
  → pressure += 12 (conflict)

Target faction:
  → influence -= 15

Echo:
  → resonance -= 2 (violence costs clarity)

Counter-event:
  → 40% chance to trigger retaliation event

Output:
  → "⚔️ {echo.name} sabotages {target} infrastructure"
  → "   → Authority legitimacy -8, Conflict rising"
```

### 2.5 talk

```
EFFECTS:
━━━━━━━━━

Success (roll vs target resistance):
  → target joins echo's circle
  → circle gains member
  → circle influence += 3

NPC dialogue:
  → NPC responds with contextual line (from spec-28 template)
  → Dialogue logged in narrative

Failure:
  → "NPC refused to join"
  → resonance unchanged

Output:
  → "💬 {echo.name} speaks with {npc.name}"
  → "   \"{npc_dialogue}\""
  → "   [SUCCESS] {npc.name} joined the circle"
```

### 2.6 found_circle

```
EFFECTS:
━━━━━━━━━

World state:
  → legitimacy -= 3 (assembly is threat to authority)
  → pressure += 2 (organization is threat)

Circle created:
  → Named circle with essence
  → Echo joins as first member
  → Circle influence = 15

Output:
  → "⭕ {echo.name} founded Circle of {name}"
  → "   First circle: {essence} resonance"
  → "   → Legitimacy -3, Authority watches"
```

### 2.7 join_circle

```
EFFECTS:
━━━━━━━━━

Echo:
  → joins existing circle
  → circle gains member

Circle:
  → member_count += 1
  → influence += 2

Output:
  → "→ {echo.name} joined {circle.name}"
```

### 2.8 leave_circle

```
EFFECTS:
━━━━━━━━━

Circle:
  → loses member
  → member_count -= 1
  → influence -= 3

Echo:
  → no longer belongs to circle
  → (can found new or join another)

Output:
  → "← {echo.name} left {circle.name}"
```

---

## 3. Action Result Structure

```python
@dataclass
class ActionResult:
    success: bool
    message: str  # Narrative text for console
    effects: dict[str, Any]  # Changes made
    
    # Optional: World state changes
    pressure_delta: float = 0
    legitimacy_delta: float = 0
    resources_delta: float = 0
    
    # Optional: Tags changed
    tags_added: list[str] = []
    tags_removed: list[str] = []
```

---

## 4. Aplicación de Efectos

```python
def apply_action_effects(result: ActionResult, world: World) -> None:
    """Apply action result effects to world state."""
    
    if result.pressure_delta:
        world.pressure += result.pressure_delta
    if result.legitimacy_delta:
        world.legitimacy += result.legitimacy_delta
    if result.resources_delta:
        world.resources += result.resources_delta
        
    if result.tags_added:
        for tag in result.tags_added:
            world.tags[tag] = world.tags.get(tag, 0) + 3
            
    if result.tags_removed:
        for tag in result.tags_removed:
            world.tags[tag] = max(0, world.tags.get(tag, 0) - 3)
```

---

## 5. Console Output Format

```
FORMATO POR ACCIÓN:
━━━━━━━━━━━━━━━━━━━━

[Turn N] 📜 {echo.name} wrote manifesto on {tag}
         Tags: {tag1}, {tag2}
         → Pressure +3, Clarity +5

[Turn N] ⚔️ {echo.name} sabotaged {target}
         → Authority -8, Conflict rising +12

[Turn N] 💬 {echo.name} spoke with {npc.name}
         "{dialogue}"
         → {npc.name} joined Circle of {name}
```

---

## 6. Dependencias

- **spec-29:** World state metrics
- **spec-30:** Circles con miembros
- **spec-28:** NPC templates y diálogos
- **spec-26:** Action definitions

---

## 7. Implementación

**Files to modify:**
- `game_core/engine/actions/write_manifesto.py` — agregar effects
- `game_core/engine/actions/propagate_idea.py` — agregar effects
- `game_core/engine/actions/ritualize.py` — agregar effects
- `game_core/engine/actions/sabotage.py` — agregar effects
- `game_core/engine/actions/talk.py` — agregar effects + dialogue
- `game_core/engine/actions/found_circle.py` — ya en spec-30
- `game_core/engine/actions/join_circle.py` — nueva
- `game_core/engine/actions/leave_circle.py` — nueva

**Files to create:**
- `game_core/domain/results.py` — ActionResult dataclass
- `game_core/engine/action_effects.py` — apply_effects function