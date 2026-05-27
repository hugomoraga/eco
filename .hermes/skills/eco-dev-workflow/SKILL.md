---
name: eco-dev-workflow
description: "ECO development workflow: spec-driven development with AI guidance, local git workflow, and GitHub integration."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [development, workflow, specs, git, github, version-control]
    related_skills: [github-pr-workflow, github-issues, spec_status]
---

# ECO Development Workflow

Complete workflow for developing ECO using spec-driven development with AI agent guidance.

## Core Principle

**Spec first, code second.** Every code change must be preceded by a spec change.

```
Correct flow:
  spec-05.md → implement → commit → PR → merge

Incorrect flow (reversed):
  code → adjust spec (going backwards = technical debt)
```

---

## 1. Starting Work on a Spec

### Before You Start

```bash
# Always work from main branch
git checkout main && git pull origin main

# Show current status
python scripts/dev_workflow.py --action status
python scripts/spec_status.py
```

### Starting a Spec

```bash
# Start working on spec-05
python scripts/dev_workflow.py --spec 05 --action start

# This will:
# 1. Fetch latest from origin
# 2. Create branch: spec-05/ideas-doctrines
# 3. Show spec file path
```

### What to Do After Starting

1. **Read the spec** thoroughly
2. **Understand dependencies** (check which specs must be complete first)
3. **Plan implementation** in small, atomic commits
4. **Follow coding conventions** in AGENT.md

---

## 2. Making Commits

### During Implementation

```bash
# Commit with conventional format
python scripts/dev_workflow.py --spec 05 --action commit -m "feat(domain): add Idea entity with virality attributes"

# Or use interactive mode (it will prompt for message)
python scripts/dev_workflow.py --spec 05 --action commit
```

### Commit Message Format

```
<type>(<scope>): <description>

[optional body]

[optional footer with issue refs]
```

**Types:**
- `feat`: New functionality
- `fix`: Bug fix
- `refactor`: Code restructuring without behavior change
- `docs`: Documentation changes
- `test`: Adding or modifying tests
- `chore`: Build system, tooling, dependency updates

**Examples:**
```bash
feat(domain): add PlayerEcho with incarnation inheritance

- clarity, resonance, presence, memory, will, shadow
- inheritance system between incarnations
- persistence formulas based on will

Closes: #spec-03

fix(engine): correct overflow in derive_pressure formula

The multiplication of pressures could overflow for large values.
Now uses weighted sum instead.

Fixes: #runtime-issue-42
```

### Best Practices for Commits

- **Atomic commits**: One logical change per commit
- **Testable units**: Each commit should leave tests passing
- **Clear messages**: Explain *why*, not just *what*
- **Reference specs**: Include spec number in footer

---

## 3. Tracking Progress

### Check Spec Status

```bash
# Quick dashboard
python scripts/spec_status.py

# Detailed JSON output for automation
python scripts/spec_status.py --json
```

### Update Spec Status

When you complete a section of a spec, update its metadata:

```markdown
## Metadata

- Status: 🔄 En desarrollo
- Version: 0.2.0
- Implementation: 60%
- Tests: 40%
- Last Update: 2026-05-24
```

### Dependency Tracking

The dashboard shows which specs depend on others. Always implement in topological order:

```
Order: 01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09 → 10 → 11 → 12 → 13 → 14 → 15 → 16 → 17 → 18
```

---

## 4. Completing a Spec

### Marking Done

```bash
# When spec implementation is complete
python scripts/dev_workflow.py --spec 05 --action done

# This will:
# 1. Show all commits in branch
# 2. Generate PR suggestion
# 3. Suggest git tag
```

### Creating the Git Tag

```bash
# Create version tag for the spec
python scripts/dev_workflow.py --spec 05 --action tag --version v1.0.0

# Push tag
git push origin spec-05/v1.0.0
```

### Tag Format

```
spec-<number>/<version>

Examples:
  spec-01/v1.0.0
  spec-03/v0.2.0
  spec-14/v1.1.0
```

---

## 5. GitHub Integration

### Creating a Pull Request

```bash
# After committing, push branch
git push -u origin HEAD

# Create PR
gh pr create \
  --title "feat(spec-05): ideas and doctrines system" \
  --body "## Summary
- Implementation of spec-05: Ideas y Doctrinas
- Added Idea and Doctrine entities
- Virality calculation system

## Testing
- [ ] Unit tests pass
- [ ] Type checking passes

Closes: #spec-05" \
  --label "spec-05,enhancement"
```

### Generating PR Body

```bash
# Auto-generate PR body from spec
python scripts/dev_workflow.py --spec 05 --action pr
```

### Monitoring CI

```bash
# Check CI status
gh pr checks --watch

# Or with curl
SHA=$(git rev-parse HEAD)
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/OWNER/REPO/commits/$SHA/status
```

### Auto-Fix CI Failures

```bash
# View failed logs
gh run view <run-id> --log-failed

# Fix and push
git add -A && git commit -m "fix: resolve CI failure in lint" && git push
```

### Merging

```bash
# Squash and merge
gh pr merge --squash --delete-branch

# Enable auto-merge
gh pr merge --auto --squash --delete-branch
```

---

## 6. Workflow Commands Reference

| Action | Command |
|--------|---------|
| Show status | `python scripts/dev_workflow.py --action status` |
| Show spec progress | `python scripts/spec_status.py` |
| Start spec | `python scripts/dev_workflow.py --spec 05 --action start` |
| Commit changes | `python scripts/dev_workflow.py --spec 05 --action commit -m "message"` |
| Complete spec | `python scripts/dev_workflow.py --spec 05 --action done` |
| Create tag | `python scripts/dev_workflow.py --spec 05 --action tag --version v1.0.0` |
| Generate PR | `python scripts/dev_workflow.py --spec 05 --action pr` |
| Show diff | `python scripts/dev_workflow.py --spec 05 --action diff` |

---

## 7. Versioning Strategy

### Semantic Versioning per Spec

Each spec is versioned independently:

```
spec-01/v1.0.0  - Major version (stable API)
spec-01/v1.1.0  - Minor version (backward compatible addition)
spec-01/v2.0.0  - Major version (breaking changes)
```

### When to Tag

- **v1.0.0**: Spec implementation complete and tested
- **v0.x.x**: Draft or in-progress implementation
- **Patch versions**: Bug fixes without spec changes

### Git Tag Workflow

```bash
# Create tag locally
git tag -a spec-05/v1.0.0 -m "spec-05 (ideas and doctrines) v1.0.0"

# Push to remote
git push origin spec-05/v1.0.0

# List all spec tags
git tag -l "spec-*"

# Delete local tag (if mistake)
git tag -d spec-05/v1.0.0

# Delete remote tag
git push origin --delete tag spec-05/v1.0.0
```

---

## 8. Common Workflows

### Bug Fix Workflow

```bash
# 1. Create fix branch from main
git checkout main && git pull
git checkout -b fix/issue-42-login-redirect

# 2. Fix and commit
git add src/auth.py tests/test_auth.py
git commit -m "fix: correct redirect URL after login

Preserves ?next= parameter instead of always going to /dashboard."

# 3. Push and PR
git push -u origin HEAD
gh pr create --title "fix: correct login redirect" --body "..."

# 4. Merge after CI
gh pr merge --squash --delete-branch
```

### Feature Branch Workflow

```bash
# 1. Start from main
git checkout main && git pull
git checkout -b feat/add-player-echo

# 2. Make multiple commits
git add src/domain/player_echo.py
git commit -m "feat(domain): add PlayerEcho entity"
git add tests/test_player_echo.py
git commit -m "test: add PlayerEcho tests"

# 3. Push and PR
git push -u origin HEAD
gh pr create --title "feat(domain): add PlayerEcho entity" --body "..."

# 4. Update spec status to "stable" after merge
```

### Spec Implementation Workflow

```bash
# 1. Start spec
python scripts/dev_workflow.py --spec 05 --action start

# 2. Work on spec (multiple commits)
# ... implementation ...

# 3. Commit with spec reference
git commit -m "feat(spec-05): implement Ideas and Doctrines

- Added Idea entity with clarity, virality, stability
- Added Doctrine with genealogical tracking
- Implemented virality threshold calculation

Closes: #spec-05"

# 4. Complete spec
python scripts/dev_workflow.py --spec 05 --action done

# 5. Create tag
python scripts/dev_workflow.py --spec 05 --action tag --version v1.0.0

# 6. Push and create PR
git push -u origin HEAD
gh pr create --title "feat(spec-05): ideas and doctrines system" ...
```

---

## 9. GitHub PR Templates

### Feature PR Template

```markdown
## Summary
<!-- What does this PR do? -->

## Spec Reference
- Implements: [spec-XX](specs/XX-name.md)
- Related specs: [spec-XX](specs/XX-name.md)

## Changes
<!-- Detailed list of changes -->

## Testing
- [ ] Unit tests pass: `pytest`
- [ ] Type checking passes: `mypy game-core/`
- [ ] Linting passes: `ruff check game-core/`
- [ ] Reproducibility verified (same seed = same result)

## Checklist
- [ ] Implementation matches spec
- [ ] No regression in existing features
- [ ] Documentation updated
- [ ] No breaking changes

## Notes
<!-- Any additional context for reviewers -->
```

### Bug Fix PR Template

```markdown
## Bug Description
<!-- What was the bug? -->

## Root Cause
<!-- Why did it happen? -->

## Fix
<!-- How was it fixed? -->

## Testing
- [ ] Test that reproduces the bug passes
- [ ] Existing tests still pass
- [ ] Edge cases considered

## Related
- Closes: #issue-number
- Related to: #spec-XX
```

---

## 10. Troubleshooting

### "Branch already exists" error

```bash
# Branch exists locally or remotely
git branch -a | grep spec-05
git checkout spec-05/ideas-doctrines
git pull origin spec-05/ideas-doctrines
```

### "Detached HEAD" state

```bash
# Create a branch from the current commit
git checkout -b fix/my-fix
```

### "Uncommitted changes" warning before starting new spec

```bash
# Stash changes
git stash
git checkout main

# Later, retrieve stashed changes
git stash pop
```

### Lost commits after bad rebase

```bash
# Find lost commits
git reflog
git checkout -b recovery <commit-sha>

# Or reset to known good state
git reset --hard origin/main
```

### GitHub token issues

```bash
# Check if token is set
echo $GITHUB_TOKEN

# Set if missing
export GITHUB_TOKEN=your_token_here

# Or configure git credential helper
git config --global credential.helper store
```

---

## 11. Best Practices Summary

1. **Always start from main**: `git checkout main && git pull`
2. **One spec per branch**: Keep features focused
3. **Commit early, commit often**: Small atomic commits
4. **Reference specs in commits**: Include `#spec-XX` in footer
5. **Update spec status**: Mark progress in spec metadata
6. **Test before pushing**: Ensure tests pass locally
7. **Review before PR**: Self-review changes with `git diff`
8. **Tag on completion**: Create version tag when spec is stable
9. **Monitor CI**: Don't ignore failing checks
10. **Clean up after merge**: Delete branches and tags

---

## Scripts Location

- `scripts/dev_workflow.py` - Main development workflow commands
- `scripts/spec_status.py` - Spec progress dashboard

Both scripts are in the project root and can be run from anywhere in the project.