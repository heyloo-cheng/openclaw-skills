---
name: pr-reviewer-router
description: Comprehensive PR review including code quality, PR description, breaking changes, and linked issues. Use when reviewing a pull request.
triggers:
  - PR
  - pull request
  - 合并请求
  - PR review
  - merge request
  - 审查PR
---

# PR Reviewer Router

Full pull request review — code + process + risk assessment.

## When NOT to Use This Skill

- For reviewing uncommitted local changes (use code-review-router)
- For draft PRs that aren't ready for review
- For documentation-only PRs (just skim)

## Step 0: Get PR Context

```bash
# Current branch info
git branch --show-current
git log --oneline main..HEAD 2>/dev/null || git log --oneline master..HEAD

# Diff against base
git --no-pager diff main..HEAD --stat 2>/dev/null || git --no-pager diff master..HEAD --stat
git --no-pager diff main..HEAD --numstat 2>/dev/null || git --no-pager diff master..HEAD --numstat
```

## Step 1: PR Description Quality

Check if PR has:
- [ ] Clear title (what, not how)
- [ ] Description of changes (why)
- [ ] Testing instructions
- [ ] Screenshots (if UI changes)
- [ ] Linked issues/tickets

## Step 2: Breaking Change Detection

Scan for:

| Pattern | Risk |
|---------|------|
| Public API signature changed | Breaking |
| Database schema migration | Breaking |
| Config format changed | Breaking |
| Dependency major version bump | Breaking |
| Removed exports/endpoints | Breaking |
| Changed default values | Potentially breaking |
| New required environment variables | Breaking |

## Step 3: Route Review Depth

### Quick Review (< 5 files, < 100 lines, no breaking changes)
```bash
opencode run "Review this PR (branch: $(git branch --show-current)). Check: code quality, naming, edge cases. Be concise."
```

### Standard Review (5-15 files, 100-500 lines)
```bash
git --no-pager diff main..HEAD | claude -p "Review this PR diff for: 1) Code quality, 2) Potential bugs, 3) Security issues, 4) Test coverage gaps, 5) Breaking changes. Provide actionable feedback organized by file."
```

### Deep Review (> 15 files OR > 500 lines OR breaking changes)
```bash
git --no-pager diff main..HEAD | claude -p "Deep review this large PR: 1) Architecture impact, 2) Breaking changes and migration path, 3) Security vulnerabilities, 4) Performance implications, 5) Test adequacy, 6) Rollback safety. Group findings by severity (critical/warning/suggestion)."
```

## Step 4: Output

```
## PR Review

**Branch:** [branch name]
**Size:** [files] files, [lines] lines
**Review depth:** [Quick/Standard/Deep]
**Breaking changes:** [Yes/No — list if yes]

### Summary
[1-2 sentence overall assessment]

### Findings
**Critical:** [must fix before merge]
**Warnings:** [should fix]
**Suggestions:** [nice to have]

### Verdict
[APPROVE / REQUEST_CHANGES / NEEDS_DISCUSSION]
```
