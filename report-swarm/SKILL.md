---
name: report-swarm
description: >
  专业报告生成引擎。当用户要求「做一份报告」「写一份分析」「行业调研」、
  「竞品分析」「市场分析」等明确需要输出报告的任务时触发。
  基于 swarm-orchestrator 的统一编排能力，协调多个 agent 完成调研→分析→写作全流程。
  支持 CrewAI + ClawTeam 联合执行。生成结构化 Markdown 报告。
triggers:
  - 做一份
  - 写一份
  - 帮我调研
  - 写报告
  - 行业分析
  - 市场调研
  - 竞品分析
  - 研究报告
---

# Report Swarm — 专业报告生成引擎

## 定位

本 skill 是**报告生成的专业执行者**，基于 [swarm-orchestrator](../swarm-orchestrator/SKILL.md) 的编排能力。

用户说「做一份 XX 报告」时，激活本 skill：
1. 调用 swarm-orchestrator 决策执行路径
2. 执行报告生成 pipeline
3. 输出结构化 Markdown 报告

## 报告生成 Pipeline

### 自动路径选择

```
简单报告（用户未指定详情）→ 直接执行
行业/市场报告              → CrewAI + ClawTeam
竞品分析报告              → CrewAI + ClawTeam
调研报告                  → CrewAI Pipeline
```

### 报告结构模板

```markdown
# [主题] 报告

## 摘要（Executive Summary）
[200字以内核心发现]

## 背景与目标
[任务背景、研究目标]

## 市场/行业概况
[数据、规模、主要玩家]

## 竞品/用户分析
[对比数据、用户画像]

## 趋势与机会
[未来趋势、增长机会]

## 风险与挑战
[潜在风险、竞争威胁]

## 结论与建议
[可执行的具体建议]

## 参考资料
[数据来源]
```

## 报告类型适配

### 行业分析报告
- 市场规模、增长率、产业链
- 政策环境、技术趋势
- 主要玩家市场份额
- 投资机会与风险

### 市场调研报告
- 目标市场定义
- 用户画像与需求
- 竞争格局分析
- 营销策略建议

### 竞品分析报告
- 竞品列表与基本信息
- 功能对比矩阵
- 优劣势分析
- 差异化机会

## 输出格式

报告保存路径：
```
~/.openclaw/workspace/data/report-swarm/outputs/<run_id>/
├── manifest.json          # 执行概览
├── research/             # 研究阶段数据
│   └── data.json
├── analysis/             # 分析阶段输出
│   └── insights.json
├── report.md             # 最终报告
└── artifacts/            # 附件（图表、数据文件）
```

## 执行示例

```bash
# 完整报告生成
python3 ~/.openclaw/skills/report-swarm/scripts/run.py "做一份抖音电商行业分析报告"

# 指定子任务数
python3 ~/.openclaw/skills/report-swarm/scripts/run.py "做一份小红书竞品分析报告" --subtasks 5

# 只看执行计划
python3 ~/.openclaw/skills/report-swarm/scripts/run.py --decide "做一份微信视频号市场分析"
```

## 内部协作

本 skill 通过以下脚本与 swarm-orchestrator 协作：

| 脚本 | 职责 |
|------|------|
| `run.py` | CLI 入口，调度 orchestrator |
| `orchestrator.py` | 决策引擎（复杂度判断、路径选择） |
| `crewai_pipeline.py` | CrewAI 角色流水线 |
| `clawteam_pipeline.py` | ClawTeam 并行执行 |
| `memory_store.py` | 结果存储（cortex-memory + 本地文件） |
| `task_manager.py` | 任务状态追踪（fcntl 文件锁） |

## 依赖

- **swarm-orchestrator** — 编排引擎（自动调用）
- `clawteam` — `~/.openclaw/clawteam/`（并行多 agent）
- `crewai` — `pip install crewai`（角色流水线，可选）
- `cortex-memory` — `~/.openclaw/workspace/plugins/cortex-memory/`

## 注意事项

- 报告应包含具体数据和引用来源，避免空洞描述
- 复杂报告建议使用 `--subtasks 5` 指定 5 个子任务并行执行
- 最终报告自动写入 `report.md`，同时存入 cortex-memory 供复用
- 用户说「写一份报告」但任务简单 → 直接执行，不强制走多 agent 流程
