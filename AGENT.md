# AGENT.md

Rules and conventions for ECO project development.

---

## 1. Philosophy

### 1.1 Spec-Driven Development

Every code change must be preceded by a spec change. Code implementing a non-existent spec is technical debt.

```txt
Correct flow:
  spec-XX.md → implement → code

Incorrect flow:
  code → adjust spec (going backwards)
```

### 1.2 Observability First

The system must be debuggable from day zero. Logs, replay, inspector always available.

### 1.3 Simplicity

KISS on every decision. If a solution is complex, it's probably wrong.

### 1.4 Reproducibility

Every simulation with the same seed must produce the same result. No side effects, no hidden global state.

---

## 2. Project Structure

```
/eco
├── SPEC.md                    # Specs index
├── specs/                     # Specifications
│   ├── 00-index.md
│   ├── 01-architecture.md
│   └── ...
├── game-core/                 # Headless engine
│   ├── engine/                 # Core engine
│   ├── domain/                 # Domain entities
│   ├── ai/                     # AI adapters
│   ├── autoplayer/             # Autoplayer
│   ├── data/                   # YAML data
│   ├── schemas/                # JSON schemas
│   ├── tests/                  # Tests
│   └── runs/                   # Logs and snapshots
├── godot-client/              # Godot client (future)
├── AGENT.md                    # This file
└── README.md
```

---

## 3. Code Conventions

### 3.1 Naming

**Files and modules:**
```python
# Modules: snake_case
world.py
player_echo.py
temporal_system.py

# Classes: PascalCase
class World:
class PlayerEcho:
class TemporalSystem:

# Functions and variables: snake_case
def calculate_derive_pressure()
def get_available_actions()
current_year = 47
```

**Constants:**
```python
# All uppercase with underscore
MAX_CLARITY = 100
DEFAULT_SEED = 42
TICK_THRESHOLDS = {...}
```

**IDs and references:**
```python
# Entity IDs: snake_case with underscores
entity_id = "protocolos_autonomos"
doctrine_id = "doctrine_protocolos_autonomos"

# Data file names: snake_case
essences.yaml
actions.yaml
event_templates.yaml
```

### 3.2 Python File Structure

```python
"""
Domain module for [functionality].

Brief description of the module's purpose.
"""

from __future__ import annotations

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


# Module constants
DEFAULT_VALUE = 50
MAX_LIMIT = 100


@dataclass
class ExampleEntity:
    """Entity representing [concept].

    Args:
        id: Unique identifier
        name: Human-readable name
        value: Attribute value
    """

    id: str
    name: str
    value: int = DEFAULT_VALUE
    metadata: Dict[str, Any] = field(default_factory=dict)

    def method(self, param: int) -> bool:
        """Method that does [thing].

        Args:
            param: Parameter description

        Returns:
            True if operation successful, False otherwise.

        Raises:
            ValueError: If param is negative.
        """
        if param < 0:
            raise ValueError("param must be non-negative")
        return True


class ExampleService:
    """Service for [functionality].

    Usage:
        service = ExampleService()
        result = service.process()
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self._internal_state = {}

    def process(self, data: str) -> Dict[str, Any]:
        """Process data and return result.

        Args:
            data: Input to process

        Returns:
            Dict with result and metadata.
        """
        result = {"status": "ok", "data": data.upper()}
        return result
```

### 3.3 Imports

```python
# Import order
# 1. Built-in
from __future__ import annotations
import os
import sys
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

# 2. Third-party
import yaml
from pydantic import BaseModel, Field

# 3. Local
from domain.entity import Entity
from engine.world_clock import WorldClock

# 4. Relative imports for clarity
from .player_echo import PlayerEcho
from ..domain.city import City
```

### 3.4 Docstrings

**Modules:**
```python
"""Domain module for [domain].

More detailed description of the module's purpose and content.
Includes notes on usage and limitations.
"""
```

**Classes:**
```python
class MyClass:
    """Brief description of the class.

    More detailed description if necessary,
    including usage notes.

    Attributes:
        attr1: Description of attribute 1.
        attr2: Description of attribute 2.
    """
```

**Methods/Functions:**
```python
def function(param1: str, param2: int = 10) -> bool:
    """Brief description of what the function does.

    More detailed description if necessary,
    including edge cases.

    Args:
        param1: Description of the first parameter.
        param2: Description of the second parameter (default: 10).

    Returns:
        True if successful, False otherwise.

    Raises:
        ValueError: If [condition].
        TypeError: If [condition].

    Example:
        >>> result = function("test", 5)
        >>> print(result)
        True
    """
```

### 3.5 Type hints

```python
# Always use complete type hints
def process(data: List[Dict[str, Any]]) -> Optional[PlayerEcho]:
    ...

# For complex types, use aliases
WorldState = Dict[str, Any]
EntityID = str
EssenceValue = int  # 0-100

def calculate(state: WorldState, entity_id: EntityID) -> EssenceValue:
    ...
```

---

## 4. Git Workflow

### 4.1 Branches

```txt
main                  # Stable, deployable code
├── develop           # Feature integration
│   ├── spec-XX/...   # Feature branches per spec
│   └── hotfix/...     # Urgent fixes
```

**Naming:**
```bash
# Feature specs
spec-05/virality-mechanism
spec-09/economy-integration

# Hotfixes
hotfix/fix-derive-pressure-overflow

# Format: type/descriptive-name
```

### 4.2 Commits

**Format:**
```
<type>(<scope>): <description>

<optional body with context>

<optional footer with metadata>
```

**Types:**
```txt
feat: new functionality
fix: bug fix
docs: documentation changes (includes specs)
refactor: refactoring without behavior change
test: adding or modifying tests
chore: build system, tooling, dependency updates
```

**Rules:**
- Atomic commits: one change = one commit
- Clear and descriptive message
- Do not commit code that breaks tests
- Do not commit secrets or local config

**Examples:**
```bash
feat(domain): add PlayerEcho entity with identity attributes

- clarity, resonance, presence, memory, will, shadow
- inheritance system between incarnations
- persistence formulas based on will

Closes: #spec-03

fix(engine): correct overflow in derive_pressure formula

The previous formula used pressure multiplication
which could overflow. Now uses weighted sum instead.

Fixes: #runtime-issue-42
```

### 4.3 Workflow Process

```bash
# 1. Create branch from develop
git checkout develop
git pull origin develop
git checkout -b spec-05/virality-mechanism

# 2. Work with small commits
git add src/domain/idea.py
git commit -m "feat(domain): add Idea structure with virality"

# 3. Keep branch updated
git fetch origin
git rebase origin/develop  # If conflicts, resolve before push

# 4. Push and create PR
git push -u origin spec-05/virality-mechanism
# Create PR on GitHub/Gitea with description

# 5. Review and merge
# Wait for approval, resolve comments, merge to develop
```

### 4.4 Code Review

**For PR author:**
- Self-review before requesting review
- Clear description of the change
- Links to related specs
- Screenshot or logs if applicable
- Tests passing

**For reviewer:**
- Review logic, not just style
- Verify related specs
- Test locally if possible
- Constructive comments
- Approve or request changes

**Review checklist:**
```txt
□ Code follows conventions
□ Tests sufficient and passing
□ Specs updated if necessary
□ No unexpected side effects
□ Logs and replay work
□ Documentation updated
□ Type hints complete
```

---

## 5. Testing

### 5.1 Framework

**pytest** for everything:
```bash
# Run all tests
pytest

# Run specific file
pytest tests/test_ideological_drift.py

# Run with coverage
pytest --cov=engine --cov-report=html

# Run with verbose output
pytest -v

# Run specific pattern
pytest -k "test_derive"
```

### 5.2 Test Structure

```python
"""
Tests for the [domain] module.

Location: tests/test_<module>.py
"""

import pytest
from domain.idea import Idea, ViralityCalculator


class TestIdea:
    """Tests for the Idea class."""

    def test_create_idea_with_defaults(self):
        """Test creation with default values."""
        idea = Idea(id="test_idea", name="Test Idea")
        assert idea.clarity == 50
        assert idea.virality == 50
        assert idea.stability == 50

    def test_create_idea_with_custom_values(self):
        """Test creation with custom values."""
        idea = Idea(
            id="custom_idea",
            name="Custom Idea",
            clarity=80,
            virality=60
        )
        assert idea.clarity == 80
        assert idea.virality == 60

    def test_virality_threshold_calculation(self):
        """Test virality threshold calculation."""
        calculator = ViralityCalculator()
        assert calculator.get_threshold(80) == "mass"

    @pytest.mark.parametrize("virality,expected_threshold", [
        (15, "insular"),
        (35, "local"),
        (55, "regional"),
        (75, "mass"),
        (95, "pandemic"),
    ])
    def test_virality_thresholds(self, virality, expected_threshold):
        """Test parametrized for all thresholds."""
        calculator = ViralityCalculator()
        assert calculator.get_threshold(virality) == expected_threshold


class TestViralityCalculator:
    """Tests for ViralityCalculator."""

    def test_modifiers_applied(self):
        """Test that modifiers are applied correctly."""
        # Setup
        idea = Idea(id="test", name="Test", virality=50)
        speaker_resonance = 70

        # Execute
        result = ViralityCalculator.calculate_with_modifiers(
            idea.virality,
            speaker_resonance=speaker_resonance
        )

        # Verify
        assert result > 50  # Speaker resonance should add

    def test_opposite_essence_penalty(self):
        """Test that opposite essences penalize."""
        idea = Idea(id="test", name="Test", virality=60)
        result = ViralityCalculator.calculate_with_modifiers(
            idea.virality,
            opposite_essence_dominant=True
        )
        assert result < 60


class TestReproducibility:
    """Tests for reproducibility."""

    def test_same_seed_same_result(self):
        """Test that same seed produces same result."""
        from engine.simulation import Simulation

        sim1 = Simulation(seed=42)
        result1 = sim1.run(turns=10)

        sim2 = Simulation(seed=42)
        result2 = sim2.run(turns=10)

        assert result1 == result2
```

### 5.3 Test Location

```txt
/tests
  test_world.py           # Tests for world.py
  test_idea.py            # Tests for idea.py
  test_ideological_drift.py
  test_autoplayer.py
  test_temporal.py
  test_serialization.py    # JSON/snapshot tests
  fixtures/               # Test data
    essence_fixture.yaml
    actions_fixture.yaml
```

### 5.4 Fixtures

```python
# conftest.py
import pytest
import yaml


@pytest.fixture
def karax_civilization():
    """Fixture with test civilization."""
    return {
        "id": "karax",
        "name": "Nodo Libre Kárax",
        "essences": {
            "anarchism": 65,
            "technocracy": 35
        }
    }


@pytest.fixture
def sample_idea():
    """Fixture with test idea."""
    return Idea(
        id="idea_test",
        name="Test Idea",
        clarity=60,
        virality=55
    )


@pytest.fixture
def valid_essences_yaml():
    """Load essences.yaml for tests."""
    with open("game-core/data/essences.yaml") as f:
        return yaml.safe_load(f)
```

### 5.5 Minimum Coverage

```bash
# Target: 80% minimum coverage on core modules
pytest --cov=game-core --cov-fail-under=80
```

---

## 6. Spec-Driven Development

### 6.1 Process

```txt
1. IDENTIFY need
   → New functionality or change detected

2. CREATE/UPDATE SPEC
   → Create spec-XX.md or modify existing
   → Document: vision, structure, formulas, examples
   → Add metadata notes (origin, dependencies)
   → Update 00-index.md if applicable

3. IMPLEMENT
   → Code follows spec
   → Tests follow spec
   → Update README if necessary

4. VERIFY
   → Tests passing
   → Spec matches implementation
   → Reproducibility verified

5. COMMIT
   → docs(spec): description of change
   → Include link to spec in commit message
```

### 6.2 Spec Checklist

When creating or modifying a spec:

```txt
□ Clear and concise vision
□ Complete data structure (YAML/JSON example)
□ Defined formulas (no ambiguity)
□ Edge cases considered
□ Dependencies declared
□ Metadata updated (origin, date, status)
□ Index updated (if applicable)
□ KISS respected (no over-engineering)
□ Concrete examples
□ Debugging mandatory documented
```

### 6.3 Spec Versioning

```yaml
# In each spec's Metadata
version: "1.0.0"  # Major.Minor.Patch
changelog:
  - "1.0.0": "Initial version"
  - "1.1.0": "Added virality mechanism"
  - "1.2.0": "Fixed derive_pressure formula"
```

### 6.4 Spec States

```txt
🔄 In progress  → Being actively edited
✅ Completed    → Implementation complete and verified
⚠️ Deprecated   → Obsolete, do not use
📌 Blocked      → Waiting on dependencies
```

---

## 7. Available Commands

### 7.1 Core Commands

```bash
# Run simulation
python game-core/run.py --seed 42 --turns 50
python game-core/run.py --seed 42 --turns 50 --autoplay

# Inspect run
python game-core/inspect.py --run runs/run_0001.jsonl --entity karax
python game-core/inspect.py --run runs/run_0001.jsonl --doctrine doctrine_protocolos_autonomos

# Replay
python game-core/replay.py --run runs/run_0001.jsonl --turn 1:100
python game-core/replay.py --run runs/run_0001.jsonl --from-turn 50

# Debug tools
python game-core/debug.py --trace runs/run_0001.jsonl
python game-core/debug.py --explain-transition host_044

# Generate documentation
python game-core/generate_docs.py
```

### 7.2 Data Commands

```bash
# Validate YAML data
python -c "import yaml; yaml.safe_load(open('game-core/data/essences.yaml'))"

# Export entities
python game-core/export_entities.py --type idea --format json

# Import test data
python game-core/load_fixtures.py --dir tests/fixtures
```

### 7.3 Testing Commands

```bash
# Run all tests
pytest

# Run specific module
pytest tests/test_ideological_drift.py -v

# Run with coverage
pytest --cov=game-core --cov-report=term-missing --cov-fail-under=80

# Run specific pattern
pytest -k "test_derive"

# Update snapshots (for serialization tests)
pytest --snapshot-update

# Linter
ruff check game-core/
ruff format game-core/

# Type check
mypy game-core/
```

### 7.4 Git Commands

```bash
# Status
git status
git log --oneline -10

# Branch
git branch -a
git checkout develop

# Commit
git add -p  # Add changes interactively
git commit -m "feat(scope): description"

# Update
git fetch origin
git pull origin develop

# Push
git push -u origin spec-XX/feature-name
```

### 7.5 Docker (if applicable)

```bash
# Build
docker build -t eco-engine:latest .

# Run tests in container
docker run --rm eco-engine:latest pytest

# Run simulation
docker run --rm eco-engine:latest python run.py --seed 42 --turns 50
```

---

## 8. Debugging

### 8.1 Logging

```python
import logging

logger = logging.getLogger(__name__)

def process_action(action):
    logger.info(f"Processing action: {action.id}")
    logger.debug(f"Action details: {action.__dict__}")

    try:
        result = execute_action(action)
        logger.info(f"Action successful: {action.id}")
        return result
    except Exception as e:
        logger.error(f"Action failed: {action.id}, error: {e}")
        raise
```

### 8.2 Log Levels

```python
# For debugging
logger.debug("detailed info")
logger.info("general info")
logger.warning("something might be wrong")
logger.error("something failed")
```

### 8.3 Debug Mode

```bash
# Run with verbose logging
python run.py --seed 42 --turns 10 --log-level trace

# Available levels: minimal, standard, verbose, trace
```

---

## 9. Logging Standards

### 9.1 JSONL Log Format

```json
{
  "timestamp": "2026-05-24T12:34:56Z",
  "level": "INFO",
  "turn": 47,
  "year": 47,
  "phase": "action_processed",
  "logger": "engine.action",
  "message": "Action executed",
  "data": {
    "action_id": "found_circle",
    "target": "district_open_labs_east",
    "effects_applied": {
      "technocracy": 8,
      "anarchism": -3
    }
  }
}
```

### 9.2 Log Rotation

- Logs in `runs/` directory
- One file per run (JSONL)
- Snapshots in `runs/snapshots/`
- Rotation: keep last 100 runs

---

## 10. Error Handling

### 10.1 Custom Exceptions

```python
class EcoError(Exception):
    """Base exception for ECO."""
    pass


class ConfigurationError(EcoError):
    """System configuration error."""
    pass


class ValidationError(EcoError):
    """Data validation error."""
    pass


class SimulationError(EcoError):
    """Error during simulation."""
    pass


class ReplayError(EcoError):
    """Error during replay."""
    pass
```

### 10.2 Usage

```python
def load_config(path: str) -> dict:
    if not os.path.exists(path):
        raise ConfigurationError(f"Config file not found: {path}")

    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Invalid YAML: {e}")
```

---

## 11. Performance

### 11.1 Profiling

```bash
# Profile simulation
python -m cProfile -o output.prof game-core/run.py --seed 42 --turns 100

# Analyze profile
python -m pstats output.prof

# Or use py-spy
py-spy record -- python game-core/run.py --seed 42 --turns 50
```

### 11.2 Benchmarks

```bash
# Run benchmarks
pytest benchmarks/

# Benchmark specific
python benchmarks/benchmark_simulation.py --iterations 100
```

---

## 12. CI/CD (Futuro)

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -e .
      - run: pytest --cov=game-core --cov-fail-under=80
      - run: ruff check game-core/
      - run: mypy game-core/
```

---

## 13. Conventions Summary

| Category | Convention |
|----------|------------|
| Files | `snake_case.py` |
| Classes | `PascalCase` |
| Functions | `snake_case()` |
| Constants | `UPPER_SNAKE_CASE` |
| IDs | `snake_case` |
| Types | `PascalCase` o aliases |
| Tests | `test_<module>.py` |
| Commits | `<type>(<scope>): <description>` |
| Branches | `type/description` |

---

## 14. Character Encoding

### 14.1 ASCII Standard Only

All code and documentation must use only printable ASCII characters.

**Rules:**
- File names: only `a-z`, `0-9`, `_`, `-`
- Variables and functions: snake_case in English
- Comments and docstrings: English without accents
- Strings in code: English, no special characters
- Documentation (SPEC.md, README.md, AGENT.md): ASCII only

**Forbidden:**
```txt
# DO NOT use:
á, é, í, ó, ú (accents)
ñ, ü
comments in Spanish
variable names in Spanish
Chinese, Japanese, Arabic characters, etc.
emojis in code or docs
```

**Allowed:**
```python
# English only
def calculate_derive_pressure(material, social, institutional, temporal):
    """Calculate ideological pressure from structural tension."""
    pass

def get_available_actions(entity):
    """Return list of actions for entity."""
    actions = ["talk", "write_manifesto", "found_circle"]
    return actions
```

### 14.2 Exceptions: Narrative Content

Narrative content MAY use other languages (Spanish, etc.):

- **Character names:** "Dra. Maela Ruun", "Saira Vel"
- **Dialogues:** `"¿Vienes a destruir el laboratorio o a entenderlo?"`
- **Event logs:** `"Las caravanas dejaron de cruzar el corredor norte"`
- **Location descriptions:** `"El edificio no tiene puerta principal"`
- **Narrative snapshots:** content of `narrative` field
- **YAML test data:** NPC archetypes, location descriptions

**Rule:** If it's in `data/`, `runs/`, `snapshots/`, or is system output -> can be narrative in any language. If it's code, variables, comments, specs -> ASCII only.

### 14.3 Verification

```bash
# Verify no non-ASCII in code
grep -r '[^[:print:][:space:]]' game-core/ --include="*.py"

# In docs
grep -r '[^[:print:][:space:]]' *.md specs/

# In YAML data (exclude narrative)
grep -r '[^[:print:][:space:]]' game-core/data/ --include="*.yaml"
```

### 14.4 Exceptions

- Test data (YAML with character names)
- Narrative content in logs/snapshots (not code)
- UI strings in Godot (handled by client)

---

## 15. Spec Evolution and Bifurcation

### 15.1 Branching Approaches (Same Spec)

When two different approaches need to be validated for the same spec:

```
spec-05/virality-mechanism      # Approach A
spec-05/virality-alternative    # Approach B
```

**Workflow:**
1. Each approach gets its own branch from `develop`
2. Implement and validate each independently
3. Merge the winner, discard the other

```bash
# Discard the losing approach
git branch -d spec-05/virality-alternative
git push origin --delete spec-05/virality-alternative
```

In the winning PR body, document why the other approach was discarded.

### 15.2 Refactoring an Existing Spec

Never modify a spec after it has been merged. Create a new one instead.

```
spec-16.md  →  "Refactor of spec-05: virality v2"
```

At the top of the new spec:
```markdown
---
Supersedes: spec-05
Related: spec-05 (deprecated)
---
```

Mark the old spec as deprecated in its metadata:
```markdown
## Metadata

- Status: 🔴 Deprecated
- Superseded by: spec-16
```

### 15.3 New Spec Extending Existing Ones

```
spec-17.md  →  "Essence system expansion (extends spec-03)"
```

At the top:
```markdown
---
Extends: spec-03
Required by: spec-09, spec-12
---
```

### 15.4 Rule Summary

| Situation | Action |
|-----------|--------|
| Two approaches for same spec | Separate branches, validate, merge winner |
| Refactor of stable spec | New spec + deprecate old |
| Extension of existing spec | New spec referencing the old |

**Core rule:** A merged spec is immutable. To change it, create a new one.

---

## Metadata

- Version: 1.1.0
- Last update: 2026-05-24
- Location: /eco/AGENT.md