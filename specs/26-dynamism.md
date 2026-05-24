# 26 - Action Diminishing Returns & Dynamism

## Metadata

- Status: draft
- Created: 2026-05-24
- Priority: high
- Depends on: 19 (MVP)

## Context

Current autoplay always picks write_manifesto (score 73) over found_circle (68.5) every turn. After 50 turns: Circles=0, Echoes=1, no world evolution.

Problems:
1. Repeated actions don't lose score → always pick same action
2. World state barely changes (only influence increases)
3. No variety, no tension, no interesting decisions

## Proposal

### 1. Diminishing Returns System

When an action is repeated, its score decreases:

```python
def get_action_score(action_type: str, echo: Echo, world: World, turn: int) -> float:
    base_score = calculate_base_score(action_type, echo, world)

    # Diminishing returns for repeated actions
    action_history = echo.action_history[-10:]  # last 10 actions
    repeats = action_history.count(action_type)
    diminishing_factor = max(0.3, 1.0 - (repeats * 0.15))  # -15% per repeat, min 30%

    # Cooldown bonus for not doing action recently
    turns_since = _turns_since_action(echo, action_type)
    freshness_bonus = min(0.3, turns_since * 0.05)  # +5% per turn since last use

    return base_score * diminishing_factor * (1 + freshness_bonus)
```

**Example:**
- write_manifesto base score: 73
- Turn 1: 73 * 1.0 = 73
- Turn 2: 73 * 0.85 = 62 (repeated)
- Turn 3: 73 * 0.70 = 51 (repeated twice)
- Turn 4: 73 * 0.55 = 40 (repeated thrice)
- found_circle (never used): 68.5 * 1.15 = 78 → now wins

### 2. World State Evolution

World should change meaningfully each turn:

**Before (static):**
- Echoes=1 for 50 turns
- Circles=0 for 50 turns
- Only influence changes

**After (dynamic):**
- Echos can spawn/join/leave
- Circles can be founded, grow, dissolve
- Faction influence can rise/fall
- Tags accumulate and affect world
- WorldTick triggers changes in pressure/events

### 3. Action Effects that Change World

**found_circle:**
- Creates a Circle with 1 member (the echo)
- If circle reaches 3 members → NPC spawned
- Circle can attract other Echos

**propagate_idea:**
- Can create new Echo (daughter echo) with similar essence
- If essence differs enough → mutation/deriva

**write_manifesto:**
- Adds tags to world/echo
- Tags affect future event generation

**ritualize:**
- Can increase echo attributes (clarity, resonance)
- Can reduce pressure (calming effect)

**sabotage:**
- Can reduce enemy faction influence
- Can remove tags from enemies

**talk:**
- Can influence other Echos to join your circle
- Can spread tags

### 4. Echo Spawning System

New Echos should spawn over time:

```python
def maybe_spawn_echo(world: World, turn: int) -> Echo | None:
    """Spawn new echo based on world conditions."""
    # If faction influence > threshold and no recent spawn
    if world.total_influence > 100 and turn - world.last_echo_spawn > 5:
        if random.random() < 0.3:  # 30% chance
            return _create_daughter_echo(world)
    return None
```

### 5. Circle Growth System

Circles grow when:
- Echos nearby take "talk" action
- Echos with matching essence join
- NPC helps recruit

Circles shrink when:
- Members leave (low resonance)
- Circle reaches critical mass and fragments

### 6. Implementation Checklist

1. Add `action_history` list to Echo model
2. Add `last_action_turn` dict to Echo
3. Implement diminishing returns in autoplayer scoring
4. Add `spawn_daughter_echo()` function
5. Add `circle_grow()` trigger on talk action
6. Add `world_tick_effects()` to evolve world state
7. Balance scores so all actions are viable

### 7. Expected Behavior After Fix

**Turn 1-3:** write_manifesto wins (fresh action bonus)
**Turn 4-6:** found_circle starts winning (diminishing returns on write_manifesto)
**Turn 7:** Circle founded with 1 member
**Turn 8-12:** Actions spread between found_circle, talk, propagate_idea
**Turn 13:** Circle has 3 members → NPC spawned
**Turn 15:** Second echo spawns
**Turn 20:** Circles=2, Echoes=2, world evolving

## Status History

- 2026-05-24: draft created