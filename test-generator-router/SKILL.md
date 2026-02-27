---
name: test-generator-router
description: Analyzes code changes and routes to the appropriate test generation strategy (unit, integration, or E2E). Use when you want to generate tests for your current changes.
triggers:
  - test
  - 测试
  - 生成测试
  - 单元测试
  - unit test
  - 写测试
  - 补测试
---

# Test Generator Router

Routes test generation to the optimal strategy based on code change characteristics.

## When NOT to Use This Skill

- For existing test modifications (just edit directly)
- For non-testable changes (docs, config formatting)
- When the project has no test framework set up

## Step 0: Environment & Test Framework Detection

```bash
git rev-parse --git-dir 2>/dev/null || echo "NOT_A_GIT_REPO"
```

Detect test framework:

| File/Pattern | Framework | Type |
|-------------|-----------|------|
| `jest.config.*`, `node_modules/jest` | Jest | JS/TS |
| `vitest.config.*` | Vitest | JS/TS |
| `pytest.ini`, `conftest.py`, `pyproject.toml[tool.pytest]` | Pytest | Python |
| `Package.swift` with XCTest | XCTest | Swift |
| `*_test.go` | Go testing | Go |
| `Cargo.toml` with `[dev-dependencies]` | Rust test | Rust |
| `cypress/`, `cypress.config.*` | Cypress | E2E |
| `playwright.config.*` | Playwright | E2E |

**If no test framework detected:** Suggest setting one up first.

## Step 1: Analyze Changes

```bash
git --no-pager diff --cached --name-only 2>/dev/null || git --no-pager diff --name-only HEAD
git --no-pager diff --cached HEAD 2>/dev/null || git --no-pager diff HEAD
```

## Step 2: Classify & Route

### → Unit Tests (isolated, single function/class)

Trigger when:
- Single file changed with new/modified functions
- Utility/helper files (`utils/`, `helpers/`, `lib/`)
- Pure logic (no I/O, no DB, no network)
- Model/entity changes
- Lines changed < 100

### → Integration Tests (multiple components interacting)

Trigger when:
- API route/controller + service layer both changed
- Database schema + model changes
- Middleware modifications
- Files span 2+ directories
- Import chains suggest component interaction

### → E2E Tests (full user flow)

Trigger when:
- UI components + API routes both changed
- Auth flow modifications
- Payment/checkout changes
- User-facing workflow changes
- E2E framework already exists in project

## Step 3: Execute Generation

### For Unit Tests
```bash
# OpenCode for quick unit tests
opencode run "Analyze the uncommitted changes and generate unit tests. Follow existing test patterns in the project. Use the project's test framework. Focus on edge cases and error handling."
```

### For Integration/E2E Tests
```bash
# Claude Code for complex test scenarios
git --no-pager diff HEAD | claude -p "Analyze this diff and generate integration tests. Consider component interactions, error propagation, and data flow. Follow existing test patterns in the project."
```

## Step 4: Fallback

If primary CLI fails, try the alternative. If both fail, output the test strategy as a plan for manual implementation.

## Step 5: Output

```
## Test Generation Results

**Strategy:** [Unit/Integration/E2E]
**Framework:** [detected framework]
**Routing:** [OpenCode/Claude Code] — [reason]

---
[Generated tests]
---

**Files to create/modify:**
- [list of test files]
```
