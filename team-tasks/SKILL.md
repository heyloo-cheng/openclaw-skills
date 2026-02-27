---
name: team-tasks
description: "Coordinate multi-agent development pipelines using shared JSON task files. Use when dispatching work across agents (coder, cursor-ops, writer, thinker), tracking pipeline progress, or running sequential/parallel/debate workflows. Supports three modes: linear (sequential), dag (dependency graph with parallel), debate (multi-agent deliberation)."
---

# Team Tasks — 多Agent协作流水线

## 概述

通过共享 JSON 任务文件协调多个 agent 协作开发。
AGI（调度者）是指挥中心 — agent 之间不直接通信。

**三种模式：**
- **Linear:** 顺序流水线 `coder → cursor-ops → writer → thinker`
- **DAG:** 依赖图，满足依赖即可并行调度
- **Debate:** 多agent辩论，收集观点 + 交叉评审 + 综合

## Agent 角色映射

| 角色 | Agent | 模型 | 职责 |
|------|-------|------|------|
| code-agent | coder | sonnet-4-6 | 写代码、实现功能 |
| test-agent | cursor-ops | sonnet-4-6 | 写测试、跑测试（Cursor驱动）|
| docs-agent | writer | sonnet-4-6 | 写文档 |
| monitor-bot | thinker | opus-4-6 | 代码审查、安全审计 |

## Session Keys（飞书群）

| Agent | Session Key |
|-------|-------------|
| coder | `agent:coder:feishu:group:oc_47d44e808dc7e606d91eb7bbc2d55c5b` |
| cursor-ops | `agent:cursor-ops:feishu:group:oc_bfd2a380d61ed86a1d8ca527ec11c504` |
| writer | `agent:writer:feishu:group:oc_36f55d29c8e6bd1851f5fb45d0da387e` |
| thinker | `agent:thinker:feishu:group:oc_604277f122e839870b6f1d0806d8f72f` |

## CLI 命令

所有命令: `python3 <skill-dir>/scripts/task_manager.py <command> [args]`

其中 `<skill-dir>` 是本 SKILL.md 所在目录。

### 快速参考

| 命令 | 模式 | 用法 | 说明 |
|------|------|------|------|
| `init` | 全部 | `init <project> -g "目标" [-m linear\|dag\|debate]` | 创建项目 |
| `add` | dag | `add <project> <task-id> -a <agent> -d <deps>` | 添加任务 |
| `add-debater` | debate | `add-debater <project> <agent> [-r "角色"]` | 添加辩论者 |
| `round` | debate | `round <project> start\|collect\|cross-review\|synthesize` | 辩论操作 |
| `status` | 全部 | `status <project> [--json]` | 查看进度 |
| `assign` | linear/dag | `assign <project> <task> "描述"` | 设置任务描述 |
| `update` | linear/dag | `update <project> <task> <status>` | 更新状态 |
| `next` | linear | `next <project> [--json]` | 获取下一阶段 |
| `ready` | dag | `ready <project> [--json]` | 获取可调度任务 |
| `graph` | dag | `graph <project>` | 显示依赖树 |
| `result` | linear/dag | `result <project> <task> "输出"` | 保存结果 |
| `reset` | linear/dag | `reset <project> [task] [--all]` | 重置状态 |
| `list` | 全部 | `list` | 列出所有项目 |

## Mode A: Linear（顺序流水线）

### 初始化

```bash
python3 scripts/task_manager.py init my-api -g "构建REST API" \
  -p "coder,cursor-ops,writer,thinker"
```

默认流水线: `coder → cursor-ops → writer → thinker`

### 分配任务

```bash
python3 scripts/task_manager.py assign my-api coder "用Flask实现REST API"
python3 scripts/task_manager.py assign my-api cursor-ops "写pytest测试，覆盖率90%+"
python3 scripts/task_manager.py assign my-api writer "写README文档"
python3 scripts/task_manager.py assign my-api thinker "安全审计和代码审查"
```

### 调度循环

```
1. next <project> --json           → 获取下一阶段
2. update <project> <agent> in-progress
3. sessions_send(sessionKey, task)  → 派发给agent
4. 等待agent回复
5. result <project> <agent> "..."   → 保存结果
6. update <project> <agent> done    → 自动推进到下一阶段
7. 重复
```

## Mode B: DAG（依赖图）

### 初始化

```bash
python3 scripts/task_manager.py init my-feature -m dag -g "构建搜索功能"
```

### 添加任务

```bash
TM="python3 scripts/task_manager.py"
$TM add my-feature design     -a writer     --desc "写API规格"
$TM add my-feature scaffold   -a coder      --desc "创建项目骨架"
$TM add my-feature implement  -a coder      -d "design,scaffold" --desc "实现API"
$TM add my-feature write-tests -a cursor-ops -d "design"          --desc "写测试用例"
$TM add my-feature run-tests  -a cursor-ops  -d "implement,write-tests" --desc "跑测试"
$TM add my-feature review     -a thinker     -d "run-tests"       --desc "代码审查"
```

### 调度循环

```
1. ready <project> --json          → 获取所有可调度任务
2. 对每个ready任务（可并行）:
   a. update <project> <task> in-progress
   b. sessions_send(agent, task + depOutputs)
3. agent回复后: result → update done → 检查新解锁的任务
4. 重复直到全部完成
```

## Mode C: Debate（多Agent辩论）

### 流程

```bash
TM="python3 scripts/task_manager.py"

# 1. 创建辩论项目
$TM init security-review --mode debate -g "审查auth模块安全性"

# 2. 添加辩论者
$TM add-debater security-review coder     --role "安全专家"
$TM add-debater security-review thinker   --role "架构分析师"
$TM add-debater security-review cursor-ops --role "测试工程师"

# 3. 开始第一轮
$TM round security-review start

# 4. 收集各方观点
$TM round security-review collect coder "发现SQL注入漏洞"
$TM round security-review collect thinker "缺少输入验证"
$TM round security-review collect cursor-ops "没有速率限制"

# 5. 交叉评审
$TM round security-review cross-review

# 6. 收集评审意见
$TM round security-review collect coder "同意速率限制很关键"
$TM round security-review collect thinker "SQL注入最严重"
$TM round security-review collect cursor-ops "建议加WAF"

# 7. 综合
$TM round security-review synthesize
```

## 数据存储

任务文件: `~/.openclaw/workspace/data/team-tasks/<project>.json`

## ⚠️ 注意事项

- Linear模式: stage ID 是 agent 名称（如 `coder`），不是数字
- DAG模式: 依赖必须先添加再引用
- Debate模式: 开始round后不能再添加辩论者
- 保存结果(`result`)要在标记完成(`update done`)之前
