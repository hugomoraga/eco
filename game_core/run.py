from __future__ import annotations

import argparse

from game_core.engine.simulation import SimulationEngine


def main() -> None:
    parser = argparse.ArgumentParser(description="ECO - Memetic Simulation Engine")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--turns", type=int, default=100, help="Max turns")
    parser.add_argument("--autoplay", action="store_true", help="Enable autoplay mode")
    parser.add_argument("--run-dir", type=str, help="Run directory for logs")
    args = parser.parse_args()

    engine = SimulationEngine(
        seed=args.seed,
        max_turns=args.turns,
        autoplay=args.autoplay,
        run_dir=args.run_dir,
    )
    result = engine.run()
    print(f"Simulation complete. Results: {result}")


if __name__ == "__main__":
    main()