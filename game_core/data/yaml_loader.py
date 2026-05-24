from __future__ import annotations

from game_core.domain.entities import WorldClock


def load_yaml(path: str) -> dict:
    import yaml

    with open(path) as f:
        return yaml.safe_load(f)


def save_yaml(data: dict, path: str) -> None:
    import yaml

    with open(path, "w") as f:
        yaml.safe_dump(data, f, indent=2)


def state_to_yaml(world: WorldClock) -> str:
    import yaml

    return yaml.dump(world.model_dump(), allow_unicode=True)