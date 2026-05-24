# 20 - Integration: Connect Disconnected Systems

## 20.1 Context

Several systems were implemented but not connected to the simulation loop:

- `game_core/domain/essence_effects.py` - EssenceEffects
- `game_core/engine/pressure.py` - DerivePressureCalculator
- `game_core/engine/event_generator.py` - EventGenerator
- `game_core/domain/npc_generator.py` - NPCGenerator

The simulation runs but these modules are never called.

## 20.2 Goal

Connect all 4 systems to the simulation loop so the game becomes more dynamic and interesting to watch.

## 20.3 Current State

```
simulation.py
  └── FactionTickSystem (actions/echo_actions.py)
        └── FactionTickSystem.execute_action()
              └── spread_doctrine (always, same score)
```

All new systems are dead code.

## 20.4 Integration Points

### 20.4.1 DerivePressureCalculator → FactionTickSystem

**Where:** `FactionTickSystem.execute_action()`

**Current:** Score is constant (31.66)

**New:** Score is modulated by DerivePressureCalculator:

```python
from game_core.engine.pressure import DerivePressureCalculator

# In FactionTickSystem.execute_action()
pressure = DerivePressureCalculator.calculate_faction_pressure(faction, world)
score_modifier = 1.0 + (pressure.total_pressure / 100.0)
adjusted_score = base_score * score_modifier
```

**Effect:** Factions with high pressure take more aggressive actions.

### 20.4.2 EssenceEffects → Interactions

**Where:** Actions that affect other entities (propagate_idea, sabotage, talk)

**Current:** No essence influence

**New:** Essence affinity modifies action outcomes:

```python
from game_core.domain.essence_effects import EssenceEffects

# In propagate_idea or similar
essence = target_circle.primary_essence
affinity = EssenceEffects.get_affinity(action_source_essence, essence)
# affinity > 0 = bonus, < 0 = penalty
effective_success_rate = base_rate * (1.0 + affinity * 0.5)
```

### 20.4.3 EventGenerator → Simulation Loop

**Where:** `SimulationEngine._tick()` after actions are processed

**Current:** No events

**New:** Events fire based on conditions:

```python
from game_core.engine.event_generator import EventGenerator

# In SimulationEngine._tick()
event_gen = EventGenerator(world_state)
possible_events = event_gen.generate(turn=current_turn)
for event in possible_events:
    if event.should_fire():
        event.apply()
        self._log_event(event)
```

**Trigger conditions:**
- Resource scarcity → economic events
- High pressure → social upheaval events
- Circle growth → expansion events
- Essence concentration → ideological events

### 20.4.4 NPCGenerator → Circle Growth

**Where:** When a circle reaches certain size threshold

**Current:** No NPCs generated

**New:** NPCs spawn when circles grow:

```python
from game_core.domain.npc_generator import NPCGenerator

# In Circle.update() or when circle membership changes
if circle.member_count >= NPCGenerator.SPAWN_THRESHOLD:
    npc = NPCGenerator.generate(circle.essence_affinity)
    circle.add_member(npc)
```

**NPC spawn threshold:** 3 members

## 20.5 Implementation Order

1. **DerivePressureCalculator** - easiest, affects FactionTickSystem
2. **EssenceEffects** - modifies existing action outcomes
3. **EventGenerator** - new event loop layer
4. **NPCGenerator** - spawn on circle growth

## 20.6 Test Criteria

After integration, running:
```bash
uv run python game_core/run.py --seed 42 --turns 50 --autoplay
```

Should show in `simulation.jsonl`:
- `faction_tick` events with varying scores (not constant 31.66)
- `event` events (at least 1-2 per 10 turns)
- `npc_created` or NPCs in snapshot
- Action outcomes influenced by essence affinity

## 20.7 Files to Modify

- `game_core/engine/simulation.py` - add EventGenerator call
- `game_core/engine/faction_tick.py` - integrate DerivePressureCalculator
- `game_core/actions/echo_actions.py` - integrate EssenceEffects
- `game_core/domain/circle.py` - integrate NPCGenerator

## 20.8 Files NOT to Modify

Do not refactor the 4 disconnected modules themselves. They are fine. Only connect them.

---

## Metadata

- Version: 0.1.0
- Created: 2026-05-24
- Status: draft
- Depends on: specs 04, 09, 13
- Blocks: spec-11 (autoplayer needs events + pressure)
