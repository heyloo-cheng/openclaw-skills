---
name: model-router
description: Automatically routes requests to the optimal model (haiku/sonnet/opus) based on task complexity. Saves 60-70% cost by using cheaper models for simple tasks.
triggers:
  - model
  - 模型选择
  - 省钱
  - save cost
  - haiku
  - sonnet
  - opus
  - 模型路由
---

# Model Router

Routes requests to the cheapest model that can handle the task well.

## Model Tiers

| Tier | Model | Cost | Use For |
|------|-------|------|---------|
| L0 | claude-haiku | $$ | 简单问答、翻译、格式化、天气、提醒 |
| L1 | claude-sonnet | $$$ | 代码生成、文档写作、中等分析、skill执行 |
| L2 | claude-opus | $$$$ | 复杂推理、架构设计、多步规划、创意任务 |

## Complexity Detection

### L0 Signals (→ haiku)
- 消息长度 < 50 字符
- 纯问答（"什么是X"、"X是什么意思"）
- 翻译请求
- 天气/时间/日期查询
- 简单格式转换
- 状态查询（"查看邮件"、"日历"）
- 单工具调用（weather、email check）
- 闲聊、打招呼

### L1 Signals (→ sonnet)
- 代码生成/修改（单文件）
- 文档写作
- Skill 执行（大部分 router skills）
- 数据分析（中等复杂度）
- 多步骤但有明确流程的任务
- Bug 修复（已定位的）

### L2 Signals (→ opus)
- 多文件代码架构
- 复杂调试（未定位的）
- 创意/头脑风暴
- 长文分析/总结
- 多 agent 协调
- 需要深度推理的任务
- 用户明确要求高质量

## Routing Logic

```
1. 检查用户是否指定了模型 → 用指定的
2. 检查是否在特定 agent 上下文:
   - news agent → 始终 haiku
   - artist agent → 始终 gemini
   - 其他 → 继续判断
3. 关键词快速匹配:
   - 天气/时间/翻译/查邮件 → L0
   - review/test/commit/deploy → L1
   - 架构/设计/分析/头脑风暴 → L2
4. 消息长度:
   - < 20 字符 → L0
   - 20-200 字符 → L1 (default)
   - > 200 字符 → L2
5. 上下文复杂度:
   - 涉及多文件/多 skill → L2
   - 单一明确任务 → L1
   - 信息查询 → L0
6. 历史学习:
   - 查 skill-usage-log，同类任务上次用什么模型成功了
   - 用户手动切换过模型 → 记住偏好
```

## Override

用户可以随时覆盖:
- "用 opus 回答" → 强制 L2
- "简单回答就行" → 强制 L0
- `/model haiku` → 切换当前会话模型

## Usage Tracking

每次路由记录到 `skill-usage-log.jsonl`:
```json
{
  "type": "model_route",
  "input_length": 45,
  "complexity": "L0",
  "model": "claude-haiku",
  "agent": "main",
  "timestamp": "...",
  "user_override": false
}
```

## Cost Estimation

假设当前 100% opus 使用:
- 切换后预估: 50% haiku + 35% sonnet + 15% opus
- haiku 价格约 opus 的 1/20
- sonnet 价格约 opus 的 1/5
- 综合节省: ~65%
