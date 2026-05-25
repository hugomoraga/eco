# 32 - Echo Spawning (Daughter Echos)

**Estado:** draft  
**Fecha:** 2026-05-24  
**Dependencias:** 01, 02, 07, 08, 26, 27, 29  

---

## 1. Contexto

Spec-26 Phase 5 y spec-27: Cuando se cumplen condiciones, nuevas Echos nacen de Echos existentes. Las daughters tienen esencia mutada y pueden divergir.

Spec-27 ya tiene configuración en tuning.yaml:
```yaml
echo_spawning:
  enabled: true
  min_influence_threshold: 80
  cooldown_turns: 5
  base_chance: 0.3
```

---

## 2. Spawning Conditions

```
CONDICIONES DE SPAWN:
━━━━━━━━━━━━━━━━━━━━━━

1. Parent echo influence >= threshold (80 de default)
2. World tiene >= 2 circles
3. World tags contiene tag dominante del parent (e.g., "revolutionary" > 20)
4. Transcurrieron >= cooldown_turns desde último spawn
5. base_chance <= roll < 1.0
```

```python
def check_echo_spawn_conditions(world: World, echo: Echo) -> bool:
    """Check if echo should spawn a daughter."""
    
    tuning = get_tuning()
    
    if not tuning.echo_spawning.enabled:
        return False
        
    if world.circles < 2:
        return False
        
    cooldown_elapsed = (
        world.clock.action_tick - world.last_echo_spawn_turn >= 
        tuning.echo_spawning.cooldown_turns
    )
    if not cooldown_elapsed:
        return False
        
    influence_threshold = tuning.echo_spawning.min_influence_threshold
    if echo.influence < influence_threshold:
        return False
        
    # Tag dominance check
    parent_tags = echo.get_top_tags(2)
    world_tag_sum = sum(world.tags.get(tag, 0) for tag in parent_tags)
    if world_tag_sum < 20:
        return False
        
    # Chance roll
    roll = random.random()
    return roll < tuning.echo_spawning.base_chance
```

---

## 3. Essence Mutation

Cuando una daughter nace, su esencia muta ligeramente:

```
MUTATION RULES:
━━━━━━━━━━━━━━━━━━

Parent essence: "anarchism|collectivism|0.8|0.2"
     ↓
Daughter essence: "anarchism|collectivism|0.75|0.25"
     ↓
     (small random delta applied to each component)

Possible mutations:
  - Strengthen one dimension: 0.8 → 0.85
  - Weaken another: 0.2 → 0.15
  - Or shift: 0.75 | 0.25 → 0.70 | 0.30 (more radical)
```

```python
def mutate_essence(parent_essence: str) -> str:
    """Create mutated essence for daughter echo."""
    
    parts = parent_essence.split("|")
    if len(parts) != 4:
        return parent_essence
        
    base, modifier, strength, secondary = parts
    
    # Small random delta (-0.05 to +0.05)
    delta = random.uniform(-0.05, 0.05)
    new_strength = max(0.5, min(0.95, float(strength) + delta))
    new_secondary = 1.0 - new_strength
    
    return f"{base}|{modifier}|{new_strength:.2f}|{new_secondary:.2f}"
```

---

## 4. Daughter Echo Creation

```python
def spawn_daughter_echo(parent: Echo, world: World) -> Echo:
    """Create daughter echo from parent."""
    
    # Generate name
    daughter_name = generate_echo_name(parent.name, world.echo_count)
    
    # Mutate essence
    daughter_essence = mutate_essence(parent.essence)
    
    # Create daughter
    daughter = Echo(
        id=generate_id(),
        name=daughter_name,
        essence=daughter_essence,
        origin=f"daughter of {parent.name}",
        parent_id=parent.id,
        influence=parent.influence * 0.7,  # Start weaker
        clarity=parent.clarity * 0.5,
        circles=[],  # No circle initially
        action_history=[],
        last_action_turn={}
    )
    
    # Place in parent's circle or nearby
    if parent.circles:
        daughter.circles = [parent.circles[0]]
        world.circles[parent.circles[0]].add_member(daughter.id)
    
    # Track spawn
    world.last_echo_spawn_turn = world.clock.action_tick
    parent.daughter_ids.append(daughter.id)
    
    return daughter
```

---

## 5. Echo Name Generation

```
PATTERN: "{ParentName}'s Daughter"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Parent: "First Echo of the Garden"
Daughter: "Second Echo of the Garden"

Parent: "Sister Clarity"
Daughter: "Sister Clarity II"
```

**Or use generational naming:**
```
Generation 1: Echo of [Noun]
Generation 2: Daughter of [Echo]
Generation 3: Branch of [Echo]
```

---

## 6. Divergence over Time

 Daughters pueden divergir de parents via spec-06 (ideological drift):

```
DIVERGENCE:
━━━━━━━━━━━━

- Daughters start with slight essence mutation
- Each world tick, 5% chance of further drift
- Drift magnitude: ±0.02 per tick
- Can eventually become a different type
```

---

## 7. Console Output

```
[Turn 15] 🌱 First Echo of the Garden splits — Daughter born
          "Second Echo of the Garden" joins the Circle
          Essence mutated: anarchism|collectivism|0.80 → 0.75|0.25

[Turn 22] 🌿 Second Echo of the Garden spreads influence
          Currently in Circle of the First Garden

[Turn 30] 🌸 Daughter echoes diverge: new ideologies emerge
          Third generation Echos show distinct character
```

---

## 8. Dependencies

- **spec-27:** Configuration (tuning.yaml)
- **spec-29:** World state metrics
- **spec-30:** Circles (for placement)
- **spec-06:** Ideological drift (for divergence)

---

## 9. Implementation

**Files to modify:**
- `game_core/domain/entities.py` — Echo entity (add daughter_ids, parent_id)
- `game_core/engine/simulation.py` — echo spawning check in world tick
- `game_core/autoplayer/engine.py` — spawning considerations

**Files to create:**
- `game_core/echo/echo_spawner.py` — spawn logic
- `game_core/echo/essence_mutator.py` — mutation logic