---
name: openspec-router
description: Spec-driven development router. Detects feature/refactor/fix requests and auto-triggers OpenSpec propose→apply→archive workflow with model-aware routing.
version: "1.0"
triggers:
  - openspec
  - spec driven
  - 加功能
  - 新功能
  - 重构
  - 我要做
  - 我想加
  - feature request
  - add feature
  - refactor
  - new feature
  - propose change
  - spec first
examples:
  - "我要给 ToolBox 加个暗黑模式"
  - "帮我重构用户认证模块"
  - "I want to add a new feature"
  - "propose a change for the login flow"
---

# OpenSpec Router

Spec-driven development 自动路由。检测到功能/重构/修复请求时，自动触发 OpenSpec 工作流。

## 前置条件

- 目标项目已运行 `openspec init --tools claude,cursor,opencode`
- OpenSpec CLI 已安装 (`npm install -g @fission-ai/openspec@latest`)

## 路由策略（模型分级）

| 阶段 | 动作 | 模型 | Agent | 原因 |
|------|------|------|-------|------|
| Propose | 生成 proposal + design + specs + tasks | opus | thinker | 需要深度思考、架构设计 |
| Apply | 按 tasks 逐步实现代码 | sonnet | coder | 执行代码，sonnet 足够 |
| Archive | 归档完成的变更 | haiku | main | 简单操作 |

## 触发条件

当用户消息匹配以下模式时自动触发：

1. 明确提到"加功能/新功能/重构/改造"
2. 描述了一个需要多步实现的变更
3. 用户说"spec first"或"先写 spec"
4. 用户直接说 `/opsx:propose`

**不触发的情况：**
- 简单 bug fix（< 20 行改动）
- 配置修改
- 文档更新
- 用户明确说"直接改"

## 工作流

### Phase 1: Propose（thinker agent, opus）

```
1. 确认目标项目路径
2. 检查项目是否已 openspec init，没有则先初始化
3. 委派给 thinker agent:
   sessions_send(sessionKey="agent:thinker:main", message="""
   [任务] OpenSpec Propose
   [背景] 用户想要: {用户描述}
   [项目] {项目路径}
   [要求] 运行以下流程:
   1. cd {项目路径}
   2. openspec new change "{change-name}"
   3. 读取 openspec status --change "{change-name}" --json
   4. 按依赖顺序生成所有 artifacts (proposal.md, design.md, specs/, tasks.md)
   5. 每个 artifact 用 openspec instructions {artifact-id} --change "{change-name}" --json 获取模板
   6. 完成后运行 openspec status --change "{change-name}" 确认
   """)
4. 回复用户: "已转给 thinker 做 spec 设计 ✅ 完成后会通知你"
```

### Phase 2: Apply（coder agent, sonnet）

```
1. thinker 完成 propose 后，读取生成的 tasks.md
2. 委派给 coder agent:
   sessions_send(sessionKey="agent:coder:main", message="""
   [任务] OpenSpec Apply
   [背景] thinker 已完成 spec，现在按 tasks 实现代码
   [项目] {项目路径}
   [Spec文件] openspec/changes/{change-name}/
   [要求] 运行以下流程:
   1. cd {项目路径}
   2. 读取 openspec/changes/{change-name}/ 下所有 artifact
   3. openspec instructions apply --change "{change-name}" --json
   4. 按 tasks.md 逐步实现，每完成一个 task 标记完成
   5. 完成后运行 openspec status --change "{change-name}" 确认
   """)
3. 回复用户: "Spec 已就绪，已转给 coder 实现代码 ✅"
```

### Phase 3: Archive（main agent, haiku）

```
1. coder 完成 apply 后
2. main 自己执行:
   cd {项目路径}
   openspec archive "{change-name}"
3. 回复用户: "变更已归档 ✅ openspec/changes/archive/{date}-{change-name}/"
```

## 快速参考

```bash
# 检查项目是否已初始化
ls openspec/ 2>/dev/null

# 初始化（首次）
openspec init --tools claude,cursor,opencode

# 查看当前变更
openspec list

# 查看变更状态
openspec status --change "change-name"

# 归档
openspec archive "change-name"
```

## 与现有系统集成

- **model-classify.mjs**: propose=L2(opus), apply=L1(sonnet), archive=L0(haiku)
- **auto-delegation**: 自动走 thinker→coder→main 三段式
- **skill-usage-log**: 记录每次 propose/apply/archive 的耗时和 token
- **semantic-cache**: 缓存相似 propose 的 design 模式，加速后续类似变更
