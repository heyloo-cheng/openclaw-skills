---
name: skill-router
description: Intelligently matches user intent to the best skill using keyword triggers, semantic search, and context awareness. Use this when unsure which skill to use, or say "帮我找skill" / "what skill should I use".
triggers:
  - skill
  - 找skill
  - 哪个skill
  - what skill
  - help me find
  - 推荐
  - recommend
---

# Skill Router

Matches user intent to the optimal skill(s) from the registry.

## When This Skill Activates

- User asks "which skill should I use?"
- User describes a task and no specific skill is obvious
- User says "帮我找skill" or "recommend a skill"

## Step 0: Load Registry

Read the skill registry:
```bash
cat ~/.openclaw/workspace/data/skill-registry.json
```

If registry is missing or outdated, regenerate:
```bash
python3 ~/.openclaw/workspace/scripts/skill-register.py
```

## Step 1: Collect Context (lightweight, < 100 tokens)

Gather environment info only if in a git repo:

```bash
# Quick environment snapshot
git rev-parse --git-dir 2>/dev/null && echo "GIT=true" || echo "GIT=false"
git branch --show-current 2>/dev/null
git diff --name-only HEAD 2>/dev/null | wc -l
git diff --name-only HEAD 2>/dev/null | head -5
ls Dockerfile docker-compose* 2>/dev/null && echo "DOCKER=true"
ls *.swift Package.swift project.yml 2>/dev/null && echo "SWIFT=true"
ls package.json 2>/dev/null && echo "NODE=true"
ls requirements.txt pyproject.toml 2>/dev/null && echo "PYTHON=true"
```

Build context summary:
```json
{
  "git": true/false,
  "dirty": true/false,
  "branch": "feature/xxx",
  "files_changed": N,
  "lang": "swift/ts/python/...",
  "has_docker": true/false,
  "current_agent": "main/coder/writer/..."
}
```

## Step 2: Match Intent

### Priority 1: Exact Trigger Match
Scan all skills' `triggers` array for exact keyword match with user input.
If one skill matches → high confidence (0.9+)

### Priority 2: Fuzzy Trigger Match
Partial match or synonym match on triggers.
If 1-3 skills match → medium confidence (0.6-0.8)

### Priority 3: Semantic Match
Compare user input against skill `description` + `triggers` + `examples`.
Use LanceDB vector search if available, otherwise text similarity.
Return top-3 candidates.

### Priority 4: Context Boost
Apply weights based on environment:

| Context | Boost Skills | Weight |
|---------|-------------|--------|
| git dirty (files changed) | code-review, commit-message, test-gen | +0.2 |
| On PR branch | pr-reviewer | +0.3 |
| Has Dockerfile | deploy-reviewer | +0.2 |
| Swift/iOS project | code-review (→ Claude Code) | +0.1 |
| Current agent = coder | code category skills | +0.2 |
| Current agent = writer | content category skills | +0.2 |
| Error/crash in input | incident-router | +0.3 |

### Agent Skill Profiles

| Agent | Preferred Categories | Excluded |
|-------|---------------------|----------|
| main | general, workflow | — |
| coder | code, test, deploy | weather, lifestyle |
| writer | content, translation | code, deploy |
| thinker | analysis, estimation | media, lifestyle |
| news | — | all custom skills |
| artist | media | code, ops |
| cursor-ops | code | content, lifestyle |

## Step 3: Output Recommendation

### High Confidence (> 0.8) — Single Match
```
🎯 推荐: **[skill name]**
[one-line description]

直接执行？(回复 "yes" 或 "y")
```

### Medium Confidence (0.5-0.8) — Top Match + Alternatives
```
🔍 最佳匹配: **[skill name]**
[description]

其他候选:
2. [skill 2] — [reason]
3. [skill 3] — [reason]

选择序号或描述更多需求。
```

### Low Confidence (< 0.5) — List Candidates
```
🤔 不太确定你需要哪个，这些可能相关:

1. [skill 1] — [description]
2. [skill 2] — [description]
3. [skill 3] — [description]

能再描述一下你想做什么吗？
```

## Step 3.5: Conversation Context (Memory Chain)

Before finalizing the match, check recent conversation (last 5 messages):

- If user just discussed a bug/error → boost incident-router
- If user just reviewed code → boost commit-message-router
- If user just estimated a task → boost coding-agent
- If user said "帮我处理一下" / "继续" / "接着做" → infer from previous topic

This allows vague follow-ups like "帮我处理" to resolve correctly without asking.

## Step 3.6: Progressive Trust (Auto-Execute)

Read `~/.openclaw/workspace/data/skill-usage-log.jsonl` for the matched skill:

- Count consecutive accepted executions (user_accepted=true, user_modified=false)
- If count >= 10 AND success_rate >= 90% → auto-execute without confirmation
- If count >= 5 AND success_rate >= 80% → show recommendation but auto-execute after 5s
- Otherwise → ask for confirmation as normal

Trust levels are per-skill, per-agent. Reset if user rejects or modifies output.

## Step 4: Execute Selected Skill

Once user confirms (or auto-execute triggers), load and follow the selected skill's SKILL.md.

## Step 5: Log Usage

After execution, record to skill usage log:
```json
{
  "skill_id": "[selected]",
  "timestamp": "[now]",
  "agent": "[current]",
  "match_type": "trigger|semantic|context",
  "confidence": 0.85,
  "user_accepted": true
}
```

Append to `~/.openclaw/workspace/data/skill-usage-log.jsonl`
