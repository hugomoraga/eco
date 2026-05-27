#!/usr/bin/env python3
"""
ECO Development Workflow - Git/IA guided local development

This script provides a structured workflow for:
1. Starting development on a spec
2. Tracking progress on specs
3. Creating commits with conventional format
4. Managing version tags for specs
5. Generating PR suggestions

Usage:
    python scripts/dev_workflow.py
    python scripts/dev_workflow.py --spec 05 --action start
    python scripts/dev_workflow.py --spec 05 --action commit
    python scripts/dev_workflow.py --spec 05 --action done
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
SPECS_DIR = PROJECT_ROOT / "specs"
GIT_DIR = PROJECT_ROOT

# ANSI colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def run_cmd(cmd: str) -> tuple[int, str, str]:
    """Run a shell command and return (exit_code, stdout, stderr)."""
    result = subprocess.run(cmd, shell=True, cwd=PROJECT_ROOT, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def get_current_branch() -> str | None:
    """Get current git branch."""
    code, out, _ = run_cmd("git branch --show-current")
    return out.strip() if code == 0 else None


def get_main_branch() -> str:
    """Get the main branch name (main or master)."""
    code, out, _ = run_cmd("git branch -a | grep -E '^(main|master)$'")
    if code == 0:
        return out.strip()
    return "main"


@dataclass
class SpecProgress:
    """Progress tracking for a spec."""

    number: str
    name: str
    status: str = "draft"
    version: str = "0.1.0"
    branch: str = ""
    commits: list[str] = field(default_factory=list)
    implementation: int = 0
    tests: int = 0


def parse_specs_status():
    """Parse current spec status from index and individual specs."""
    specs = []

    for spec_file in sorted(SPECS_DIR.glob("*.md")):
        if spec_file.name == "00-index.md":
            continue

        match = re.match(r"^(\d+)-", spec_file.name)
        if not match:
            continue

        spec_num = match.group(1)
        content = spec_file.read_text()

        # Extract title
        title_match = re.search(r"^#+\s+\d+\.?\s*(.+)$", content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else spec_file.stem

        # Parse status from metadata
        status = "draft"
        if "🔄 En desarrollo" in content or "en desarrollo" in content.lower():
            status = "in_progress"
        elif "✅" in content or "completada" in content.lower() or "stable" in content.lower():
            status = "stable"

        # Parse version
        version_match = re.search(r"version:\s*\"(\d+\.\d+\.\d+)\"", content)
        version = version_match.group(1) if version_match else "0.1.0"

        specs.append(SpecProgress(number=spec_num, name=title, status=status, version=version))

    return specs


def suggest_branch_name(spec_num: str, action: str) -> str:
    """Suggest a branch name based on spec and action."""
    spec_name = ""
    for f in SPECS_DIR.glob(f"{spec_num}-*.md"):
        spec_name = f.stem.split("-")[1] if "-" in f.stem else f.stem
        break

    prefixes = {
        "start": "spec",
        "implement": "feat",
        "commit": "feat",
        "done": "chore",
        "review": "docs",
    }
    prefix = prefixes.get(action, "feat")
    return f"{prefix}/{spec_num}-{spec_name}"


def cmd_start(spec_num: str):
    """Start working on a spec: create branch, update status."""
    print(f"\n{BOLD}{BLUE}=== Starting work on spec-{spec_num} ==={RESET}\n")

    # Get spec info
    spec_file = None
    for f in SPECS_DIR.glob(f"{spec_num}-*.md"):
        spec_file = f
        break

    if not spec_file:
        print(f"{RED}Spec {spec_num} not found!{RESET}")
        return

    spec_name = spec_file.stem.split("-", 1)[-1] if "-" in spec_file.name else spec_file.stem

    # Check current branch
    current = get_current_branch()
    main = get_main_branch()

    print(f"Current branch: {current}")
    print(f"Main branch: {main}")
    print(f"Spec: {spec_name}")

    # Fetch latest
    print("\nFetching latest from origin...")
    run_cmd("git fetch origin")

    # Create branch
    branch = f"spec-{spec_num}/{spec_name}"
    print(f"\nCreating branch: {branch}")
    code, _out, _err = run_cmd(f"git checkout -b {branch} origin/{main}")

    if code != 0:
        # Branch might already exist
        print(f"{YELLOW}Branch exists, checking out existing branch{RESET}")
        run_cmd(f"git checkout {branch}")

    print(f"\n{GREEN}✓ Now working on spec-{spec_num} ({spec_name}){RESET}")
    print(f"Branch: {branch}")

    # Show the spec file path
    print(f"\nSpec file: {spec_file}")

    # Update spec status to in_progress if needed
    content = spec_file.read_text()
    if "Estado: 🔄 En desarrollo" not in content and "en desarrollo" not in content.lower():
        print(f"\n{YELLOW}Note: Spec status should be updated to 'en desarrollo'{RESET}")

    print(f"\n{BOLD}Next steps:{RESET}")
    print(f"  1. Read the spec: cat {spec_file}")
    print("  2. Implement the changes")
    print(f"  3. Run: python scripts/dev_workflow.py --spec {spec_num} --action commit")
    print(f"  4. When done: python scripts/dev_workflow.py --spec {spec_num} --action done")


def cmd_commit(spec_num: str, message: str = ""):
    """Commit current changes for a spec."""
    print(f"\n{BOLD}{BLUE}=== Committing changes for spec-{spec_num} ==={RESET}\n")

    # Check git status
    code, out, _ = run_cmd("git status --porcelain")
    if not out.strip():
        print("No changes to commit.")
        return

    print(f"Changes:\n{out}")

    # Get changed files
    changed_files = [f for f in out.strip().split("\n") if f]
    print(f"\n{len(changed_files)} file(s) changed")

    # Generate commit message if not provided
    if not message:
        # Extract spec name
        spec_name = ""
        for f in SPECS_DIR.glob(f"{spec_num}-*.md"):
            spec_name = f.stem.split("-", 1)[-1]
            break

        print(f"\n{BOLD}Commit message for spec-{spec_num} ({spec_name}):{RESET}")
        print("""
Type options:
  feat:     New functionality
  fix:      Bug fix
  refactor: Code refactoring (no functionality change)
  docs:     Documentation
  test:     Tests
  chore:    Build/tooling changes

Format: <type>(<scope>): <description>
Example: feat(domain): implement PlayerEcho inheritance system

Enter commit message (or 'q' to cancel):""")

        # For automation, generate a suggested message
        message = f"feat(spec-{spec_num}): implement {spec_name}"

    # Stage and commit
    print("\nStaging files...")
    run_cmd("git add -A")

    print(f"Committing: {message}")
    code, out, err = run_cmd(f'git commit -m "{message}"')

    if code == 0:
        print(f"\n{GREEN}✓ Committed successfully{RESET}")
        run_cmd("git log --oneline -3")
    else:
        print(f"{RED}Commit failed: {err}{RESET}")


def cmd_done(spec_num: str):
    """Mark spec as complete, create PR suggestion, tag release."""
    print(f"\n{BOLD}{BLUE}=== Completing spec-{spec_num} ==={RESET}\n")

    # Get spec info
    spec_file = None
    for f in SPECS_DIR.glob(f"{spec_num}-*.md"):
        spec_file = f
        break

    if not spec_file:
        print(f"{RED}Spec {spec_num} not found!{RESET}")
        return

    spec_name = spec_file.stem.split("-", 1)[-1]

    # Get current branch and commits
    branch = get_current_branch()
    _code, out, _ = run_cmd("git log --oneline origin/main..HEAD")
    commits = out.strip().split("\n") if out.strip() else []

    print(f"Branch: {branch}")
    print(f"Commits in this branch: {len(commits)}")

    if commits:
        print("\nCommits:")
        for c in commits:
            print(f"  {c}")

    # Generate PR suggestion
    print(f"\n{BOLD}{GREEN}=== PR SUGGESTION ==={RESET}")
    print(f"""
## Pull Request Template

**Title:** feat(spec-{spec_num}): {spec_name}

**Description:**
- Implementation of spec-{spec_num}: {spec_name}
- {len(commits)} commit(s) in this feature branch

**Changes:**
```bash
git log origin/main..HEAD --oneline
```

**Testing:**
- [ ] Unit tests pass: `pytest`
- [ ] Linting passes: `ruff check game-core/`
- [ ] Type checking passes: `mypy game-core/`

**Checklist:**
- [ ] Spec updated with implementation status
- [ ] Documentation reflects changes
- [ ] No breaking changes to existing functionality

**Labels:** `spec-{spec_num}`, `enhancement`

**Reviewers:** Assign as appropriate

**Closes:** #spec-{spec_num}
""")

    # Suggest git tag
    print(f"\n{BOLD}Suggested Git Tag:{RESET}")
    print(f"  git tag -a spec-{spec_num}/v1.0.0 -m 'spec-{spec_num} ({spec_name}) complete'")
    print(f"  git push origin spec-{spec_num}/v1.0.0")

    # Ask if user wants to create PR
    print(f"\n{YELLOW}Would you like to create a PR now? (y/n){RESET}")
    # In automated mode, just show the suggestion


def cmd_status():
    """Show current development status."""
    print(f"\n{BOLD}{BLUE}=== ECO Development Status ==={RESET}\n")

    branch = get_current_branch()
    main = get_main_branch()

    print(f"Current branch: {GREEN}{branch}{RESET}")
    print(f"Main branch: {main}")

    # Check for uncommitted changes
    code, out, _ = run_cmd("git status --porcelain")
    if out.strip():
        print(f"\n{YELLOW}Uncommitted changes:{RESET}")
        print(out)

    # Show commits since main
    _code, out, _ = run_cmd(f"git log --oneline origin/{main}..HEAD")
    if out.strip():
        print(f"\n{YELLOW}Commits ahead of {main}:{RESET}")
        print(out)

    # Show spec progress
    print(f"\n{BOLD}Spec Progress:{RESET}")
    specs = parse_specs_status()

    for spec in specs:
        status_icon = {"stable": "✅", "in_progress": "🔄", "draft": "📝"}.get(spec.status, "❓")

        print(f"  spec-{spec.number} {status_icon} {spec.name[:40]:<40} v{spec.version}")

    print(f"\nTotal: {len(specs)} specs")
    stable = sum(1 for s in specs if s.status == "stable")
    in_progress = sum(1 for s in specs if s.status == "in_progress")
    print(
        f"  Stable: {stable}, In Progress: {in_progress}, Draft: {len(specs) - stable - in_progress}"
    )


def cmd_tag(spec_num: str, version: str = "v1.0.0"):
    """Create a version tag for a spec."""
    print(f"\n{BOLD}{BLUE}=== Creating tag for spec-{spec_num} ==={RESET}\n")

    # Get spec name
    spec_name = ""
    for f in SPECS_DIR.glob(f"{spec_num}-*.md"):
        spec_name = f.stem.split("-", 1)[-1]
        break

    if not spec_name:
        print(f"{RED}Spec {spec_num} not found!{RESET}")
        return

    tag_name = f"spec-{spec_num}/{version}"
    message = f"spec-{spec_num} ({spec_name}) {version}"

    print(f"Tag: {tag_name}")
    print(f"Message: {message}")

    # Check if tag already exists
    code, out, _ = run_cmd(f"git tag -l '{tag_name}'")
    if out.strip():
        print(f"{YELLOW}Tag already exists!{RESET}")
        print(f"Existing tag: {out}")
        return

    # Create tag
    print("\nCreating tag...")
    code, out, err = run_cmd(f'git tag -a "{tag_name}" -m "{message}"')

    if code == 0:
        print(f"{GREEN}✓ Tag created{RESET}")
        print(f"\nTo push: git push origin {tag_name}")
    else:
        print(f"{RED}Failed to create tag: {err}{RESET}")


def cmd_pr(spec_num: str):
    """Generate PR body for a spec."""
    print(f"\n{BOLD}{BLUE}=== PR for spec-{spec_num} ==={RESET}\n")

    # Get spec info
    spec_file = None
    for f in SPECS_DIR.glob(f"{spec_num}-*.md"):
        spec_file = f
        break

    if not spec_file:
        print(f"{RED}Spec {spec_num} not found!{RESET}")
        return

    spec_name = spec_file.stem.split("-", 1)[-1]
    content = spec_file.read_text()

    # Count commits
    get_current_branch()
    _code, out, _ = run_cmd("git log --oneline origin/main..HEAD")
    commits = out.strip().split("\n") if out.strip() else []

    # Extract key sections from spec
    # Look for implementation notes, formulas, etc.
    sections = []
    for line in content.split("\n"):
        if line.startswith("## "):
            sections.append(line.replace("## ", ""))

    print(f"""
## Pull Request: spec-{spec_num}

**Title:** feat(spec-{spec_num}): {spec_name}

### Summary
Implementation of [{spec_name}](specs/{spec_num.zfill(2)}-{spec_name}.md) specification.

### Spec Sections Covered
{chr(10).join(f"- {s}" for s in sections[:5])}

### Commits ({len(commits)} total)
```
{out if out else "(no commits yet)"}
```

### Checklist
- [ ] Implementation matches spec
- [ ] Tests cover new functionality
- [ ] Documentation updated
- [ ] No regression in existing features

### Notes for Reviewer
<!-- Add any notes about edge cases, design decisions, etc. -->

**Labels:** `spec-{spec_num}`, `enhancement`
**Reviewers:** @hugo (suggested)
""")


def cmd_diff(spec_num: str):
    """Show diff for spec changes."""
    print(f"\n{BOLD}{BLUE}=== Diff for spec-{spec_num} ==={RESET}\n")

    _code, out, _ = run_cmd("git diff origin/main -- '*.py' '*.md' | head -100")
    if out:
        print(out[:3000])  # Limit output
    else:
        print("No changes detected.")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="ECO Development Workflow")
    parser.add_argument("--spec", help="Spec number (e.g., 05)")
    parser.add_argument(
        "--action",
        choices=["start", "commit", "done", "status", "tag", "pr", "diff"],
        help="Action to perform",
    )
    parser.add_argument("--message", "-m", help="Commit message")
    parser.add_argument("--version", "-v", help="Version for tag (default: v1.0.0)")

    args = parser.parse_args()

    if args.action == "status":
        cmd_status()
    elif args.spec and args.action == "start":
        cmd_start(args.spec)
    elif args.spec and args.action == "commit":
        cmd_commit(args.spec, args.message or "")
    elif args.spec and args.action == "done":
        cmd_done(args.spec)
    elif args.spec and args.action == "tag":
        cmd_tag(args.spec, args.version or "v1.0.0")
    elif args.spec and args.action == "pr":
        cmd_pr(args.spec)
    elif args.spec and args.action == "diff":
        cmd_diff(args.spec)
    else:
        # Interactive mode - show status and prompt for action
        cmd_status()
        print(f"""
{BOLD}Available Actions:{RESET}
  --spec NN --action start    Start working on spec (creates branch)
  --spec NN --action commit   Commit current changes
  --spec NN --action done     Mark spec complete, show PR suggestion
  --spec NN --action tag      Create version tag
  --spec NN --action pr       Generate PR body
  --spec NN --action diff     Show changes since main

  --action status            Show current status
""")


if __name__ == "__main__":
    main()
