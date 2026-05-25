#!/usr/bin/env python3
"""
MVP Consolidated Audit

Reads:
  - Implementation files (audit_mvp logic)
  - spec-19.md (status tracking table)

Outputs:
  - Unified progress report with implementation status + spec tracking
"""

import os
import sys
from pathlib import Path

# Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"


def section(title: str) -> None:
    print(f"\n{BOLD}{'=' * 60}")
    print(f" {title}")
    print(f"{'=' * 60}{RESET}")


def check_row(name: str, passed: bool, details: str = "") -> bool:
    status = f"{GREEN}✅{RESET}" if passed else f"{RED}❌{RESET}"
    detail_str = f"  {CYAN}{details}{RESET}" if details else ""
    print(f"  {status} {name}{detail_str}")
    return passed


def parse_spec19_status() -> dict:
    """Parse spec-19 to get spec status table."""
    spec19 = Path("specs/19-mvp-implementation.md")
    if not spec19.exists():
        return {}

    content = spec19.read_text()

    # Extract spec status from the table
    # Format: | 01 | Architecture | deprecated | v0.2.0 | ...
    specs = {}
    for line in content.split("\n"):
        if line.startswith("| ") and " | " in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 5 and parts[1].strip().isdigit():
                num = int(parts[1].strip())
                name = parts[2].strip()
                status = parts[3].strip()
                specs[num] = {"name": name, "status": status}

    return specs


def audit_implementation() -> dict:
    """Run implementation audit (same as original audit_mvp.py)."""
    results = {}

    section("Implementation Audit (spec-16)")

    # File structure
    base = Path("game_core")
    files = [
        ("domain/entities.py", base / "domain" / "entities.py"),
        ("domain/city.py", base / "domain" / "city.py"),
        ("domain/npc.py", base / "domain" / "npc.py"),
        ("engine/simulation.py", base / "engine" / "simulation.py"),
        ("engine/random.py", base / "engine" / "random.py"),
        ("actions/base.py", base / "actions" / "base.py"),
        ("actions/echo_actions.py", base / "actions" / "echo_actions.py"),
        ("data/essences.yaml", base / "data" / "essences.yaml"),
        ("data/actions.yaml", base / "data" / "actions.yaml"),
    ]

    print(f"\n  {BOLD}File Structure{RESET}")
    file_pass = all(check_row(name, f.exists()) for name, f in files)
    results["files"] = file_pass

    # Domain entities
    entities = base / "domain" / "entities.py"
    print(f"\n  {BOLD}Domain Entities{RESET}")
    if entities.exists():
        content = entities.read_text()
        entity_checks = [
            ("Echo class", "class Echo" in content),
            ("Circle class", "class Circle" in content),
            ("Faction class", "class Faction" in content),
            ("World class", "class World" in content),
            ("WorldClock class", "class WorldClock" in content),
            ("Pydantic BaseModel", "BaseModel" in content),
        ]
        entity_pass = all(check_row(name, cond) for name, cond in entity_checks)
    else:
        entity_pass = False
    results["entities"] = entity_pass

    # Actions
    actions_dir = base / "actions"
    print(f"\n  {BOLD}Actions (spec-07){RESET}")
    if actions_dir.exists():
        base_file = actions_dir / "base.py"
        echo_file = actions_dir / "echo_actions.py"
        required = ["found_circle", "propagate_idea", "talk", "write_manifesto", "sabotage", "ritualize"]
        if base_file.exists():
            content = base_file.read_text() + echo_file.read_text() if echo_file.exists() else ""
            action_pass = all(check_row(f"action: {a}", a in content) for a in required)
        else:
            action_pass = False
    else:
        action_pass = False
    results["actions"] = action_pass

    # Simulation
    sim = base / "engine" / "simulation.py"
    print(f"\n  {BOLD}Simulation Engine{RESET}")
    if sim.exists():
        content = sim.read_text()
        sim_checks = [
            ("Simulation class", "class Simulation" in content),
            ("seed parameter", "seed" in content),
            ("JSONL logging", "jsonl" in content.lower() or ".jsonl" in content),
        ]
        sim_pass = all(check_row(name, cond) for name, cond in sim_checks)
    else:
        sim_pass = False
    results["simulation"] = sim_pass

    # Autoplay
    run = base / "run.py"
    print(f"\n  {BOLD}Autoplay Flag{RESET}")
    if run.exists():
        content = run.read_text()
        autoplay_pass = check_row("--autoplay flag", "autoplay" in content)
    else:
        autoplay_pass = False
    results["autoplay"] = autoplay_pass

    return results


def display_spec_tracking(specs: dict) -> None:
    """Display spec tracking from spec-19."""
    section("Spec Status Tracking (spec-19)")

    status_colors = {
        "implemented": GREEN,
        "deprecated": RED,
        "stable": GREEN,
        "in_progress": YELLOW,
        "draft": CYAN,
    }

    # Group by status
    by_status = {}
    for num, info in sorted(specs.items()):
        status = info["status"]
        if status not in by_status:
            by_status[status] = []
        by_status[status].append((num, info["name"]))

    for status, items in by_status.items():
        color = status_colors.get(status, RESET)
        print(f"\n  {BOLD}{color}{status.upper()}{RESET} ({len(items)} specs)")
        for num, name in items:
            print(f"    {num:02d} | {name}")


def main():
    os.chdir(Path(__file__).parent.parent)

    print(f"\n{BOLD}{'=' * 60}")
    print(" MVP CONSOLIDATED AUDIT")
    print(f"{'=' * 60}{RESET}")

    # Implementation audit
    impl_results = audit_implementation()

    # Spec tracking from spec-19
    specs = parse_spec19_status()
    display_spec_tracking(specs)

    # Summary
    section("SUMMARY")

    impl_pass = sum(1 for v in impl_results.values() if v)
    impl_total = len(impl_results)

    print(f"\n  {BOLD}Implementation Audit:{RESET}")
    for name, passed in impl_results.items():
        status = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
        print(f"    {status}  {name}")

    print(f"\n  {BOLD}Implementation:{RESET} {impl_pass}/{impl_total} sections passing")

    if specs:
        print(f"\n  {BOLD}Specs Tracked:{RESET} {len(specs)} specs in spec-19")
        status_counts = {}
        for info in specs.values():
            s = info["status"]
            status_counts[s] = status_counts.get(s, 0) + 1
        for status, count in sorted(status_counts.items()):
            print(f"    {status}: {count}")

    # Overall status
    print(f"\n{BOLD}{'=' * 60}")
    if impl_pass == impl_total:
        print(f"  {GREEN}✅ MVP 0 IMPLEMENTATION COMPLETE{RESET}")
        print(f"  Specs in spec-19: {len(specs)} tracked")
    else:
        print(f"  {YELLOW}⚠️  MVP 0 implementation incomplete ({impl_pass}/{impl_total}){RESET}")
    print(f"{'=' * 60}{RESET}")

    return 0 if impl_pass == impl_total else 1


if __name__ == "__main__":
    sys.exit(main())
