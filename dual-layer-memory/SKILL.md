---
name: dual-layer-memory
description: Dual-layer memory storage system for LanceDB. Every lesson stored as both fact (technical) and decision (principle) layers with mandatory recall verification.
version: "1.0"
triggers:
  - 双层记忆
  - dual layer memory
  - 铁律
  - lesson store
  - 教训记录
  - memory rules
  - fact decision
  - 记忆存储规则
examples:
  - "记录这个教训到 LanceDB"
  - "store this lesson with dual layer"
  - "按铁律存储记忆"
---

# Dual-Layer Memory System

每个教训/经验必须存两条 LanceDB 记忆，确保从不同角度都能检索到。

## 规则

### 技术层 (fact, importance ≥ 0.8)
```
Pitfall: [症状]. Cause: [根因]. Fix: [方案]. Prevention: [预防]
```

### 原则层 (decision, importance ≥ 0.85)
```
Decision principle ([tag]): [规则]. Trigger: [触发条件]. Action: [动作]
```

## 流程

```
1. 识别教训/经验
2. memory_store(category="fact", importance=0.8, text="Pitfall: ...")
3. memory_store(category="decision", importance=0.85, text="Decision principle: ...")
4. memory_recall 验证技术层能检索到（命中率 > 40%）
5. memory_recall 验证原则层能检索到（命中率 > 40%）
6. 两层都验证通过才能继续
```

## 约束

- 每条记忆 < 500 字符
- 不存原始对话摘要或大块文本
- 结构化格式 + 关键词便于检索
- 一条记忆 = 一个知识点

## Importance 分级

| 分数 | 含义 |
|------|------|
| 0.9+ | 铁律级别，永不遗忘 |
| 0.8-0.9 | 重要经验，长期保留 |
| 0.7-0.8 | 一般知识，正常衰减 |
| < 0.7 | 低优先级，可被遗忘 |

## 分类规范

| Category | 用途 |
|----------|------|
| fact | 客观事实、技术细节、踩坑记录 |
| decision | 决策原则、工作流规则、Checklist |
| preference | 用户偏好、个人习惯 |
| entity | 人物、项目、设备信息 |
