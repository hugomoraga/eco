from __future__ import annotations

import random


class SeededRandom:
    _instance: SeededRandom | None = None

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)

    @classmethod
    def get_instance(cls, seed: int | None = None) -> SeededRandom:
        if cls._instance is None or seed is not None:
            cls._instance = cls(seed if seed is not None else 42)
        return cls._instance

    def random(self) -> float:
        return self.rng.random()

    def uniform(self, a: float, b: float) -> float:
        return self.rng.uniform(a, b)

    def choice(self, seq: list) -> any:
        return self.rng.choice(seq)

    def shuffle(self, seq: list) -> None:
        self.rng.shuffle(seq)

    def randint(self, a: int, b: int) -> int:
        return self.rng.randint(a, b)

    def getstate(self) -> tuple:
        return self.rng.getstate()

    def setstate(self, state: tuple) -> None:
        self.rng.setstate(state)

    def getrandbits(self, k: int) -> int:
        return self.rng.getrandbits(k)

    def sample(self, seq: list, k: int) -> list:
        return self.rng.sample(seq, k)


def seeded_random(seed: int = 42) -> SeededRandom:
    return SeededRandom.get_instance(seed)