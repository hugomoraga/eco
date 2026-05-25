# SPEC-40: Event Categorization & Essence-Driven Events

## Status
- Created: 2026-05-24
- MVP: YES
- Tags: events, essence, categorization

## Overview

Reemplazar el sistema de eventos hardcodeado (2 fallback events) con un pool categorizado de 100 eventos. Cada evento tiene derivación por esencia: el tipo de esencia dominante en el mundo influye en qué categoría de evento es más probable. AI solo enriquece flavor text, no define estructura.

## Architecture

### Data Files

```
game_core/data/events.yaml        # 100 eventos categorizados
game_core/i18n/es.yaml            # traducciones español
game_core/i18n/en.yaml            # traducciones inglés
```

### Event Categories (6)

| Category   | Trigger Condition                              | Essence Affinity            |
|------------|----------------------------------------------|------------------------------|
| CRISIS     | pressure > 70 OR legitimacy < 25            | anarchism, absurdism         |
| RITUAL     | circles with ritual flag OR ritual_tick > 0   | thelema, absurdism           |
| POLITICAL  | legitimacy < 40 OR factions > 2              | technocracy, anarchism       |
| DISCOVERY  | knowledge > 60 OR innovation events          | technocracy, ecology         |
| SOCIAL     | circle.splinter OR member_count changes       | anarchism, ecology           |
| ENTROPY    | decay_tick > 3 OR memory_depth < 20          | absurdism, thelema            |

### Event Structure

```yaml
events:
  crisis_protest_001:
    category: CRISIS
    essence_weights:
      anarchism: 1.5
      absurdism: 1.2
      thelema: 0.5
    choices:
      - label: "events:crisis_protest_001:support"
        effect_tags: ["increase_unrest", "increase_anarchism"]
      - label: "events:crisis_protest_001:suppress"
        effect_tags: ["increase_technocracy", "lower_productivity"]
```

### Essence Weight Calculation

When selecting event category:
1. Get dominant essence from world state (weighted by echo essences)
2. For each category, sum: `base_weight + essence_weight_modifier`
3. Pick category with highest weighted score
4. Pick random event from that category's pool

```python
# Example
dominant = "anarchism"  # from world state
category_weights = {
    "CRISIS":   base 0.3 + anarchism 0.4 = 0.7,
    "RITUAL":   base 0.2 + anarchism 0.1 = 0.3,
    "POLITICAL": base 0.2 + anarchism 0.3 = 0.5,
    ...
}
selected_category = max(category_weights, key=category_weights.get)
```

## Event Pool (100 Events)

### CRISIS (18 events)
1. crisis_protest_001..006
2. crisis_shortage_001..004
3. crisis_breakdown_001..004
4. crisis_panic_001..004

### RITUAL (17 events)
5. ritual_gathering_001..005
6. ritual_initiation_001..004
7. ritual_ transgression_001..004
8. ritual_sacrifice_001..004

### POLITICAL (17 events)
9. political_alliance_001..005
10. political_betrayal_001..004
11. political_reform_001..004
12. political_collapse_001..004

### DISCOVERY (16 events)
13. discovery_tech_001..004
14. discovery_memory_001..004
15. discovery_network_001..004
16. discovery_nature_001..004

### SOCIAL (16 events)
17. social_formation_001..004
18. social_fission_001..004
19. social_conflict_001..004
20. social_harmony_001..004
21. social_exclusion_001..004

### ENTROPY (16 events)
22. entropy_decay_001..004
23. entropy_forgetting_001..004
24. entropy_corruption_001..004
25. entropy_phantom_001..004

## Code Changes

### 1. game_core/engine/event_pool.py (NEW)

```python
class EventPool:
    def __init__(self, events_path: str = "game_core/data/events.yaml"):
        self.events = self._load_events(events_path)
        self.categories = self._build_category_index()

    def select_category(self, world_state: dict, essence_distribution: dict) -> str:
        # Calculate weights per category
        # Return highest weighted category

    def select_event(self, category: str) -> dict:
        # Pick random from category pool

    def get_event_data(self, event_id: str) -> dict | None:
        # Return full event data for i18n lookup
```

### 2. game_core/engine/event_generator.py (MODIFY)

- Remove hardcoded fallback events
- Add `EventPool` dependency
- `generate()` calls `pool.select_category()` → `pool.select_event()`
- AI adapter only for flavor text enrichment (optional)
- If AI fails, use selected event directly (no fallback pool)

### 3. game_core/domain/entities.py (MODIFY)

Add `EventCategory` enum:
```python
class EventCategory(str, Enum):
    CRISIS = "crisis"
    RITUAL = "ritual"
    POLITICAL = "political"
    DISCOVERY = "discovery"
    SOCIAL = "social"
    ENTROPY = "entropy"
```

### 4. i18n files (MODIFY)

Add translations for all 100 events × 2 languages.
Format: `events:<event_id>:title`, `events:<event_id>:summary`, `events:<event_id>:<choice_key>`

## i18n Translation Keys

```
events:
  <event_id>:
    title: "..."
    summary: "..."
    choices:
      - "Choice text..."
        effects: ["tag1", "tag2"]
```

## Integration Points

- `EventGenerator.__init__(adapter, pool=None)` - pool injected
- `simulation.py` - no changes needed, EventGenerator interface unchanged
- `world_state` passed to `generate(context)` includes `essence_distribution`, `pressure`, `legitimacy`, etc.

## Testing

1. Verify 100 events load from YAML
2. Verify category selection respects essence weights
3. Verify all events have valid i18n keys
4. Verify AI adapter can enrich but not block
5. Run `audit_consolidated.py` and `test_integration.py`

## Dependencies

- SPEC-36 (Player Input) not required
- All other systems independent

## Files to Create/Modify

| File | Action |
|------|--------|
| `game_core/data/events.yaml` | CREATE (100 events) |
| `game_core/engine/event_pool.py` | CREATE |
| `game_core/engine/event_generator.py` | MODIFY |
| `game_core/domain/entities.py` | MODIFY (add EventCategory enum) |
| `game_core/i18n/es.yaml` | MODIFY (add event translations) |
| `game_core/i18n/en.yaml` | MODIFY (add event translations) |
| `scripts/audit_consolidated.py` | RUN after changes |
| `scripts/test_integration.py` | RUN after changes |

## Notes

- 100 events in YAML is large; use anchor/alias for repeated choice patterns
- effect_tags validation still uses `EffectTagValidator`
- Events with `choices: []` are auto-resolved (no player choice)
- Each event MUST have at least 2 choices for player agency