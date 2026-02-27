---
name: code-review-router
description: Intelligently routes code reviews between OpenCode and Claude Code based on tech stack, complexity, and change characteristics. Use when you want an automated code review of your current changes.
---

# Code Review Router

Routes code reviews to the optimal CLI (OpenCode or Claude Code) based on change characteristics.

## When NOT to Use This Skill

- For non-code reviews (documentation proofreading, prose editing)
- When reviewing external/third-party code you don't control
- For commit message generation (use a dedicated commit skill)
- When you need a specific reviewer (use that CLI directly)

## Step 0: Environment Check

Verify we're in a git repository:

```bash
git rev-parse --git-dir 2>/dev/null || echo "NOT_A_GIT_REPO"
```

**If not a git repo:** Stop and inform the user: "This directory is not a git repository. Initialize with `git init` or navigate to a repo."

## Step 1: Prerequisites Check

Verify both CLIs are available:

```bash
# Check for OpenCode
which opencode || echo "OPENCODE_NOT_FOUND"

# Check for Claude Code
which claude || echo "CLAUDE_NOT_FOUND"
```

**If neither CLI is found:** Stop and inform the user they need to install at least one:
- OpenCode: `curl -fsSL https://opencode.ai/install | bash`
- Claude Code: `npm install -g @anthropic-ai/claude-code`

**If only one CLI is available:** Use that CLI (no routing needed).

**If both are available:** Proceed with routing analysis.

## Step 2: Analyze Git Diff

Run these commands to gather diff statistics:

```bash
# Get diff stats (staged + unstaged)
git --no-pager diff --stat HEAD 2>/dev/null || git --no-pager diff --stat

# Get full diff for pattern analysis
git --no-pager diff HEAD 2>/dev/null || git --no-pager diff

# Count changed files
git --no-pager diff --name-only HEAD 2>/dev/null | wc -l

# Count total changed lines
git --no-pager diff --numstat HEAD 2>/dev/null | awk '{added+=$1; removed+=$2} END {print added+removed}'
```

**If no changes detected:** Report "Nothing to review - no uncommitted changes found." and stop.

## Step 3: Calculate Complexity Score

Initialize `complexity_score = 0`, then add points:

| Condition | Points | Detection Method |
|-----------|--------|------------------|
| Files changed > 10 | +2 | `git diff --name-only \| wc -l` |
| Files changed > 20 | +3 | (additional, total +5) |
| Lines changed > 300 | +2 | `git diff --numstat` sum |
| Lines changed > 500 | +3 | (additional, total +5) |
| Multiple directories touched | +1 | Count unique dirs in changed files |
| Test files included | +1 | Files matching `*test*`, `*spec*` |
| Config files changed | +1 | Files: `*.config.*`, `*.json`, `*.yaml`, `*.yml`, `*.toml` |
| Database/schema changes | +2 | Files: `*migration*`, `*schema*`, `*.sql`, `prisma/*` |
| API route changes | +2 | Files in `api/`, `routes/`, containing `endpoint`, `handler` |
| Service layer changes | +2 | Files in `services/`, `*service*`, `*provider*` |

## Step 4: Detect Language & Framework

Analyze file extensions and content patterns:

### Primary Language Detection
```
.ts, .tsx     → TypeScript
.js, .jsx     → JavaScript
.py           → Python
.go           → Go
.rs           → Rust
.java         → Java
.rb           → Ruby
.php          → PHP
.cs           → C#
.swift        → Swift
.kt           → Kotlin
```

### Framework Detection (check imports/file patterns)
```
React/Next.js    → "import React", "from 'react'", "next.config", pages/, app/
Vue              → ".vue" files, "import Vue", "from 'vue'"
Angular          → "angular.json", "@angular/core"
Django           → "django", "models.py", "views.py", "urls.py"
FastAPI          → "from fastapi", "FastAPI("
Express          → "express()", "from 'express'"
NestJS           → "@nestjs/", "*.module.ts", "*.controller.ts"
Rails            → "Gemfile" with rails, app/controllers/
Spring           → "springframework", "@RestController"
SwiftUI          → "import SwiftUI", "View", "body: some View"
UIKit            → "import UIKit", "UIViewController"
```

### Security-Sensitive Patterns

Detect by **file path** OR **code content**:

**File paths:**
```
**/auth/**
**/security/**
**/*authentication*
**/*authorization*
**/middleware/auth*
```

**Code patterns (in diff content):**
```
password\s*=
api_key\s*=
secret\s*=
Bearer\s+
JWT
\.env
credentials
private_key
access_token
```

**Config files:**
```
.env*
*credentials*
*secrets*
*.pem
*.key
```

## Step 5: Apply Routing Decision Tree

**Routing Priority Order** (evaluate top-to-bottom, first match wins):

### Priority 1: Pattern-Based Rules (Hard Rules)

| Pattern | Route | Reason |
|---------|-------|--------|
| Security-sensitive files/code detected | **Claude Code** | Requires careful security analysis |
| Files > 20 OR lines > 500 | **Claude Code** | Large changeset needs thorough review |
| Database migrations or schema changes | **Claude Code** | Architectural risk |
| API/service layer modifications | **Claude Code** | Backend architectural changes |
| Changes span 3+ top-level directories | **Claude Code** | Multi-service impact |
| Complex TypeScript (generics, type utilities) | **Claude Code** | Type system complexity |
| Swift/iOS project changes | **Claude Code** | Native app complexity |
| Pure frontend only (jsx/tsx/vue/css/html) | **OpenCode** | Simpler, visual-focused review |
| Python ecosystem (py, Django, FastAPI) | **OpenCode** | Quick feedback loop |
| Documentation only (md/txt/rst) | **OpenCode** | Simple text review |
| Single file, < 50 lines changed | **OpenCode** | Fast review for small changes |

### Priority 2: Complexity Score (if no pattern matched)

| Score | Route | Reason |
|-------|-------|--------|
| ≥ 6 | **Claude Code** | High complexity warrants deeper analysis |
| < 6 | **OpenCode** | Moderate complexity, prefer speed |

### Priority 3: Default

→ **OpenCode** (faster feedback loop for unclear cases)

## Step 6: Execute Review

### Explain Routing Decision

Before executing, output:

```
## Code Review Routing

**Changes detected:**
- Files: [X] files changed
- Lines: [Y] lines modified
- Primary language: [language]
- Framework: [framework or "none detected"]

**Complexity score:** [N]/10
- [List contributing factors]

**Routing decision:** [OpenCode/Claude Code]
- Reason: [primary reason for choice]

**Executing review...**
```

### CLI Commands

**For OpenCode:**
```bash
# Use run command with review prompt
cd <project-dir> && opencode run "Review the current uncommitted changes (git diff HEAD) for: 1) Code quality issues, 2) Best practices violations, 3) Potential bugs, 4) Security concerns, 5) Performance issues. Provide specific, actionable feedback."
```

**For Claude Code:**
```bash
# Use non-interactive print mode with diff piped in
git --no-pager diff HEAD | claude -p "Review this code diff for: 1) Code quality issues, 2) Best practices violations, 3) Potential bugs, 4) Security concerns, 5) Performance issues. Provide specific, actionable feedback."
```

## Step 7: Handle Failures with Fallback

If the chosen CLI fails (non-zero exit or error output):

1. **Report the failure:**
   ```
   [Primary CLI] failed: [error message]
   Attempting fallback to [other CLI]...
   ```

2. **Try the alternative CLI**

3. **If fallback also fails:**
   ```
   Both review CLIs failed.
   - OpenCode error: [error]
   - Claude Code error: [error]

   Please check CLI installations and try manually.
   ```

## Step 8: Format Output

Present the review results clearly:

```
## Code Review Results

**Reviewed by:** [OpenCode/Claude Code]
**Routing:** [brief reason]

---

[CLI output here]

---

**Review complete.** [X files, Y lines analyzed]
```

## Quick Reference

| Change Type | Route | Reason |
|-------------|-------|--------|
| React component styling | OpenCode | Pure frontend |
| Django view update | OpenCode | Python ecosystem |
| Single bug fix < 50 lines | OpenCode | Simple change |
| New API endpoint + tests | Claude Code | Architectural |
| Auth system changes | Claude Code | Security-sensitive |
| Database migration | Claude Code | Schema change |
| Multi-service refactor | Claude Code | High complexity |
| TypeScript type overhaul | Claude Code | Complex types |
| Swift/iOS feature | Claude Code | Native app complexity |
