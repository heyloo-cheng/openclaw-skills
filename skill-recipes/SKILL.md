---
name: skill-recipes
description: Pre-defined and custom workflow recipes that chain multiple skills together. Use when you want to run a full workflow like "发版", "新功能", "修bug", or "重构".
triggers:
  - recipe
  - workflow
  - 发版
  - release
  - 新功能
  - new feature
  - 修bug
  - bugfix
  - 重构
  - refactor
  - 流程
  - pipeline
---

# Skill Recipes

Chain multiple skills into automated workflows.

## Built-in Recipes

### 🚀 Release (发版)
**Triggers:** "发版", "release", "上线", "发布"

Steps:
1. `test-generator-router` — 确保测试覆盖
2. `code-review-router` — 代码审查
3. `commit-message-router` — 生成 commit message
4. `deploy-reviewer` — 部署配置检查
5. `doc-generator-router` (changelog) — 生成 changelog

### ✨ New Feature (新功能)
**Triggers:** "新功能", "new feature", "开发新功能"

Steps:
1. `task-estimator` — 评估工作量
2. `coding-agent` — 开发实现
3. `test-generator-router` — 生成测试
4. `code-review-router` — 代码审查
5. `commit-message-router` — 提交代码

### 🐛 Bugfix (修 Bug)
**Triggers:** "修bug", "bugfix", "fix bug", "修复bug"

Steps:
1. `incident-router` — 定位问题
2. `coding-agent` — 修复代码
3. `test-generator-router` — 补充测试
4. `code-review-router` — 审查修复
5. `commit-message-router` — 提交

### 🔧 Refactor (重构)
**Triggers:** "重构", "refactor", "优化代码结构"

Steps:
1. `refactor-planner` — 分析和规划
2. `test-generator-router` — 确保测试覆盖
3. `coding-agent` — 执行重构
4. `code-review-router` — 审查重构
5. `commit-message-router` — 提交

### 📝 Documentation (文档)
**Triggers:** "写文档", "更新文档", "documentation"

Steps:
1. `doc-generator-router` — 生成文档
2. `translation-router` — 翻译（如需要）
3. `commit-message-router` — 提交

### 🔍 PR Review (PR 审查)
**Triggers:** "审查PR", "review PR", "PR流程"

Steps:
1. `pr-reviewer-router` — 完整 PR 审查
2. `test-generator-router` — 检查测试覆盖
3. `deploy-reviewer` — 检查部署影响（如有）

## Execution Mode

When a recipe is triggered, ask user:

```
🔄 启动 [Recipe Name] 流程

步骤:
1. [step 1] — [description]
2. [step 2] — [description]
...

执行模式:
- **自动** — 依次执行，每步输出摘要
- **确认** — 每步执行前确认
- **选择** — 选择要执行的步骤

选择模式 (默认: 确认):
```

## Step Execution

For each step:

1. Load the skill's SKILL.md
2. Execute according to skill instructions
3. Capture output summary
4. If step fails:
   - Report error
   - Ask: continue / retry / skip / abort
5. Pass relevant context to next step

## Progress Output

```
🔄 [Recipe Name] — Step [N/Total]

✅ Step 1: test-generator-router — 3 tests generated
▶️ Step 2: code-review-router — executing...
⏳ Step 3: commit-message-router — pending
⏳ Step 4: deploy-reviewer — pending
```

## Custom Recipes

Users can define custom recipes in `~/.openclaw/workspace/data/skill-recipes-custom.yaml`:

```yaml
my-workflow:
  name: "我的工作流"
  triggers: ["我的流程"]
  steps:
    - skill: code-review-router
    - skill: commit-message-router
```

Load custom recipes:
```bash
cat ~/.openclaw/workspace/data/skill-recipes-custom.yaml 2>/dev/null
```
