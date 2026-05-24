# 22 - AI-Generated Manifestos with Tag Extraction

## Metadata

- Status: draft
- Created: 2026-05-24
- Depends on: 07 (Actions), 12 (AI Integration)

## Context

Currently `write_manifesto` is a stub that only prints "Wrote manifesto (stub)".
It does nothing functionally - no tags created, no influence gained, no world impact.

The manifesto system should be the primary mechanism for:
- Spreading ideas
- Creating emergent tags
- Building doctrinal clarity
- Converting influence to tangible system effects

## Current State

```python
# game_core/actions/echo_actions.py - WriteManifesto action
def execute(self, context: ActionContext) -> ActionResult:
    return ActionResult(
        success=True,
        message="Wrote manifesto (stub)",
        state_delta={},
        new_entities=[],
        consumed_resources={"social_cost": 5.0}
    )
```

## Proposed Behavior

### 1. AI Manifesto Generation

Use the AI adapter to generate a narrative manifesto:

```
Prompt to AI:
"Write a short manifesto (2-3 paragraphs) in Spanish for a movement
following {echo.essence}. The manifesto should:
- Reflect the core tenets of {echo.essence}
- Include references to ideology tags the echo carries
- Be evocative and persuasive
- End with a rallying cry or slogan

Context: World tick {world_tick}, faction influence {influence}"

Response format: Plain text manifesto
```

### 2. Tag Extraction from Manifesto

After generating the text, extract system tags:

```python
ESSENCE_KEYWORDS = {
    "anarchism": ["libertad", "autonomía", "horizontal", "sin Estado"],
    "technocracy": ["conocimiento", "protocolo", "expertos", "ciencia"],
    "absurdism": ["caos", "nonsense", "absurdo", "carpe diem"],
    "thelema": ["voluntad", "destino", "magia", "gnosis"],
    "ecology": ["naturaleza", "equilibrio", "sustentable", "tierra"],
}

# Search manifesto text for keywords
# Match found keywords → map to system tags
# Create emergent tags if no match found
```

### 3. Effects Applied

If tags extracted:

| Effect | Amount |
|--------|--------|
| +doctrinal_clarity | +0.1 per tag found |
| +influence | +5 per tag found |
| tags_created | list of found/emergent tags |
| social_cost | 5.0 (unchanged) |

If no tags extracted:
- Still creates the manifesto entity
- Minimal effect (+1 influence as acknowledgment)
- Log warning about empty manifesto

### 4. New Entities

```python
# Create Manifesto entity
Manifesto(
    id=str(uuid.uuid4()),
    author_echo_id=echo.id,
    content=generated_text,
    tags=extracted_tags,
    world_tick_created=world.tick,
    essence=echo.essence,
)
```

### 5. Integration Points

- `Echo.manifestos: list[str]` - IDs of manifestos written
- `World.manifestos: list[Manifesto]` - all manifestos in world
- `Faction.ideology_tags` - updated with extracted tags

## Data Model

### Manifesto Entity

```python
class Manifesto(BaseModel):
    id: str
    author_echo_id: str
    content: str  # Generated text (2-3 paragraphs)
    tags: list[str]  # Extracted or emergent tags
    world_tick_created: int
    essence: str  # Echo's essence at time of writing
    influence_generated: float
```

### Update World

```python
class World:
    # Add to existing World model:
    manifestos: list[Manifesto] = Field(default_factory=list)
```

## API Changes

### Action Signature (unchanged)

```python
def execute(self, context: ActionContext) -> ActionResult
```

### ActionResult Changes

```python
ActionResult(
    success=True,
    message=f"Manifesto written with {len(tags)} tags",
    state_delta={
        "manifestos": [manifesto.id],
        "doctrinal_clarity": +0.3,
        "influence": +15.0,
    },
    new_entities=[manifesto],
    consumed_resources={"social_cost": 5.0},
    tags_created=["anti_estado", "horizontalidad"],  # New field
)
```

## AI Adapter Extension

Add to AIAdapter:

```python
def generate_manifesto(self, echo: Echo, world: World) -> str:
    """Generate manifesto text using AI."""
    ...
```

Mock adapter: Return hardcoded manifesto based on essence.

## Testing

```python
def test_write_manifesto_generates_text():
    # Generate manifesto for anarchism echo
    # Assert content length > 200 chars
    # Assert essence keywords present

def test_write_manifesto_extracts_tags():
    # Generate manifesto
    # Assert 1-3 tags extracted
    # Assert tags are in ESSENCE_KEYWORDS or emergent

def test_write_manifesto_effects():
    # Write manifesto
    # Assert +influence
    # Assert +doctrinal_clarity
    # Assert manifesto entity created

def test_write_manifesto_no_tags():
    # Generate with mocked empty response
    # Assert minimal effects (+1 influence)
```

## Acceptance Criteria

- [ ] `write_manifesto` generates 2-3 paragraph text in Spanish
- [ ] Tags extracted from manifesto text appear in action_result.tags_created
- [ ] Influence increases when tags are found
- [ ] Doctrinal clarity increases per tag
- [ ] Manifesto entity created and stored in world
- [ ] Echo.manifestos list updated with manifesto ID
- [ ] Mock adapter returns essence-appropriate text
- [ ] Action fails gracefully if AI unavailable (use fallback text)

## Status History

- 2026-05-24: draft created