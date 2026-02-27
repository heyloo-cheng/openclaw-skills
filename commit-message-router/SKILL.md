---
name: commit-message-router
description: Intelligently generates commit messages based on change characteristics. Routes between concise format for small fixes and conventional commits with detailed body for larger changes. Use when you want to generate a commit message for your current changes.
---

# Commit Message Router

Generates optimal commit messages based on change size, type, and complexity.

## When NOT to Use This Skill

- When the user has a specific commit message in mind
- For merge commits (use default merge message)
- For empty commits

## Step 0: Environment Check

```bash
git rev-parse --git-dir 2>/dev/null || echo "NOT_A_GIT_REPO"
git diff --cached --name-only | wc -l  # Check staged changes
git diff --name-only | wc -l           # Check unstaged changes
```

**If no changes:** "Nothing to commit."

## Step 1: Analyze Changes

```bash
# Staged changes (preferred) or unstaged
git --no-pager diff --cached --stat 2>/dev/null || git --no-pager diff --stat
git --no-pager diff --cached --numstat 2>/dev/null || git --no-pager diff --numstat
git --no-pager diff --cached --name-only 2>/dev/null || git --no-pager diff --name-only
```

## Step 2: Classify Change Type

| Pattern | Type | Prefix |
|---------|------|--------|
| Test files only (`*test*`, `*spec*`) | test | `test:` |
| Docs only (`*.md`, `*.txt`, `*.rst`) | docs | `docs:` |
| Config only (`*.json`, `*.yaml`, `*.toml`, `*.config.*`) | chore | `chore:` |
| CI files (`.github/`, `Jenkinsfile`, `*.yml` in CI dirs) | ci | `ci:` |
| Style only (`*.css`, `*.scss`, formatting changes) | style | `style:` |
| Bug fix (small, single file, < 30 lines) | fix | `fix:` |
| New file(s) added | feat | `feat:` |
| File(s) deleted | refactor | `refactor:` |
| Dependency updates (`package.json`, `Gemfile`, `go.mod`) | chore | `chore(deps):` |
| Mixed / unclear | feat or fix | Determine from diff content |

## Step 3: Route by Size

### Small Changes (≤ 3 files, ≤ 50 lines)
→ **Concise format**: Single line, no body

```
<type>: <short description>
```

Example: `fix: correct null check in user validation`

### Medium Changes (4-10 files, 51-200 lines)
→ **Standard conventional commit**: Subject + brief body

```
<type>(<scope>): <short description>

- Change 1
- Change 2
```

### Large Changes (> 10 files OR > 200 lines)
→ **Detailed conventional commit**: Subject + body + footer

```
<type>(<scope>): <short description>

<paragraph explaining why and what>

Changes:
- Detail 1
- Detail 2
- Detail 3

Breaking changes: <if any>
```

## Step 4: Generate Message

Use the diff content to write a specific, meaningful message:

- Subject line ≤ 72 characters
- Use imperative mood ("add", "fix", "update", not "added", "fixed")
- Be specific (not "fix bug" but "fix null pointer in auth middleware")
- Scope = primary module/directory affected
- Body explains WHY, not just WHAT

## Step 5: Present and Confirm

```
## Commit Message

**Format:** [Concise/Standard/Detailed]
**Type:** [type]

---
<generated message>
---

Apply this commit? (or edit first)
```

If user approves, run:
```bash
git commit -m "<message>"
```
