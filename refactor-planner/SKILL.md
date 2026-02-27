---
name: refactor-planner
description: Analyzes code for smells and complexity, then routes to the appropriate refactoring strategy. Use when you want to refactor or improve code quality.
---

# Refactor Planner

Analyzes code quality issues and recommends targeted refactoring strategies.

## When NOT to Use This Skill

- For formatting-only changes (use a linter/formatter)
- For adding new features (use coding agent)
- When code is already clean and well-structured

## Step 0: Scope Detection

```bash
# If user specifies a file/directory, use that
# Otherwise, analyze recent changes
git --no-pager diff --name-only HEAD~5..HEAD 2>/dev/null | head -20
```

## Step 1: Code Smell Detection

| Smell | Detection | Severity |
|-------|-----------|----------|
| Long function (> 50 lines) | Line count per function | Medium |
| Large file (> 300 lines) | `wc -l` | Medium |
| Deep nesting (> 3 levels) | Indentation analysis | High |
| Duplicate code | Similar blocks across files | High |
| God class/module | File with 10+ exports/methods | High |
| Long parameter list (> 4 params) | Function signatures | Medium |
| Magic numbers/strings | Hardcoded values in logic | Low |
| Dead code | Unused imports, unreachable branches | Low |
| Tight coupling | Circular imports, excessive deps | High |
| Missing error handling | Bare try/catch, unhandled promises | High |

## Step 2: Route Refactoring Strategy

### Strategy A: Extract & Simplify (1-3 files)
Trigger: Long function, deep nesting, magic values

```bash
opencode run "Refactor <file>: extract long functions, flatten nested conditionals, use early returns. Keep behavior identical."
```

### Strategy B: Restructure (4-10 files)
Trigger: God class, tight coupling, structural smells

```bash
git --no-pager diff HEAD | claude -p "Analyze for structural issues. Suggest refactoring with design patterns. Step-by-step plan preserving behavior."
```

### Strategy C: Architecture Overhaul (10+ files)
Trigger: Circular deps, no separation of concerns

```bash
claude -p "Analyze project structure. Suggest architectural refactoring: dependency direction, layer separation, module boundaries. Phased migration plan."
```

## Step 3: Risk Assessment

| Risk | Criteria | Action |
|------|----------|--------|
| Low | Pure logic, good tests | Proceed |
| Medium | Some I/O, partial tests | Add tests first |
| High | DB/API, no tests | Write tests → refactor → verify |

## Step 4: Output

```
## Refactoring Plan

**Scope:** [Small/Medium/Large]
**Strategy:** [Extract / Restructure / Overhaul]
**Risk:** [Low/Medium/High]

**Smells:** [list with severity]
**Actions:** [numbered steps]
**Prerequisites:** Tests + git branch
```
