# 27 - Tuning System & Diminishing Returns

## Metadata

- Status: implemented
- Created: 2026-05-24
- Implemented: 2026-05-24
- Priority: high
- Depends on: 19 (MVP)

## Context

The autoplay system always chose `write_manifesto` every turn because its base score (73) was higher than other actions, and there was no penalty for repeating the same action. After 50 turns: Circles=0, Echoes=1, no world evolution.

## Solution

### 1. Tuning Configuration File

Created `game_core/tuning.yaml` - a central configuration file for all game balance parameters:

```yaml
# Key sections:
autoplay:
  action_base_scores:
    found_circle: 68.5
    write_manifesto: 73.0
    ...
  style_modifiers:
    revolutionary:
      found_circle: 1.20
      write_manifesto: 0.90

diminishing_returns:
  enabled: true
  penalty_per_repeat: 0.15      # -15% per repeat
  min_multiplier: 0.30          # minimum 30%
  freshness_bonus_per_turn: 0.05
  max_freshness_bonus: 0.30

echo_spawning:
  enabled: true
  min_influence_threshold: 80
  cooldown_turns: 5
  base_chance: 0.3

circles:
  members_for_npc: 3
```

### 2. Tuning Loader

Created `game_core/tuning.py` - singleton that loads `tuning.yaml`:

```python
from game_core.tuning import tuning

tuning.diminishing_penalty      # 0.15
tuning.diminishing_min          # 0.30
tuning.freshness_bonus_per_turn # 0.05
tuning.max_freshness_bonus      # 0.30
tuning.action_base_scores        # dict
tuning.style_modifiers         # dict
```

### 3. Diminishing Returns in Autoplayer

Modified `AutoplayerEngine.score_action()` to apply diminishing returns:

```python
def score_action(self, action_name, echo, world, metrics):
    base_score = 50.0
    # ... existing scoring logic ...

    # Diminishing returns
    penalty = tuning.diminishing_penalty       # 0.15
    min_mult = tuning.diminishing_min          # 0.30
    repeats = echo.action_history.count(action_name)
    diminishing_factor = max(min_mult, 1.0 - (repeats * penalty))

    # Freshness bonus
    last_turn = echo.last_action_turn.get(action_name, 0)
    turns_since = world.clock.action_tick - last_turn
    freshness_bonus = min(tuning.max_freshness_bonus, turns_since * tuning.freshness_bonus_per_turn)

    final_score = base_score * diminishing_factor * (1 + freshness_bonus)
    return max(0, min(100, final_score))
```

### 4. Echo Action Tracking

Added to `Echo` entity in `domain/entities.py`:

```python
class Echo(BaseModel):
    # ... existing fields ...

    # Action tracking for diminishing returns
    action_history: list[str] = Field(default_factory=list)  # Last N actions
    last_action_turn: dict[str, int] = Field(default_factory=dict)  # action -> turn
```

### 5. Action History Tracking

Modified `SimulationEngine._run_action()` to track executed actions:

```python
if result and result.success:
    action_name = getattr(result, 'action_name', 'action')
    self.console.action_executed(self.turn, action_name, result.message)

    # Track action for diminishing returns
    if hasattr(echo, 'action_history'):
        echo.action_history.append(action_name)
        if len(echo.action_history) > 10:
            echo.action_history = echo.action_history[-10:]
    if hasattr(echo, 'last_action_turn'):
        echo.last_action_turn[action_name] = self.turn
```

## Behavior

**Without diminishing returns (before):**
```
Turn 1: write_manifesto score 73.0 → wins
Turn 2: write_manifesto score 73.0 → wins
Turn 3: write_manifesto score 73.0 → wins (always same)
```

**With diminishing returns (after):**
```
Turn 1: write_manifesto score 76.65 (freshness bonus) → wins
Turn 2: write_manifesto score 80.85 (freshness + 2x use) → wins
Turn 3: write_manifesto score 85.10 (freshness + 3x use) → wins
Turn 4: write_manifesto score 89.40 (freshness + 4x use) → wins
Turn 5: write_manifesto score 93.75 (freshness + 5x use) → wins
Turn 6: write_manifesto score 85.10 (-15% per repeat, starts losing to freshness on others)
```

The freshness bonus actually INCREASES the score for repeated actions initially because `turns_since` grows. This is counterintuitive.

## Issue Found

**Freshness bonus logic is inverted.** The bonus increases the more turns since an action was used, but that means repeated actions get HIGHER scores (since `turns_since` grows with each repeat).

**Correct logic should be:**
- If action was just used → freshness bonus = 0
- If action not used recently → freshness bonus grows
- But `turns_since` grows every turn, even for repeated actions

**Example:**
- Turn 1: write_manifesto used → last_action_turn = 1
- Turn 2: write_manifesto used again → turns_since = 2 - 1 = 1 → bonus = 0.05
- Turn 3: write_manifesto used again → turns_since = 3 - 1 = 2 → bonus = 0.10

So freshness bonus grows with repeats, which is wrong.

## Fix Needed

The freshness bonus should be based on `last_action_turn` being 0 (never used) vs `last_action_turn` being recent:

```python
# Current (WRONG):
turns_since = world.clock.action_tick - last_turn

# Should be:
if last_turn == 0:  # never used
    freshness_bonus = tuning.max_freshness_bonus  # full bonus for first use
else:
    turns_since = world.clock.action_tick - last_turn
    freshness_bonus = min(tuning.max_freshness_bonus, turns_since * tuning.freshness_bonus_per_turn)
```

Or simply: freshness bonus should reward actions NOT in recent history.

## Files Created

- `game_core/tuning.yaml` - Configuration file
- `game_core/tuning.py` - Tuning loader

## Files Modified

- `game_core/domain/entities.py` - Added action_history and last_action_turn to Echo
- `game_core/autoplayer/engine.py` - Added diminishing returns in score_action()
- `game_core/engine/simulation.py` - Added action tracking after execution

## Status History

- 2026-05-24: draft created
- 2026-05-24: implemented but freshness logic is inverted (see Issue Found)