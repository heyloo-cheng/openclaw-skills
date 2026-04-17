---
name: swarm-orchestrator
description: >
  统一任务编排引擎。当用户描述需要调研、分析、写作的任务，
  或明确要求使用 "CrewAI"、"ClawTeam"、"多 agent"、"子任务"、"并行执行" 时触发。
  自动判断复杂度：简单任务直接执行，中等任务用 CrewAI pipeline，
  复杂任务用 CrewAI + ClawTeam 联合编排。
  支持用户直接指定执行模式（crewai / clawteam / crewai+clawteam / 3个子任务）。
  关键词：crewai、clawteam、多 agent、并行、子任务、调研、报告、分析、市场、竞品。
---

# Swarm Orchestrator — 统一任务编排引擎

## 核心定位

本 skill 是 OpenClaw 的**统一执行入口**，职责：
1. 理解用户意图和指定模式
2. 判断任务复杂度
3. 选择最合适的执行路径
4. 协调 CrewAI / ClawTeam / 直接执行

## 执行决策树

```
用户输入
    │
    ├─ 用户指定了模式？
    │    ├─ "clawteam"           → ClawTeam（并行多 agent，tmux 隔离）
    │    ├─ "crewai"             → CrewAI（角色流水线，可追加 ClawTeam）
    │    ├─ "crewai+clawteam"    → 两个都用（编排层 + 执行层）
    │    └─ "N 个子任务"          → 按 N 个并行子任务执行
    │
    └─ 用户没有指定 → OpenClaw 自动判断复杂度
         │
         ├─ 简单（子目标 ≤ 2）  → 直接执行
         ├─ 中等（3-5 个子目标）→ CrewAI pipeline
         └─ 复杂（6+ 个子目标） → CrewAI + ClawTeam
```

## 升级规则

系统只能**往上加**，不能**往下减**：

| 用户选 | 系统判断需要 | 最终执行 |
|--------|------------|---------|
| CrewAI | ClawTeam 有帮助 | CrewAI + ClawTeam |
| ClawTeam | CrewAI 有帮助 | CrewAI + ClawTeam |
| 直接执行 | 需要多 agent | 升级为 CrewAI |

## 复杂度判断标准

| 级别 | 标准 | 执行 |
|------|------|------|
| 简单 | 子目标 ≤ 2，1 个领域，无实时数据 | 直接执行 |
| 中等 | 子目标 3-5，2-3 个领域，结构化输出 | CrewAI |
| 复杂 | 子目标 ≥ 6，多领域，有依赖关系，需要并行 | CrewAI + ClawTeam |

**复杂度关键词**（自动累加）：
- 降分：告诉我、查一下、翻译、改写、润色、总结
- 加分：分析、调研、报告、对比、行业、市场、竞品、全面、深度
- 大量加分：多维度、多角度、系统化、战略、架构、生态

## 用户指定模式

识别以下关键词：

```
clawteam / claw-team / claw team → 强制 ClawTeam
crewai / crew-ai / crew ai     → 强制 CrewAI（可追加 ClawTeam）
crewai+clawteam / 全开          → 两个都用
auto / 自动 / 默认              → 系统自动判断
直接 / 简单 / 快速              → 直接执行
N 个子任务 / N 步 / 分 N 步      → N 个并行子任务
```

## Pipeline 详解

### Pipeline A: 直接执行

简单任务，直接用 OpenClaw 主 agent 完成。

```bash
openclaw agent -m "任务描述" --thinking medium
```

### Pipeline B: CrewAI Pipeline

中等复杂度任务。角色流水线：

| Agent | 职责 | OpenClaw 角色 |
|-------|------|--------------|
| Researcher | 收集数据、爬取信息 | main |
| Analyst | 分析数据、提炼洞察 | thinker |
| Writer | 撰写报告、格式化输出 | writer |

**推荐子任务数**：
- 3 个子目标 → Researcher + Writer
- 4-5 个子目标 → Researcher + Analyst + Writer
- 6+ 个子目标 → 建议升级到 CrewAI + ClawTeam

### Pipeline C: ClawTeam Pipeline

并行多 agent 执行。用于用户明确指定或任务可自然拆分。

```bash
# 1. 创建团队
clawteam team spawn-team my-team -d "任务描述" -n leader

# 2. 创建任务
clawteam task create my-team "子任务1" -o worker-1
clawteam task create my-team "子任务2" -o worker-2
clawteam task create my-team "子任务3" -o worker-3

# 3. Spawn workers（每个 worker 有自己的 tmux 窗口 + git worktree）
clawteam spawn -t my-team -n worker-1 --task "任务1描述"
clawteam spawn -t my-team -n worker-2 --task "任务2描述"
clawteam spawn -t my-team -n worker-3 --task "任务3描述"

# 4. 监控进度
clawteam board show my-team
clawteam board live my-team --interval 5

# 5. 收集结果
clawteam inbox receive my-team

# 6. 清理
clawteam team cleanup my-team --force
```

**ClawTeam 关键特性**：
- 每个 worker 在独立的 tmux 窗口中运行
- 通过 `clawteam inbox` 在 workers 之间传递消息
- 任务依赖链：`--blocked-by <task_id>` 自动解锁
- Web 看板：`clawteam board serve --port 8080`

### Pipeline D: CrewAI + ClawTeam 联合编排

复杂任务。CrewAI 做**编排层**，ClawTeam 做**执行层**：

```
CrewAI Orchestrator（OpenClaw leader）
  ├─ 解析任务 → 拆分为子任务
  ├─ 派发给 ClawTeam → clawteam spawn team + spawn workers
  ├─ 监控进度   → clawteam board / task wait
  └─ 汇总结果   → 写入 cortex-memory

ClawTeam 执行层
  ├─ spawn researcher-worker  → 真正执行研究
  ├─ spawn analyst-worker      → 真正执行分析
  ├─ spawn writer-worker       → 真正执行写作
  └─ 通过 inbox 消息传递中间结果
```

**典型 5-agent 团队**：
```
leader（OpenClaw 主 agent）
  ├─ researcher-1 → 并行研究 A
  ├─ researcher-2 → 并行研究 B
  ├─ analyst → 分析整合
  └─ writer → 撰写报告
```

## 执行流程（完整版）

### Step 1: 解析用户输入

从输入中提取：
- **任务目标**：核心任务
- **指定模式**：用户是否明确指定执行方式
- **子任务数**：用户指定的数量（如"3 个子任务"）

### Step 2: 决策执行路径

根据决策树选择执行模式。

### Step 3: 运行 Pipeline

```bash
# 自动模式（系统判断复杂度）
python3 ~/.openclaw/skills/report-swarm/scripts/run.py "做一份抖音市场分析报告"

# 强制 CrewAI
python3 ~/.openclaw/skills/report-swarm/scripts/run.py "做一份抖音市场分析报告" --mode crewai

# 强制 ClawTeam
python3 ~/.openclaw/skills/report-swarm/scripts/run.py "做一份抖音市场分析报告" --mode clawteam

# 强制两个都用
python3 ~/.openclaw/skills/report-swarm/scripts/run.py "做一份抖音市场分析报告" --mode crewai+clawteam

# 指定子任务数
python3 ~/.openclaw/skills/report-swarm/scripts/run.py "做一份抖音市场分析报告" --subtasks 5

# 只输出执行决策，不执行
python3 ~/.openclaw/skills/report-swarm/scripts/run.py --decide "做一份抖音市场分析报告"
```

### Step 4: 汇总输出

- 所有 pipeline 中间结果写入 `~/.openclaw/workspace/data/report-swarm/outputs/<run_id>/`
- 最终报告写入 `report.md`
- 返回简洁摘要给用户

## 依赖

- `clawteam` — 位于 `~/.openclaw/clawteam/`（已集成）
- `crewai` — pip install crewai（可选，不影响 ClawTeam）
- `cortex-memory` — 结果存储（`~/.openclaw/workspace/plugins/cortex-memory/`）

## 注意事项

- ClawTeam 数据目录：`~/.clawteam/`
- ClawTeam spawn 的 agent 默认使用 `openclaw`（OpenClaw 是 ClawTeam 的默认 agent）
- 所有 pipeline 结果最终写入 cortex-memory，供后续任务复用
- 用户说 "CrewAI" 但任务太复杂 → 自动追加 ClawTeam
- **ClawTeam 已在 OpenClaw 内置**，无需额外安装
