---
name: task-estimator
description: Estimates task complexity and time based on requirement description. Routes between quick estimation and detailed breakdown. Use when estimating effort for a coding task.
triggers:
  - estimate
  - 估时
  - 评估
  - 工作量
  - 多久
  - complexity
  - 排期
  - 估算
---

# Task Estimator

Analyzes requirements and provides time/complexity estimates with confidence levels.

## When NOT to Use This Skill

- For tasks already in progress (just track actual time)
- For non-technical tasks
- For vague one-word descriptions (ask for more detail first)

## Step 1: Parse Requirement

Extract from user's description:
- **What:** Core deliverable
- **Scope:** Files/modules likely affected
- **Dependencies:** External services, APIs, libraries
- **Unknowns:** Ambiguous or undefined aspects

## Step 2: Complexity Classification

| Factor | Low (1) | Medium (2) | High (3) |
|--------|---------|------------|----------|
| Scope | 1-2 files | 3-10 files | 10+ files |
| Domain knowledge | Familiar | Some research | New territory |
| Dependencies | None | Internal only | External APIs/services |
| Testing needs | Existing tests | New unit tests | Integration + E2E |
| Risk | No breaking changes | Minor migration | Schema/API changes |
| Ambiguity | Clear spec | Some unknowns | Many unknowns |

**Total score:** Sum all factors (6-18)

| Score | Complexity | T-shirt |
|-------|------------|---------|
| 6-8 | Simple | S |
| 9-12 | Moderate | M |
| 13-15 | Complex | L |
| 16-18 | Very Complex | XL |

## Step 3: Route Estimation Strategy

### Simple (S) — Quick Estimate
```
Estimate directly based on pattern matching:
- Bug fix, single file → 0.5-2h
- New utility function → 1-3h
- Config change → 0.5-1h
- Doc update → 0.5-2h
```

### Moderate (M) — Breakdown Estimate
```bash
opencode run "Break down this task into subtasks with time estimates: <requirement>. Consider: implementation, testing, code review, edge cases. Output as a table."
```

### Complex (L/XL) — Deep Analysis
```bash
claude -p "Analyze this requirement and provide a detailed estimate: <requirement>. Include: 1) Task breakdown with dependencies, 2) Risk factors and unknowns, 3) Time range (optimistic/realistic/pessimistic), 4) Suggested approach, 5) What to clarify before starting."
```

## Step 4: Apply Multipliers

| Factor | Multiplier |
|--------|------------|
| First time with this codebase | ×1.5 |
| Unclear requirements | ×1.5 |
| No existing tests | ×1.3 |
| Cross-team dependency | ×1.5 |
| Production hotfix (pressure) | ×0.8 (cut scope) |

## Step 5: Output

```
## Task Estimate

**Task:** [description]
**Complexity:** [S/M/L/XL] ([score]/18)
**Confidence:** [High/Medium/Low]

**Breakdown:**
| Subtask | Estimate | Risk |
|---------|----------|------|
| [task 1] | [time] | [low/med/high] |
| [task 2] | [time] | [low/med/high] |

**Total:**
- Optimistic: [time]
- Realistic: [time]
- Pessimistic: [time]

**Unknowns to clarify:** [list]
**Suggested approach:** [brief strategy]
```
