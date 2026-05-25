#!/usr/bin/env python3
import re
from pathlib import Path

SPECS_DIR = Path('specs')

def get_index_dependencies() -> dict[str, list[str]]:
    """Read dependencies from index file."""
    deps = {}
    index_path = SPECS_DIR / "00-index.md"

    if not index_path.exists():
        return deps

    content = index_path.read_text()
    lines = content.split("\n")

    # Find the header row to identify the dependencies column
    header_idx = -1
    dep_col = 4  # Default fourth column (0-indexed from cells)
    for i, line in enumerate(lines):
        if "| # | Spec | Descripción | Dependencias |" in line or "| # | Spec | Descripcion | Dependencias |" in line:
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

result = get_index_dependencies()
print(f"Result: {result}")
