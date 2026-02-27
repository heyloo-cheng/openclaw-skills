---
name: skill-intelligence
description: Proactive skill recommendations, usage learning, and cross-agent collaboration. Runs during heartbeats or on-demand to suggest skills, track usage patterns, and optimize routing.
triggers:
  - skill推荐
  - 推荐skill
  - skill report
  - skill stats
  - 使用报告
  - skill usage
---

# Skill Intelligence

Proactive recommendations, self-evolution, and cross-agent awareness.

## Module A: Proactive Recommendations (Push Mode)

### Trigger Conditions

During heartbeat or conversation, detect these signals:

| Signal | Detection | Recommend |
|--------|-----------|-----------|
| git diff > 200 lines | `git diff --numstat HEAD \| awk '{s+=$1+$2}END{print s}'` | code-review-router |
| New API file, no test | New file in `api/`/`routes/`, no matching `*test*` | test-generator-router |
| commit msg < 10 chars | `git log -1 --format=%s \| wc -c` | commit-message-router |
| Dockerfile modified | `git diff --name-only HEAD \| grep -i docker` | deploy-reviewer |
| Same error 3+ times | Error pattern in recent conversation | incident-router |
| PR branch behind main 10+ | `git rev-list --count HEAD..main` | pr-reviewer-router |
| File > 300 lines edited | `wc -l` on changed files | refactor-planner |
| On PR branch | Branch name matches `pr/`, `feature/`, `fix/` | pr-reviewer-router |

### Heartbeat Integration

Add to HEARTBEAT.md check (lightweight, < 5 commands):

```bash
# Quick skill recommendation scan
cd <project-dir> 2>/dev/null || exit 0
DIRTY=$(git diff --numstat HEAD 2>/dev/null | awk '{s+=$1+$2}END{print s+0}')
BRANCH=$(git branch --show-current 2>/dev/null)
```

### Recommendation Format
```
💡 检测到 [signal description]
   建议使用: **[skill name]** — [one-line reason]
   (回复 "yes" 执行，或忽略)
```

### Frequency Control

Read/write `~/.openclaw/workspace/data/skill-recommendations.json`:
```json
{
  "last_recommendations": {
    "code-review-router": "2026-02-27T10:00:00Z",
    "test-generator-router": "2026-02-26T15:00:00Z"
  },
  "declined": {
    "deploy-reviewer": {"count": 3, "muted_until": "2026-03-06T00:00:00Z"}
  }
}
```

Rules:
- Same recommendation: max once per 24h
- User declines 3 times → mute that recommendation for 7 days
- Critical signals (security, crash) bypass frequency limits

---

## Module B: Self-Evolution (Feedback Learning)

### Usage Logging

After every skill execution, append to `~/.openclaw/workspace/data/skill-usage-log.jsonl`:

```json
{
  "skill_id": "code-review-router",
  "timestamp": "2026-02-27T15:30:00Z",
  "agent": "coder",
  "context": {"lang": "swift", "files": 5, "lines": 200},
  "routed_to": "claude",
  "match_type": "trigger",
  "confidence": 0.9,
  "execution_time_ms": 15000,
  "success": true,
  "user_accepted": true,
  "user_modified": false
}
```

### Learning Rules

Periodically analyze usage log (weekly or on-demand):

1. **Route Threshold Adjustment**
   - Count user's tool preference at each complexity level
   - If user manually switches tool > 50% of time at threshold → adjust

2. **Success Rate Tracking**
   - Per-skill success rate from usage log
   - < 70% success → flag for review
   - 3 consecutive failures → auto-switch to fallback

3. **Preference Learning**
   - Track which skills user uses most per context
   - Build per-user weight adjustments
   - Store in `skill-registry.json` (update `use_count`, `success_rate`)

### Monthly Report

Generate on-demand with `/skill stats` or `skill report`:

```
## Skill 使用报告 (2026-02)

📊 总执行次数: 87

🏆 最常用:
1. code-review-router — 23次 (成功率 91%)
2. commit-message-router — 18次 (成功率 95%)
3. test-generator-router — 12次 (成功率 83%)

⚠️ 需要优化:
- incident-router — 成功率 60% (5/8次失败)

💤 未使用:
- deploy-reviewer, translation-router, task-estimator

📈 趋势:
- code-review 使用量 +30% vs 上月
- 用户偏好 Claude Code 处理 Swift 项目 (8/10次)

💡 建议:
- incident-router 成功率低，考虑优化 prompt
- deploy-reviewer 从未使用，是否需要保留？
```

---

## Module C: Cross-Agent Collaboration

### Agent Skill Profiles

Read from `~/.openclaw/workspace/data/skill-agent-profiles.json`:

```json
{
  "main": {
    "preferred": ["general", "workflow", "lifestyle", "productivity"],
    "boost": {},
    "exclude": []
  },
  "coder": {
    "preferred": ["code", "ops"],
    "boost": {"code-review-router": 0.3, "test-generator-router": 0.3},
    "exclude": ["weather", "spotify-player", "openhue"]
  },
  "writer": {
    "preferred": ["content"],
    "boost": {"doc-generator-router": 0.3, "translation-router": 0.3},
    "exclude": ["code-review-router", "deploy-reviewer", "incident-router"]
  },
  "thinker": {
    "preferred": ["general", "code"],
    "boost": {"task-estimator": 0.3, "refactor-planner": 0.2},
    "exclude": ["media", "lifestyle"]
  },
  "news": {
    "preferred": [],
    "exclude": ["*"]
  },
  "artist": {
    "preferred": ["media"],
    "exclude": ["code", "ops"]
  },
  "cursor-ops": {
    "preferred": ["code"],
    "boost": {"cursor-agent": 0.5},
    "exclude": ["content", "lifestyle"]
  }
}
```

### Routing with Agent Awareness

When skill-router runs:
1. Detect current agent from runtime context
2. Load agent profile
3. Apply boosts to preferred category skills
4. Filter out excluded skills
5. If best match is excluded → suggest delegating to appropriate agent

### Cross-Agent Delegation

```
🔄 当前 agent (writer) 不适合执行 code-review-router
   建议转给 coder agent 处理？(回复 "yes" 转发)
```

### Shared Learning

All agents write to the same `skill-usage-log.jsonl`.
Learning insights are shared — if coder learns that Swift projects prefer Claude Code, thinker also knows this when estimating Swift tasks.

### Auto-Delegation Learning

Track cross-agent delegation patterns in `skill-usage-log.jsonl`:

```json
{
  "type": "delegation",
  "from_agent": "writer",
  "to_agent": "coder",
  "skill_category": "code",
  "timestamp": "2026-02-27T15:00:00Z",
  "user_approved": true
}
```

Rules:
- Same delegation pattern 3+ times with user approval → auto-delegate next time
- Store learned rules in `~/.openclaw/workspace/data/skill-auto-delegations.json`:
```json
{
  "writer→coder": {"categories": ["code", "ops"], "auto": true, "count": 5},
  "main→coder": {"categories": ["code"], "auto": false, "count": 2}
}
```
- Auto-delegation message: "🔄 自动转给 [agent] 处理（基于历史偏好）"

---

## Module D: Monthly Report (Cron)

### Setup

Create cron job for monthly report (每月 1 号 9:00):

```bash
openclaw cron create --schedule "0 9 1 * *" --agent main --prompt "生成 skill 月度使用报告并发送到飞书主 Agent 私聊"
```

### Report Generation

Read `skill-usage-log.jsonl`, aggregate by month:

1. Total executions
2. Top 5 most used skills
3. Per-skill success rate
4. Unused skills list
5. Trend vs last month
6. Auto-trust upgrades (skills that earned auto-execute)
7. Delegation patterns

### Delivery

Send report to Feishu main agent DM (not group):
```
message tool:
  channel: feishu
  accountId: main
  target: <user's feishu open_id>
  message: <formatted report>
```

User's Feishu open_id: `ou_8067c16c778766946f5ccea50b3af738`
