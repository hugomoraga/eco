#!/usr/bin/env python3
"""
MVP Consolidated Audit (actualizado a estructura real)

Reads:
  - Implementation files
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
    """Run implementation audit against current structure."""
    results = {}

    section("Implementation Audit")

    base = Path("game_core")

    # ─── File Structure (actual) ───────────────────────────────────────────
    print(f"\n  {BOLD}File Structure (current){RESET}")
    files = [
        ("domain/entities.py", base / "domain" / "entities.py"),
        ("domain/city.py", base / "domain" / "city.py"),
        ("domain/npc.py", base / "domain" / "npc.py"),
        ("domain/enums.py", base / "domain" / "enums.py"),
        ("systems/simulation.py", base / "systems" / "simulation.py"),
        ("systems/random.py", base / "systems" / "random.py"),
        ("systems/pressure.py", base / "systems" / "pressure.py"),
        ("systems/event_generator.py", base / "systems" / "event_generator.py"),
        ("actions/base.py", base / "actions" / "base.py"),
        ("actions/circle_actions.py", base / "actions" / "circle_actions.py"),
        ("actions/social_actions.py", base / "actions" / "social_actions.py"),
        ("autoplayer/engine.py", base / "autoplayer" / "engine.py"),
        ("ai/base.py", base / "ai" / "base.py"),
        ("essences.yaml", base.parent / "data" / "essences.yaml"),
    ]

    file_pass = all(check_row(name, f.exists()) for name, f in files)
    results["files"] = file_pass

    # ─── Domain Entities ────────────────────────────────────────────────────
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
            ("Person class", "class Person" in content),
            ("Host class", "class Host" in content),
            ("Pydantic BaseModel", "BaseModel" in content),
        ]
        entity_pass = all(check_row(name, cond) for name, cond in entity_checks)
    else:
        entity_pass = False
    results["entities"] = entity_pass

    # ─── Actions ────────────────────────────────────────────────────────────
    print(f"\n  {BOLD}Actions (8 total){RESET}")
    actions_dir = base / "actions"
    required_actions = [
        "found_circle", "join_circle", "leave_circle",
        "propagate_idea", "talk", "write_manifesto",
        "sabotage", "ritualize"
    ]
    if actions_dir.exists():
        all_content = ""
        for f in ["base.py", "circle_actions.py", "social_actions.py", "manifesto_actions.py"]:
            fp = actions_dir / f
            if fp.exists():
                all_content += fp.read_text()
        action_pass = all(check_row(f"action: {a}", a in all_content) for a in required_actions)
    else:
        action_pass = False
    results["actions"] = action_pass

    # ─── Systems ────────────────────────────────────────────────────────────
    sim = base / "systems" / "simulation.py"
    print(f"\n  {BOLD}Simulation Engine{RESET}")
    if sim.exists():
        content = sim.read_text()
        sim_checks = [
            ("SimulationEngine class", "class SimulationEngine" in content),
            ("seed parameter", "seed" in content),
            ("JSONL logging", "jsonl" in content.lower() or ".jsonl" in content),
            ("snapshots", "snapshot" in content.lower()),
            ("autoplay support", "autoplay" in content.lower()),
        ]
        sim_pass = all(check_row(name, cond) for name, cond in sim_checks)
    else:
        sim_pass = False
    results["simulation"] = sim_pass

    # ─── Autoplayer ────────────────────────────────────────────────────────
    auto = base / "autoplayer" / "engine.py"
    print(f"\n  {BOLD}Autoplayer{RESET}")
    if auto.exists():
        content = auto.read_text()
        auto_checks = [
            ("AutoplayerEngine class", "class AutoplayerEngine" in content),
            ("AutoplayMode enum", "AutoplayMode" in content),
            ("PlayerStyles", "PLAYER_STYLES" in content),
            ("select_action method", "def select_action" in content),
            ("score_action method", "def score_action" in content),
        ]
        auto_pass = all(check_row(name, cond) for name, cond in auto_checks)
    else:
        auto_pass = False
    results["autoplay"] = auto_pass

    # ─── Pressure System ────────────────────────────────────────────────────
    pressure = base / "systems" / "pressure.py"
    print(f"\n  {BOLD}Pressure System{RESET}")
    if pressure.exists():
        content = pressure.read_text()
        pressure_checks = [
            ("DerivePressureCalculator", "class DerivePressureCalculator" in content),
            ("EconomyPressure", "class EconomyPressure" in content),
            ("calculate method", "def calculate" in content),
        ]
        pressure_pass = all(check_row(name, cond) for name, cond in pressure_checks)
    else:
        pressure_pass = False
    results["pressure"] = pressure_pass

    # ─── Event Generator ────────────────────────────────────────────────────
    event_gen = base / "systems" / "event_generator.py"
    print(f"\n  {BOLD}Event Generator{RESET}")
    if event_gen.exists():
        content = event_gen.read_text()
        event_checks = [
            ("EventGenerator class", "class EventGenerator" in content),
            ("EffectTagValidator", "class EffectTagValidator" in content),
            ("GameEvent class", "class GameEvent" in content),
        ]
        event_pass = all(check_row(name, cond) for name, cond in event_checks)
    else:
        event_pass = False
    results["events"] = event_pass

    # ─── AI Adapters ───────────────────────────────────────────────────────
    ai_dir = base / "ai"
    print(f"\n  {BOLD}AI Adapters{RESET}")
    # MockAdapter is inline in ai/base.py
    mock_inline = (ai_dir / "base.py").exists() and "MockAdapter" in (ai_dir / "base.py").read_text()
    check_row("MockAdapter (inline in base.py)", mock_inline)
    # Real adapters in adapters/
    adapter_dir = ai_dir / "adapters"
    for adapter in ["openai", "minimax"]:
        adapter_file = adapter_dir / f"{adapter}_adapter.py"
        exists = adapter_file.exists()
        check_row(f"{adapter}_adapter.py", exists)
    results["ai_adapters"] = mock_inline

    # ─── Essences (20 esencias, spec-47) ───────────────────────────────────
    essences_file = base.parent / "data" / "essences.yaml"
    print(f"\n  {BOLD}Essences (spec-47: 20 esencias){RESET}")
    if essences_file.exists():
        content = essences_file.read_text()
        # Count essences in YAML (top-level keys under 'essences:')
        # Match lines like "  thelema:" at 2 spaces, all-lowercase
        import re
        essence_matches = re.findall(r'^  [a-z_]+:$', content, re.MULTILINE)
        # Filter: only known essences (no 'name', 'description', 'attributes', etc.)
        fake_keys = {'name', 'description', 'attributes', 'affinity_matrix', 'affinity_values',
                     'affinity', 'alignment', 'essences'}
        essence_names = [m.rstrip(':').strip() for m in essence_matches if m.rstrip(':').strip() not in fake_keys]
        # Deduplicate (essences appear in both 'essences:' and 'affinity_matrix:' sections)
        unique_essences = list(dict.fromkeys(essence_names))
        essence_count = len(unique_essences)
        check_row(f"essence count ({essence_count}/20)", essence_count >= 20)
        checks_pass = essence_count >= 20
        # Check key essences from spec-47
        key_essences = ["anarchism", "technocracy", "absurdism", "thelema", "ecology", "capitalism", "socialism"]
        for e in key_essences:
            check_row(f"  - {e}", e in content)
        results["essences"] = checks_pass
    else:
        results["essences"] = False

    # ─── i18n ──────────────────────────────────────────────────────────────
    i18n_dir = base / "i18n"
    print(f"\n  {BOLD}i18n (es/en){RESET}")
    if i18n_dir.exists():
        es = (i18n_dir / "es.yaml").exists()
        en = (i18n_dir / "en.yaml").exists()
        check_row("es.yaml", es)
        check_row("en.yaml", en)
        results["i18n"] = es and en
    else:
        results["i18n"] = False

    # ─── Tuning ────────────────────────────────────────────────────────────
    tuning = base / "utils" / "tuning.py"
    print(f"\n  {BOLD}Tuning System{RESET}")
    if tuning.exists():
        content = tuning.read_text()
        tuning_pass = "diminishing" in content.lower() and "tuning" in content.lower()
        check_row("tuning.py", True)
        check_row("diminishing returns", "diminishing" in content.lower())
        results["tuning"] = tuning_pass
    else:
        results["tuning"] = False

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
    print(" MVP CONSOLIDATED AUDIT (current)")
    print(f"{'=' * 60}{RESET}")

    impl_results = audit_implementation()
    specs = parse_spec19_status()
    display_spec_tracking(specs)

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

    print(f"\n{BOLD}{'=' * 60}")
    if impl_pass == impl_total:
        print(f"  {GREEN}✅ MVP IMPLEMENTATION COMPLETE{RESET}")
        print(f"  Specs in spec-19: {len(specs)} tracked")
    else:
        print(f"  {YELLOW}⚠️  Implementation incomplete ({impl_pass}/{impl_total}){RESET}")
    print(f"{'=' * 60}{RESET}")

    return 0 if impl_pass == impl_total else 1


if __name__ == "__main__":
    sys.exit(main())
