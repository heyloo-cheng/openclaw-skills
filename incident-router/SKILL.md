---
name: incident-router
description: Routes incident troubleshooting based on error log characteristics. Use when diagnosing errors, crashes, or system issues from logs.
triggers:
  - incident
  - 故障
  - 排查
  - error
  - 报错
  - 崩溃
  - crash
  - debug
  - 排错
---

# Incident Router

Analyzes error patterns and routes to the appropriate troubleshooting strategy.

## When NOT to Use This Skill

- For code review (use code-review-router)
- For planned debugging (use refactor-planner)
- When the issue is already identified and just needs fixing

## Step 1: Collect Error Context

Ask user for or detect:
```bash
# Recent error logs
tail -100 /var/log/syslog 2>/dev/null || journalctl -n 100 2>/dev/null
# App logs
find . -name "*.log" -mmin -30 -exec tail -50 {} \;
# Process status
ps aux | head -20
# Disk/memory
df -h; free -h 2>/dev/null || vm_stat
```

## Step 2: Classify Error Pattern

| Pattern | Category | Priority |
|---------|----------|----------|
| `OOM`, `killed`, `memory` | Memory | P1 |
| `ECONNREFUSED`, `timeout`, `DNS` | Network | P1 |
| `permission denied`, `EACCES`, `403` | Permission | P2 |
| `disk full`, `no space`, `ENOSPC` | Disk | P1 |
| `segfault`, `SIGSEGV`, `crash` | Crash | P1 |
| `deadlock`, `lock wait timeout` | Database | P1 |
| `connection pool exhausted` | Database | P2 |
| `rate limit`, `429`, `throttle` | Rate Limit | P2 |
| `SSL`, `certificate`, `TLS` | Certificate | P2 |
| `syntax error`, `undefined`, `null` | Code Bug | P3 |

## Step 3: Route Troubleshooting

### Memory Issues
```bash
# Gather diagnostics
ps aux --sort=-%mem | head -10
cat /proc/meminfo 2>/dev/null || vm_stat
```
→ Claude Code for deep analysis of memory leaks

### Network Issues
```bash
# Quick diagnostics
ping -c 3 <target>; curl -v <endpoint> 2>&1 | head -30
netstat -tlnp 2>/dev/null || lsof -i -P | grep LISTEN
```
→ OpenCode for quick connectivity checks

### Database Issues
```bash
# Connection and lock status
# Varies by DB engine
```
→ Claude Code for query analysis and lock debugging

### Permission Issues
```bash
ls -la <path>; id; groups
```
→ OpenCode for quick permission fixes

### Crash/Segfault
```bash
# Core dump analysis, stack trace
dmesg | tail -20
```
→ Claude Code for crash analysis

## Step 4: Output

```
## Incident Analysis

**Category:** [Memory/Network/DB/Permission/Crash]
**Priority:** [P1/P2/P3]
**Pattern:** [detected error pattern]

**Diagnostics:**
[gathered info]

**Root Cause:** [analysis]
**Fix:** [recommended action]
**Prevention:** [how to avoid recurrence]
```
