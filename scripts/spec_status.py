#!/usr/bin/env python3
"""
ECO Spec Status Dashboard

Reads all specs from specs/ directory and generates a progress report.
Used to track implementation status across iterations.

Usage:
    python scripts/spec_status.py
    python scripts/spec_status.py --verbose
    python scripts/spec_status.py --json
"""

from __future__ import annotations

import os
import re
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


SPECS_DIR = Path("specs")
STATUS_TYPES = ["draft", "in_progress", "stable", "deprecated"]


@dataclass
class SpecInfo:
    """Information extracted from a spec file."""

    number: str
    filename: str
    title: str
    status: str = "draft"
    version: str = "0.0.0"
    implementation: str = "0%"
    tests: str = "0%"
    last_update: str = ""
    dependencies: list[str] = field(default_factory=list)


def parse_spec_number(filename: str) -> Optional[str]:
    """Extract spec number from filename like '01-architecture.md'."""
    match = re.match(r"^(\d+)-", filename)
    return match.group(1) if match else None


def parse_metadata(content: str) -> dict:
    """Parse metadata section from spec content.

    Looks for YAML-like metadata at end of file or status badges in header.
    Handles both English and Spanish status labels.
    """
    metadata = {}

    # Status mappings for Spanish labels
    status_map = {
        "en desarrollo": "in_progress",
        "completada": "stable",
        "deprecated": "deprecated",
        "bloqueada": "blocked",
        "🔄 en desarrollo": "in_progress",
        "✅ corregido": "stable",
        "✅ completada": "stable",
        "✅": "stable",
        "⚠️ deprecated": "deprecated",
        "📌 bloqueada": "blocked",
    }

    # Check for status badge in header: **Status:** Stable | **Version:** 1.2.0
    status_match = re.search(r"\*\*Status:\*\*\s*([\w\s]+?)(?:\s*\*\*|\|)", content)
    if status_match:
        raw_status = status_match.group(1).lower().strip()
        metadata["status"] = status_map.get(raw_status, raw_status)

    # Check for Spanish status patterns like "Estado: 🔄 En desarrollo"
    spanish_status_match = re.search(r"Estado:\s*([^\n\-]+)", content)
    if spanish_status_match and "status" not in metadata:
        raw = spanish_status_match.group(1).lower().strip()
        # Clean emoji
        raw = re.sub(r"[^\w\s]", "", raw).strip()
        metadata["status"] = status_map.get(raw, raw if raw in status_map.values() else "draft")

    version_match = re.search(r"\*\*Version:\*\*\s*([\d.]+)", content)
    if version_match:
        metadata["version"] = version_match.group(1)

    impl_match = re.search(r"\*\*Impl:\*\*\s*(\d+%)", content)
    if impl_match:
        metadata["implementation"] = impl_match.group(1)

    tests_match = re.search(r"\*\*Tests:\*\*\s*(\d+%)", content)
    if tests_match:
        metadata["tests"] = tests_match.group(1)

    # Check for last update date (various formats)
    date_patterns = [
        r"(\d{4}-\d{2}-\d{2})",  # 2026-05-24
        r"(\d{2}/\d{2}/\d{4})",  # 24/05/2026
        r"Last update:\s*([^\n]+)",
    ]
    for pattern in date_patterns:
        date_match = re.search(pattern, content)
        if date_match:
            metadata["last_update"] = date_match.group(1).strip()
            break

    return metadata


def read_specs() -> list[SpecInfo]:
    """Read all spec files and extract metadata."""
    specs = []

    if not SPECS_DIR.exists():
        print("Error: specs/ directory not found")
        return specs

    for file_path in sorted(SPECS_DIR.glob("*.md")):
        if file_path.name == "00-index.md":
            continue  # Skip index

        spec_num = parse_spec_number(file_path.name)
        if not spec_num:
            continue

        content = file_path.read_text()

        # Extract title from first H1 or H2
        title_match = re.search(r"^#+\s+(?:\d+\s*-\s*)?(.+)$", content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else file_path.stem

        # Parse metadata
        meta = parse_metadata(content)

        spec = SpecInfo(
            number=spec_num,
            filename=file_path.name,
            title=title,
            status=meta.get("status", "draft"),
            version=meta.get("version", "0.0.0"),
            implementation=meta.get("implementation", "0%"),
            tests=meta.get("tests", "0%"),
            last_update=meta.get("last_update", ""),
        )

        specs.append(spec)

    return specs


def get_index_dependencies() -> dict[str, list[str]]:
    """Read dependencies from index file."""
    deps = {}
    index_path = SPECS_DIR / "00-index.md"

    if not index_path.exists():
        return deps

    content = index_path.read_text()
    lines = content.split("\n")

    # Find the header row to identify the dependencies column
    # Header: | # | Spec | Descripción | Dependencias |
    header_idx = -1
    dep_col = 4  # Default fourth column (0-indexed from cells)
    for i, line in enumerate(lines):
        if "| # | Spec | Descripción | Dependencias |" in line or "| # | Spec | Descripcion | Dependencias |" in line:
            header_idx = i
            break

    if header_idx == -1:
        # Try alternate header format from first table
        for i, line in enumerate(lines):
            if re.match(r"\|\s*#\s+\|", line) and "Dependencias" in line:
                header_idx = i
                break

    if header_idx == -1:
        return deps

    # Parse rows after header until we hit a separator line (---) or different table
    for line in lines[header_idx + 1 :]:
        # Stop if we hit a different section (second table with Status instead of Dependencias)
        if "| # | Spec | Status |" in line:
            break

        # Stop if we hit a table separator
        if re.match(r"\|\s*---\s*\|", line):
            continue

        # Skip empty lines
        if line.strip() == "":
            continue

        # Count pipe separators - first table rows have 5 | = 6 cells
        pipe_count = line.count("|")
        if pipe_count == 5:
            cells = [c.strip() for c in line.split("|")]
            if len(cells) == 6 and cells[0] == "" and cells[5] == "":
                spec_num = cells[1]
                # Skip header rows (non-numeric spec numbers)
                if not spec_num.isdigit():
                    continue
                deps_str = cells[dep_col].strip()
                if deps_str and deps_str != "-":
                    dep_nums = re.findall(r"\d+", deps_str)
                    deps[spec_num] = dep_nums
                else:
                    deps[spec_num] = []

    return deps


def calculate_progress(specs: list[SpecInfo]) -> dict:
    """Calculate overall progress metrics."""
    total = len(specs)
    if total == 0:
        return {"total": 0, "by_status": {}, "avg_implementation": 0}

    status_counts = {}
    total_impl = 0

    for spec in specs:
        status_counts[spec.status] = status_counts.get(spec.status, 0) + 1
        impl_pct = int(spec.implementation.rstrip("%")) if spec.implementation != "N/A" else 0
        total_impl += impl_pct

    return {
        "total": total,
        "by_status": status_counts,
        "avg_implementation": total_impl // total if total else 0,
    }


def print_dashboard(specs: list[SpecInfo], verbose: bool = False):
    """Print the spec status dashboard."""
    progress = calculate_progress(specs)
    deps = get_index_dependencies()

    # Header
    print("=" * 70)
    print("ECO SPEC STATUS DASHBOARD".center(70))
    print("=" * 70)

    # Summary
    print(f"\nTotal specs: {progress['total']}")
    print("\nStatus breakdown:")
    for status, count in sorted(progress["by_status"].items()):
        pct = (count / progress["total"]) * 100 if progress["total"] else 0
        bar = "█" * int(pct // 5) + "░" * (20 - int(pct // 5))
        print(f"  [{status:12}] {bar} {count}/{progress['total']} ({pct:.0f}%)")

    print(f"\nAvg implementation: {progress['avg_implementation']}%")

    # Detailed table
    print("\n" + "-" * 70)
    print(f"{'#':>2} {'Spec':<30} {'Status':<12} {'Ver':<6} {'Impl':<6} {'Tests':<6}")
    print("-" * 70)

    for spec in specs:
        status_icon = {
            "stable": "✅",
            "in_progress": "🔄",
            "draft": "📝",
            "deprecated": "⚠️",
        }.get(spec.status, "❓")

        impl_pct = spec.implementation.rstrip("%") if spec.implementation != "N/A" else "?"
        tests_pct = spec.tests.rstrip("%") if spec.tests != "N/A" else "?"

        print(
            f"{spec.number:>2} {spec.title[:28]:<30} {status_icon}{spec.status:<11} "
            f"v{spec.version:<5} {impl_pct:>5}% {tests_pct:>5}%"
        )

    # Dependencies check
    print("\n" + "-" * 70)
    print("Dependencies Check:")
    for spec in specs:
        if spec.number in deps and deps[spec.number]:
            dep_nums = [d.split()[-1] for d in deps[spec.number] if d.strip()]
            dep_statuses = []
            for d in dep_nums:
                for s in specs:
                    if s.number == d:
                        dep_statuses.append(f"{d}:{s.status}")
                        break
            print(f"  spec-{spec.number}: depends on {', '.join(dep_statuses)}")

    print("\n" + "=" * 70)


def print_json(specs: list[SpecInfo]):
    """Print status as JSON for machine parsing."""
    data = {
        "progress": calculate_progress(specs),
        "specs": [
            {
                "number": s.number,
                "title": s.title,
                "status": s.status,
                "version": s.version,
                "implementation": s.implementation,
                "tests": s.tests,
                "last_update": s.last_update,
            }
            for s in specs
        ],
    }
    print(json.dumps(data, indent=2))


def main():
    import argparse

    parser = argparse.ArgumentParser(description="ECO Spec Status Dashboard")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    specs = read_specs()

    if not specs:
        print("No specs found in specs/ directory")
        return

    if args.json:
        print_json(specs)
    else:
        print_dashboard(specs, verbose=args.verbose)


if __name__ == "__main__":
    main()