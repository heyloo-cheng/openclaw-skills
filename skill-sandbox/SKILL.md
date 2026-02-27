---
name: skill-sandbox
description: Validates and dry-run tests new or modified skills before deployment. Use when creating, modifying, or importing a new skill to verify it works correctly.
triggers:
  - skill test
  - 测试skill
  - validate skill
  - dry run
  - 沙盒测试
  - skill验证
  - 验证skill
---

# Skill Sandbox

Validates skill structure, simulates execution, and runs test cases.

## When to Use

- After creating a new skill
- After modifying an existing skill
- After importing a skill from clawhub or external source
- Before registering a skill to the registry

## Step 1: Structure Validation

Check the SKILL.md file:

```bash
SKILL_PATH="<path to SKILL.md>"
[ -f "$SKILL_PATH" ] || echo "ERROR: File not found"
```

### Required Checks
- [ ] File exists and is readable
- [ ] Has YAML frontmatter (starts with `---`)
- [ ] `name` field present in frontmatter
- [ ] `description` field present in frontmatter
- [ ] Description is meaningful (> 20 chars)
- [ ] Has at least one `## Step` or `## When` section
- [ ] No broken markdown (unclosed code blocks)

### Recommended Checks
- [ ] Has `triggers` in frontmatter or in skill-triggers.json
- [ ] Has `examples` defined
- [ ] Referenced CLI tools exist on system
- [ ] Referenced file paths exist

### Validation Output
```
## Skill Validation: [skill-name]

Structure:
  ✅ Frontmatter present
  ✅ name: "code-review-router"
  ✅ description: (85 chars)
  ⚠️  No triggers defined — add to skill-triggers.json
  ✅ 8 steps found

Dependencies:
  ✅ opencode — found at /Users/boton/.opencode/bin/opencode
  ✅ claude — found at /opt/homebrew/bin/claude
  ✅ git — found at /usr/bin/git
  ❌ codex — NOT FOUND

Result: PASS (1 warning, 0 errors)
```

## Step 2: Dry-Run Simulation

Parse all steps and list what would be executed WITHOUT running anything:

```
## Dry-Run: [skill-name]

Step 0: Environment Check
  → Would run: git rev-parse --git-dir
  → Checks: git repository exists

Step 1: Prerequisites Check
  → Would run: which opencode, which claude
  → Checks: CLI availability

Step 2: Analyze Git Diff
  → Would run: git diff --stat HEAD, git diff --numstat HEAD
  → Reads: current uncommitted changes

Step 3: Calculate Complexity Score
  → Logic: score based on files/lines/patterns
  → No commands executed

Step 4: Detect Language
  → Logic: file extension analysis
  → No commands executed

Step 5: Route Decision
  → Logic: pattern match → complexity score → default
  → Output: selected CLI + reason

Step 6: Execute Review
  → Would run: opencode run "..." OR git diff | claude -p "..."
  → ⚠️  This is the actual execution step

Step 7: Fallback
  → Would run: alternative CLI if primary fails

Step 8: Format Output
  → Logic: format and present results
```

## Step 3: Test Cases

If test cases exist in `~/.openclaw/workspace/data/skill-tests/[skill-id].test.yml`, run them:

### Test Case Format
```yaml
skill: code-review-router
tests:
  - name: "small frontend change"
    input:
      user_message: "review my code"
      context:
        files_changed: 2
        lines_changed: 30
        languages: ["tsx"]
        has_security: false
    expected:
      route: "opencode"
      should_not: "claude"

  - name: "large backend with auth"
    input:
      user_message: "审查代码"
      context:
        files_changed: 15
        lines_changed: 600
        languages: ["ts"]
        has_security: true
    expected:
      route: "claude"

  - name: "no changes"
    input:
      user_message: "review"
      context:
        files_changed: 0
    expected:
      action: "stop"
      message_contains: "Nothing to review"
```

### Test Execution
For each test case:
1. Mock the context (don't run real git commands)
2. Walk through the skill's decision logic
3. Verify the routing decision matches expected
4. Report pass/fail

### Test Output
```
## Test Results: code-review-router

✅ small frontend change — routed to opencode (expected: opencode)
✅ large backend with auth — routed to claude (expected: claude)
✅ no changes — stopped with message (expected: stop)

3/3 passed, 0 failed
```

## Step 4: Registry Integration Test

Verify the skill can be found by the router:

1. Temporarily register the skill
2. Test trigger keyword matching
3. Test semantic search matching
4. Verify category assignment

```
## Registry Test: [skill-name]

Trigger match:
  ✅ "review" → code-review-router (rank 1)
  ✅ "审查" → code-review-router (rank 1)
  ✅ "代码检查" → code-review-router (rank 1)

Category: code ✅
Agent compatibility: main, coder ✅
```

## Step 5: Final Report

```
## Skill Sandbox Report: [skill-name]

| Check | Status |
|-------|--------|
| Structure | ✅ PASS |
| Dependencies | ⚠️ 1 missing (optional) |
| Dry-run | ✅ PASS |
| Test cases | ✅ 3/3 passed |
| Registry | ✅ PASS |

**Verdict:** Ready to deploy ✅

Next steps:
- Run: python3 scripts/skill-register.py (to update registry)
```

## Auto-Trigger

When a new SKILL.md is created or modified in `~/.openclaw/workspace/skills/`:
1. Automatically run validation (Step 1)
2. If validation passes, suggest full sandbox test
3. If all tests pass, auto-register to registry
