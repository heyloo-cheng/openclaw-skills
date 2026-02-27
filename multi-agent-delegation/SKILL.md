---
name: multi-agent-delegation
description: Cross-agent delegation framework for OpenClaw multi-agent setups. Main agent acts as router, delegates to specialized agents (coder/writer/thinker/artist) with context passing and result forwarding.
version: "1.0"
triggers:
  - 委派
  - delegation
  - multi agent
  - 多agent
  - 跨agent
  - auto delegate
  - 自动分发
  - agent routing
  - thinker coder writer
examples:
  - "把这个代码任务委派给 coder"
  - "delegate this writing task"
  - "自动分发任务给合适的 agent"
---

# Multi-Agent Delegation Framework

Main agent (opus) 做调度，不做执行。收到任务后判断类型，委派给专业 agent。

## 路由表

| 任务类型 | 目标 Agent | 模型 | Session Key |
|---------|-----------|------|-------------|
| 新功能/重构 | thinker→coder | opus→sonnet | OpenSpec 三段式 |
| 写代码/review | coder | sonnet | agent:coder:main |
| 写文档/翻译 | writer | sonnet | agent:writer:main |
| 生成图片 | artist | gemini | agent:artist:main |
| Cursor 任务 | cursor-ops | sonnet | agent:cursor-ops:main |
| 深度分析 | thinker | opus | agent:thinker:main |

## 委派消息格式

```
[任务] 具体要做什么
[背景] 用户之前聊了什么（2-3句话概括）
[文件] 相关文件路径
[要求] 用户的特殊要求
```

## 防坑规则

1. **延迟防护**: < 200 token 输出的任务不委派，main 自己做
2. **上下文传递**: 必须附带 [任务][背景][文件][要求] 四要素
3. **数据一致性**: skill-watcher 自动同步，cache 30 天过期
4. **回复路由**: 委派完成后 main 转发结果摘要(< 200 token)回原对话
5. **质量保障**: 30 秒超时→main 自己做，连续 3 次失败→暂停委派

## 委派流程

```
1. sessions_send(sessionKey="agent:[id]:main", message="[任务]...")
2. 回复用户："已转给 [agent] 处理 ✅"
3. 监听完成（sessions_history 或 subagents list）
4. 读取结果，生成摘要 < 200 token
5. 发送摘要到原对话
```

## Main 自己处理

- 闲聊、打招呼、简短问答
- 任务分发和协调
- 记忆管理（MEMORY.md、daily log）
- 系统管理（openclaw 配置、插件）
- 用户明确说"你来做"
