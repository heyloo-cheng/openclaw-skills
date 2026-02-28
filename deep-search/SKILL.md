---
name: deep-search
description: 三层降级深度搜索引擎（Exa → Tavily → Crawl4AI），支持语义搜索、深度研究、自动容错。触发词：深度搜索、deep search、深搜、详细搜索、帮我查、调研、research。
triggers:
  - 深度搜索
  - deep search
  - 深搜
  - 详细搜索
  - 帮我查
  - 调研
  - research
  - 搜一下
  - 帮我搜
  - 查一下
---

# Deep Search — 三层降级深度搜索引擎

## 架构

```
Exa (AI语义搜索) → Tavily (AI agent搜索) → Crawl4AI + web_fetch (兜底)
```

每层有独立熔断器，连续失败 3 次自动跳过 30 分钟。

## 使用方式

### 1. 判断搜索深度

| 用户意图 | 深度 | Exa 模式 |
|----------|------|----------|
| 简单事实查询 | quick | `type: "auto"` |
| 技术调研 | deep | `type: "deep"` |
| 深度研究/报告 | max | `type: "deep-max"` |

### 2. 执行搜索

```bash
node ~/.openclaw/workspace/skills/deep-search/scripts/search-engine.mjs \
  --query "你的搜索问题" \
  --depth deep
```

### 3. 环境变量

```
EXA_API_KEY=xxx        # 从 https://dashboard.exa.ai 获取
TAVILY_API_KEY=xxx     # 从 https://app.tavily.com 获取
```

### 4. 容错规则

- 每个 provider 独立熔断（3 次失败 → 30min 冷却）
- 超时 15 秒自动降级
- 空结果换关键词重试 1 次再降级
- 额度用完(429)立即降级
- 全部失败返回空数组 + 告警

### 5. 结果增强

搜索结果经过：
1. Jina reranker 排序（如可用）
2. 去重（cosine distance < 0.1）
3. 存入 context-engine semantic 层（如可用）
