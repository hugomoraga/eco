from __future__ import annotations

from pathlib import Path

import yaml

from game_core.systems.random import SeededRandom


class EventPool:
    """Event pool that loads events from YAML and selects events by category based on world state."""

    def __init__(self, events_path: str = "data/events.yaml"):
        self.events_path = events_path
        self.events_data: dict = {}
        self.category_index: dict[str, list[str]] = {}

        self._load_events()
        self._build_category_index()

    def _load_events(self) -> None:
        """Load events.yaml file."""
        path = Path(self.events_path)
        if not path.is_absolute():
            path = Path(__file__).parent.parent.parent / self.events_path

        with open(path) as f:
            data = yaml.safe_load(f)
            self.events_data = data.get("events", {})

    def _build_category_index(self) -> None:
        """Build category -> [event_ids] index."""
        self.category_index = {}
        for event_id, event_data in self.events_data.items():
            category = event_data.get("category", "").lower()
            if category:
                if category not in self.category_index:
                    self.category_index[category] = []
                self.category_index[category].append(event_id)

    def get_dominant_essence(self, world_state: dict) -> str:
        """Calculate dominant essence from world_state essence_distribution.

        Handles both dict and Pydantic model objects.
        """
        # Handle Pydantic model (World object)
        if hasattr(world_state, 'model_dump'):
            world_state = world_state.model_dump()

        essence_dist = world_state.get("essence_distribution", {})
        if not essence_dist:
            # Fallback: compute from echoes if available
            echoes = world_state.get("echoes", [])
            if echoes:
                from collections import Counter
                essences = [e.get("essence", "anarchism") for e in echoes]
                counter = Counter(essences)
                return counter.most_common(1)[0][0]
            return "anarchism"

        # Find essence with highest weight
        dominant = max(essence_dist.items(), key=lambda x: x[1])
        return dominant[0]

    def calculate_category_weights(self, world_state: dict) -> dict[str, float]:
        """Calculate weights per category based on world state and essence distribution.

        Base weights + modifier based on dominant essence.
        """
        # Handle Pydantic model (World object)
        if hasattr(world_state, 'model_dump'):
            world_state = world_state.model_dump()

        base_weights = {
            "crisis": 1.2,
            "ritual": 1.0,
            "political": 1.0,
            "discovery": 0.9,
            "social": 0.8,
            "entropy": 0.7,
        }

        # Modifier based on dominant essence
        essence_modifiers = {
            "anarchism": {"crisis": 1.3, "entropy": 1.1, "social": 1.0},
            "absurdism": {"crisis": 1.2, "ritual": 1.2, "entropy": 1.1},
            "thelema": {"ritual": 1.3, "political": 1.1, "social": 0.9},
            "technocracy": {"political": 1.3, "discovery": 1.1, "crisis": 0.9},
            "ecology": {"discovery": 1.3, "social": 1.1, "entropy": 1.0},
        }

        dominant = self.get_dominant_essence(world_state)
        modifiers = essence_modifiers.get(dominant, {})

        weights = {}
        for category, base in base_weights.items():
            modifier = modifiers.get(category, 1.0)
            weights[category] = base * modifier

        # Boost crisis weight if world is unstable
        stability = world_state.get("stability", 50.0)
        if stability < 30:
            weights["crisis"] *= 1.5
        elif stability > 70:
            weights["crisis"] *= 0.7

        return weights

    def select_category(self, world_state: dict) -> str:
        """Select a category using weighted random based on world state."""
        # Handle Pydantic model (World object)
        if hasattr(world_state, 'model_dump'):
            world_state = world_state.model_dump()

        weights = self.calculate_category_weights(world_state)
        rng = SeededRandom.get_instance()

        categories = list(weights.keys())
        weight_values = list(weights.values())

        # Filter categories that have events
        available = [(c, w) for c, w in zip(categories, weight_values, strict=False) if self.category_index.get(c)]
        if not available:
            return "crisis"

        cats, wts = zip(*available, strict=False)
        total = sum(wts)
        probs = [w / total for w in wts]

        roll = rng.random()
        cumulative = 0.0
        for cat, prob in zip(cats, probs, strict=False):
            cumulative += prob
            if roll <= cumulative:
                return cat

        return cats[-1]

    def select_event(self, category: str) -> str:
        """Select a random event_id from a category."""
        if category not in self.category_index or not self.category_index[category]:
            return ""

        rng = SeededRandom.get_instance()
        return rng.choice(self.category_index[category])

    def get_event_data(self, event_id: str) -> dict | None:
        """Get full event data by event_id."""
        return self.events_data.get(event_id)

    def get_events_by_category(self, category: str) -> list[str]:
        """Get all event_ids in a category."""
        return self.category_index.get(category, [])

    def get_categories(self) -> list[str]:
        """Get all available categories."""
        return list(self.category_index.keys())
