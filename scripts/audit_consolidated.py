#!/usr/bin/env python3
"""
MVP Consolidated Audit — Reflects hexagonal architecture (spec-54).

Reads:
  - core/, infra/, adapters/ file structure
  - data/ YAML files
  - specs/19-mvp-implementation.md (status tracking)

Outputs:
  - Unified progress report with implementation status + spec tracking
"""

import os
import re
import sys
from pathlib import Path

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
    status = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
    detail_str = f"  ({CYAN}{details}{RESET})" if details else ""
    print(f"  {status}  {name}{detail_str}")
    return passed


def read_file(path: Path) -> str | None:
    if path.exists():
        return path.read_text()
    return None


def audit_implementation() -> dict:
    """Run implementation audit against hexagonal architecture."""
    results = {}
    root = Path(".")

    section("Domain Entities (core/domain/entities/)")

    entity_files = {
        "Echo": root / "core/domain/entities/echo.py",
        "Circle": root / "core/domain/entities/circle.py",
        "World": root / "core/domain/entities/world.py",
        "Person": root / "core/domain/entities/person.py",
        "Civ": root / "core/domain/entities/civ.py",
        "Faction": root / "core/domain/entities/faction.py",
        "Idea": root / "core/domain/entities/idea.py",
        "Doctrine": root / "core/domain/entities/doctrine.py",
        "Manifesto": root / "core/domain/entities/manifesto.py",
        "Actor": root / "core/domain/entities/actor.py",
        "NPC": root / "core/domain/entities/npc.py",
        "Host (legacy)": root / "core/domain/entities/host.py",
    }
    all_content = ""
    for name, path in entity_files.items():
        content = read_file(path)
        exists = content is not None
        has_class = exists and f"class {name.split(' ')[0]}" in content
        check_row(name, has_class, "found" if has_class else ("missing class" if exists else "file missing"))
        if content:
            all_content += content

    results["entities"] = all(
        f"class {n.split(' ')[0]}" in (read_file(p) or "")
        for n, p in entity_files.items()
        if n != "Host (legacy)"
    )

    section("Value Objects & Definitions (core/domain/)")

    vo_files = {
        "ResonanceProfile": root / "core/domain/value_objects/resonance_profile.py",
        "ResonanceScore": root / "core/domain/value_objects/resonance_score.py",
        "ResourcePool": root / "core/domain/value_objects/resource_pool.py",
        "ResonanceDef": root / "core/domain/definitions/resonance_def.py",
        "ActionDef": root / "core/domain/definitions/action_def.py",
        "CivTemplate": root / "core/domain/definitions/civ_template.py",
        "PersonArchetype": root / "core/domain/definitions/person_archetype.py",
    }
    vo_pass = True
    for name, path in vo_files.items():
        found = (read_file(path) or "") != ""
        check_row(name, found)
        vo_pass = vo_pass and found
    results["value_objects"] = vo_pass

    section("Enums (core/domain/enums.py)")

    enums_content = read_file(root / "core/domain/enums.py") or ""
    required_enums = [
        "TemporalLayer",
        "EchoPhase",
        "CircleStatus",
        "CircleEventType",
        "EventCategory",
        "CivAlignment",
        "ActionCategory",
    ]
    enums_pass = True
    for enum_name in required_enums:
        found = f"class {enum_name}" in enums_content
        check_row(enum_name, found)
        enums_pass = enums_pass and found
    results["enums"] = enums_pass

    section("Domain Rules & Systems (core/domain/)")

    rules_content = read_file(root / "core/domain/rules/crisis.py") or ""
    systems_content = read_file(root / "core/domain/systems/essence_system.py") or ""
    goals_content = read_file(root / "core/domain/rules/goals.py") or ""

    rules_pass = True
    for name, content, pattern in [
        ("CrisisType", rules_content, "class CrisisType"),
        ("CRISIS_DATA", rules_content, "CRISIS_DATA"),
        ("EssenceSystem", systems_content, "class EssenceSystem"),
        ("Goal", goals_content, "class Goal"),
    ]:
        found = pattern in content
        check_row(name, found)
        rules_pass = rules_pass and found
    results["rules_systems"] = rules_pass

    section("Actions (core/application/actions/)")

    actions_dir = root / "core/application/actions"
    required_actions = [
        "found_circle",
        "join_circle",
        "leave_circle",
        "propagate_idea",
        "talk",
        "write_manifesto",
        "sabotage",
        "ritualize",
        "negotiate",
        "recruit_follower",
        "spread_rumor",
        "ritual",
    ]
    actions_content = ""
    for f in actions_dir.glob("*.py"):
        actions_content += f.read_text()
    action_pass = True
    for action in required_actions:
        found = 'def execute' in actions_content and action in actions_content
        check_row(f"action: {action}", found)
        action_pass = action_pass and found
    results["actions"] = action_pass

    section("Processors (core/application/processors/)")

    proc_dir = root / "core/application/processors"
    processor_checks = [
        ("SimulationEngine", "class SimulationEngine", "simulation_engine.py"),
        ("EventGenerator", "class EventGenerator", "event_generator.py"),
        ("EventPool", "class EventPool", "event_pool.py"),
        ("PressureCalculator", "class DerivePressureCalculator", "pressure.py"),
        ("NarrativeEngine", "class NarrativeEngine", "narrative_engine.py"),
        ("NPCProcessor", "process_npc_turns", "npc_processor.py"),
        ("CircleProcessor", "process_circle_tick", "circle_processor.py"),
        ("GoalProcessor", "initialize_goals", "goal_processor.py"),
    ]
    proc_pass = True
    for name, pattern, filename in processor_checks:
        content = read_file(proc_dir / filename) or ""
        found = pattern in content
        check_row(name, found)
        proc_pass = proc_pass and found
    results["processors"] = proc_pass

    section("Simulation Engine")

    sim_content = read_file(root / "core/application/processors/simulation_engine.py") or ""
    sim_checks = [
        ("SimulationEngine class", "class SimulationEngine" in sim_content),
        ("seed parameter", "seed" in sim_content),
        ("run method", "def run" in sim_content),
        ("JSONL logging", ".jsonl" in sim_content),
        ("snapshots", "snapshot" in sim_content.lower()),
    ]
    sim_pass = all(check_row(name, cond) for name, cond in sim_checks)
    results["simulation"] = sim_pass

    section("Autoplayer (adapters/autoplayer/)")

    auto_content = read_file(root / "adapters/autoplayer/engine.py") or ""
    auto_checks = [
        ("AutoplayerEngine class", "class AutoplayerEngine" in auto_content),
        ("AutoplayMode enum", "AutoplayMode" in auto_content),
        ("score_action method", "def score_action" in auto_content),
    ]
    auto_pass = all(check_row(name, cond) for name, cond in auto_checks)
    results["autoplay"] = auto_pass

    section("Pressure System (core/application/processors/pressure.py)")

    pressure_content = read_file(root / "core/application/processors/pressure.py") or ""
    pressure_checks = [
        ("DerivePressureCalculator", "class DerivePressureCalculator" in pressure_content),
        ("calculate method", "def calculate" in pressure_content),
    ]
    pressure_pass = all(check_row(name, cond) for name, cond in pressure_checks)
    results["pressure"] = pressure_pass

    section("AI Adapters (infra/ai/)")

    ai_dir = root / "infra/ai"
    base_content = read_file(ai_dir / "base.py") or ""
    mock_inline = "MockAdapter" in base_content
    check_row("MockAdapter (infra/ai/base.py)", mock_inline)
    adapter_dir = ai_dir / "adapters" if (ai_dir / "adapters").exists() else ai_dir
    minimax = (adapter_dir / "minimax_adapter.py").exists() or (ai_dir / "minimax_adapter.py").exists()
    openai = (adapter_dir / "openai_adapter.py").exists() or (ai_dir / "openai_adapter.py").exists()
    check_row("MinimaxAdapter", minimax)
    check_row("OpenAIAdapter", openai)
    results["ai_adapters"] = mock_inline

    section("Resonances/Essences (data/resonances.yaml)")

    resonances_file = root / "data/resonances.yaml"
    essences_file = root / "data/essences.yaml"
    active_file = resonances_file if resonances_file.exists() else essences_file

    if active_file.exists():
        content = active_file.read_text()
        essence_matches = re.findall(r"^  [a-z_]+:$", content, re.MULTILINE)
        fake_keys = {
            "name", "description", "attributes", "affinity_matrix",
            "affinity_values", "affinity", "alignment", "essences",
        }
        essence_names = [
            m.rstrip(":").strip() for m in essence_matches
            if m.rstrip(":").strip() not in fake_keys
        ]
        unique_essences = list(dict.fromkeys(essence_names))
        essence_count = len(unique_essences)
        check_row(f"essence count ({essence_count}/20)", essence_count >= 20)
        key_essences = [
            "anarchism", "technocracy", "absurdism", "thelema",
            "ecology", "capitalism", "socialism",
        ]
        for e in key_essences:
            check_row(f"  - {e}", e in content)
        results["essences"] = essence_count >= 20
    else:
        check_row("resonances.yaml", False, "file missing")
        results["essences"] = False

    section("i18n (adapters/i18n/)")

    i18n_dir = root / "adapters/i18n"
    es = (i18n_dir / "es.yaml").exists()
    en = (i18n_dir / "en.yaml").exists()
    check_row("es.yaml", es)
    check_row("en.yaml", en)
    results["i18n"] = es and en

    section("Tuning (infra/config/tuning.py)")

    tuning_content = read_file(root / "infra/config/tuning.py") or ""
    tuning_pass = "diminishing" in tuning_content.lower() and "tuning" in tuning_content.lower()
    check_row("tuning.py", bool(tuning_content))
    check_row("diminishing returns", "diminishing" in tuning_content.lower())
    results["tuning"] = tuning_pass

    section("Factories (core/factories/)")

    factories_dir = root / "core/factories"
    required_factories = [
        "echo.py", "circle.py", "civ.py", "faction.py",
        "npc.py", "host.py", "narrative_generator.py", "tags.py",
    ]
    factories_pass = True
    for f in required_factories:
        exists = (factories_dir / f).exists()
        check_row(f, exists)
        factories_pass = factories_pass and exists
    results["factories"] = factories_pass

    section("Ports (core/ports/)")

    ports_dir = root / "core/ports"
    required_ports = ["player.py", "logger.py", "messages.py", "codec.py"]
    ports_pass = True
    for f in required_ports:
        exists = (ports_dir / f).exists()
        check_row(f, exists)
        ports_pass = ports_pass and exists
    results["ports"] = ports_pass

    section("CLI Adapter (adapters/cli/)")

    cli_dir = root / "adapters/cli"
    cli_content = read_file(cli_dir / "launcher.py") or ""
    cli_checks = [
        ("Launcher class", "class Launcher" in cli_content or "def main" in read_file(cli_dir / "main.py") or ""),
        ("--seed argument", "--seed" in cli_content or "--seed" in (read_file(cli_dir / "main.py") or "")),
        ("--autoplay flag", "--autoplay" in cli_content or "--autoplay" in (read_file(cli_dir / "main.py") or "")),
    ]
    cli_pass = all(check_row(name, cond) for name, cond in cli_checks)
    results["cli"] = cli_pass

    section("Logging (infra/logging/)")

    log_content = read_file(root / "infra/logging/main.py") or ""
    log_checks = [
        ("structlog", "structlog" in log_content),
        ("JSONL output", "jsonl" in log_content.lower() or "json" in log_content.lower()),
        ("debug.log", "debug.log" in log_content or "debug" in log_content),
    ]
    log_pass = all(check_row(name, cond) for name, cond in log_checks)
    results["logging"] = log_pass

    return results


def parse_spec_status() -> dict:
    """Parse spec-19 or spec index for status tracking."""
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


def display_spec_tracking(specs: dict) -> None:
    section("Spec Status Tracking (spec-19)")

    status_colors = {
        "implemented": GREEN,
        "deprecated": RED,
        "stable": GREEN,
        "in_progress": YELLOW,
        "draft": CYAN,
        "ready": GREEN,
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
    print(" MVP CONSOLIDATED AUDIT (hexagonal arch)")
    print(f"{'=' * 60}{RESET}")

    impl_results = audit_implementation()
    specs = parse_spec_status()

    if specs:
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
        print(f"  {GREEN}ALL CHECKS PASSED{RESET}")
    else:
        print(f"  {YELLOW}PARTIAL: {impl_pass}/{impl_total} sections passing{RESET}")
    print(f"{'=' * 60}{RESET}")

    return 0 if impl_pass == impl_total else 1


if __name__ == "__main__":
    sys.exit(main())
