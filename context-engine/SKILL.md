---
name: context-engine
description: Topic-based dynamic context loading plugin. Classifies messages by topic, compresses inactive topics, loads only relevant context. Inspired by virtual-context's 3-layer architecture.
version: "0.1.0"
triggers:
  - context engine
  - 上下文
  - 话题分类
  - topic classification
  - dynamic context
  - context loading
  - 动态加载
  - context swap
examples:
  - "切换话题时自动压缩旧上下文"
  - "只加载当前话题的记忆"
  - "reduce context window usage"
---

# Context Engine

基于话题的动态上下文加载插件。借鉴 virtual-context 的 3 层架构，用 OpenClaw 原生 `before_prompt_build` hook 实现。

## 工作原理

```
消息进来 → 话题分类(9类) → 当前话题保留完整上下文
                          → 其他话题压缩为1行摘要
话题切换 → 旧话题自动压缩 → 新话题加载完整历史
```

## 话题分类

| 话题 | 关键词 |
|------|--------|
| coding | 代码/code/bug/fix/refactor/review |
| config | 配置/config/plugin/install |
| memory | 记忆/memory/lancedb/recall |
| skill | skill/技能/router/trigger |
| agent | agent/委派/delegate/thinker/coder |
| security | 安全/security/audit |
| search | 搜索/search/github |
| planning | 计划/plan/roadmap |
| chat | 闲聊/hello |

## 安装

插件路径：`~/.openclaw/workspace/plugins/context-engine/`

```bash
cd ~/.openclaw/workspace/plugins/context-engine
npm install && npm run build
openclaw plugins install -l .
openclaw gateway restart
```

## 架构

3 个 hook：
- `before_prompt_build` — 话题分类 + 动态上下文注入
- `llm_output` — 追踪当前话题活跃度
- `before_compaction` — compaction 前保存话题摘要

## 下一步

- v0.2: 接入 LanceDB 向量化做语义话题分类（替代正则）
- v0.3: 话题级别语义缓存
- v0.4: 跨 session 话题持久化
