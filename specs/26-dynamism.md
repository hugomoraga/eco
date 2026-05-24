# 26 - Narrative Dynamism & Living World

## Metadata

- Status: draft
- Created: 2026-05-24
- Updated: 2026-05-24
- Priority: critical
- Depends on: 19 (MVP)

## Context

Current state: The simulation runs but reads like a spreadsheet, not a story.

```
[Turn 5] ⚡ Evento: "Comunidad libre consume recursos energéticos"
[Turn 6] • Founded circle: Circle of First Echo
[Turn 7] • Founded circle: Circle of First Echo
[Turn 8] • Founded circle: Circle of First Echo
```

**Problems:**
1. Nothing interesting happens between events (5-turn gaps)
2. Actions are stubs - "Founded circle" doesn't mean anything
3. No NPCs, no characters, no voices
4. Tags exist but have no effect
5. Circles are just counters
6. Events don't change anything real
7. No sense of a living world with agency

**Goal:** Every turn should tell part of a story. The console should be readable as a narrative.

## Vision: Turn-by-Turn Narrative

Each turn produces ONE of:
- An **event** with named characters and consequences
- An **action** with specific, named effect
- An **NPC** speaking or acting
- A **state change** explained narratively
- A **discovery** or revelation

**Example desired output:**

```
[Turn 3] 📜 Echoes write manifesto on anarchism in the public square
[Turn 4] 👤 Brother Simón comes forward: "I share this vision" (+3 followers)
[Turn 5] ⚡ CRISIS: "Authorities ban public assembly" → Legitimacy -15
[Turn 6] ⭕ Echo founds Circle of the First Garden (5 members join)
[Turn 7] 👤 Dra. Maela Ruun warns: "This path leads to isolation"
[Turn 8] 📣 Propagandists spread to the eastern districts
[Turn 9] ⭕ Circle grows: The First Garden now has 12 members
[Turn 10] ⚡ EVENT: "The Assembly of Thorns" - 3 factions dispute resources
[Turn 11] 👤 Old Kael whispers: "Remember what happened in Barrias..."
[Turn 12] 📉 Influence of Order: 45 → 38 (-7)
```

## Core Systems to Implement

### 1. Actions with Teeth (Real Effects)

**found_circle:**
- Creates circle with name (AI-generated or formula: "Circle of [Noun]")
- Echo joins as first member
- Other Echos/NPCs can join if nearby
- Circle has essence that can attract/repel

**propagate_idea:**
- Generates tags (already working with AI)
- Tags accumulate in world state
- High tag concentration → events triggered
- Can cause echo to "resonate" and spawn daughter

**write_manifesto:**
- AI generates actual manifesto text (stored in logs)
- Tags extracted → world.tags adds them
- Echo clarity increases

**ritualize:**
- Generates event in current location
- Can increase/decrease local pressure
- Echo resonance attribute changes

**talk:**
- Can recruit NPC or Echo to circle
- NPC may respond with dialogue
- Recorded in narrative

**sabotage:**
- Reduces target faction influence
- Generates counter-event (retaliation)

### 2. Echo Spawning (Daughter Echos)

When conditions met, new Echo spawns:
```
if world.tags['revolutionary'] > 20 and world.circles > 2:
    if random.random() < spawn_chance:
        daughter = create_echo(
            essence=mutate_essence(parent.essence),
            name=generate_name(),
            origin=f" daughter of {parent.name}"
        )
```

**Daughter Echo behaviors:**
- Starts in nearby circle
- Has slight mutation of parent's essence
- Can diverge over time (deriva)
- Has own action preferences

### 3. NPCs (Named Characters)

NPCs spawn from:
- Circle reaching 3+ members
- Talk action with high resonance
- Random events ("wanderer arrives")

**NPC structure:**
```python
class NPC:
    id: str
    name: str  # AI-generated: "Brother Simón", "Dra. Maela Ruun"
    essence: str
    circle_id: str | None
    traits: list[str]  # "skeptical", "zealous", "pragmatic"
    dialogue_history: list[str]
    influence: float  # can affect others
```

**NPC actions:**
- Speak (generates dialogue)
- Join/leave circle
- Influence other NPCs
- Trigger events

### 4. Events with Consequences

Events MUST change something:
```
Event("Authority bans assembly"):
    world.legitimacy -= 10
    world.pressure += 5
    yield "The council's legitimacy crumbles"
```

**Event types:**
- Crisis (negative world change)
- Opportunity (positive world change)
- Revelation (new information/tags)
- Conflict (faction vs faction)
- Convergence (circles merge)

### 5. Tags Accumulation & Effect

Tags in world state:
```python
world.tags: dict[str, float] = {
    "anarchism": 15.0,
    "collectivism": 8.0,
    "mysticism": 3.0,
    "resistance": 12.0,
}
```

**Tag effects:**
- High tag value → events related to tag trigger
- Competing tags → tension events
- Tag mutations → daughter echo essence changes

### 6. World State (Pressure, Legitimacy, Resources)

New world metrics:
```python
world.pressure: float      # civil unrest, 0-100
world.legitimacy: float   # authority trust, 0-100  
world.resources: float    # food/energy, 0-100
```

**Turn evolution:**
- Each turn: pressure += random(-2, +3)
- Events modify these values
- Low legitimacy → more crisis events
- High pressure → events of resistance

## Console Output Specification

**Format per turn:**
```
[Turn N] {emoji} {narrative text}
```

**Emoji meanings:**
- 📜 Action (manifesto, propagate)
- ⭕ Circle founded/grows
- 👤 NPC speaks or acts
- ⚡ Event (crisis, opportunity)
- 📣 Propagation spreading
- 🔮 Ritual performed
- ⚔️ Sabotage/conflict
- 📈/📉 Major state change
- ❌ Failure/retreat
- 🏷️ Tag acquired

**Narrative rules:**
1. Named characters when possible ("Dra. Maela", "Brother Simón")
2. Specific, not generic ("Circle of the Burning Garden" not "Circle #3")
3. Consequence mentioned ("→ Legitimacy -10")
4. Past tense for completed, present for ongoing

## Implementation Phases

### Phase 1: Actions with Teeth (THIS SPEC)
- [ ] found_circle → creates named circle, echo joins
- [ ] propagate_idea → adds tags to world
- [ ] write_manifesto → text + tags + clarity boost
- [ ] ritualize → generates localized event
- [ ] talk → can recruit, generates dialogue
- [ ] sabotage → reduces faction, triggers retaliation

### Phase 2: Living Circles
- [ ] Circles store member list
- [ ] Circle name generation
- [ ] Circle growth mechanism
- [ ] Circle can attract Echos

### Phase 3: NPC System
- [ ] NPC model (name, essence, traits)
- [ ] NPC spawning (circle 3+ members)
- [ ] NPC dialogue generation
- [ ] NPC actions

### Phase 4: World State
- [ ] pressure, legitimacy, resources
- [ ] Turn evolution of metrics
- [ ] Event consequences on metrics

### Phase 5: Echo Spawning
- [ ] Daughter echo creation
- [ ] Essence mutation
- [ ] Spawn conditions

### Phase 6: Narrative Console
- [ ] Per-turn narrative output
- [ ] Named characters in output
- [ ] Consequence reporting
- [ ] Story coherence

## Status History

- 2026-05-24: draft created (was about diminishing returns)
- 2026-05-24: updated - complete rewrite for narrative dynamism
