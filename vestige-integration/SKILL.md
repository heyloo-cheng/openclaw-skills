# vestige-integration

FSRS-6 科学记忆管理 + 29 脑模块集成

## 概述

vestige 是基于 130 年记忆研究的认知记忆系统，实现了 FSRS-6 间隔重复算法、扩散激活、突触标记等机制。

## 特性

- 🧠 **FSRS-6 间隔重复** — 科学的记忆巩固算法
- 🔗 **29 个认知模块** — 模拟人类记忆过程
- 📊 **自动记忆巩固** — 定期运行 consolidation
- 🔍 **智能检索** — 7 阶段认知搜索管道
- 📈 **记忆健康监控** — 保留率、趋势追踪

## 使用

### 存储记忆

```javascript
import { store } from './index.mjs';

await store({
  text: "OpenClaw 是 AI 助手框架",
  tags: ["system", "framework"],
  importance: 0.9
});
```

### 检索记忆

```javascript
import { recall } from './index.mjs';

const results = await recall("OpenClaw 架构");
// 返回相关记忆，按 FSRS-6 排序
```

### 复习计划

```javascript
import { getReviewPlan } from './index.mjs';

const plan = await getReviewPlan();
// 返回需要复习的记忆列表
```

### 记忆巩固

```javascript
import { consolidate } from './index.mjs';

await consolidate();
// 运行记忆巩固周期
```

### 健康检查

```javascript
import { health } from './index.mjs';

const status = await health();
// 返回记忆系统健康状态
```

## CLI 命令

```bash
# 存储记忆
vestige ingest "text" --tags tag1,tag2

# 搜索记忆
vestige search "query"

# 查看统计
vestige stats

# 记忆巩固
vestige consolidate

# 健康检查
vestige health

# 备份
vestige backup

# 导出
vestige export --format json
```

## 配置

### 环境变量

```bash
# 数据目录（默认: ~/.vestige/data）
VESTIGE_DATA_DIR=/custom/path

# 日志级别
RUST_LOG=debug

# 巩固间隔（小时，默认: 6）
VESTIGE_CONSOLIDATION_INTERVAL_HOURS=6

# 保留率目标（默认: 0.8）
VESTIGE_RETENTION_TARGET=0.8
```

## 集成到 OpenClaw

### memory-lancedb-pro 集成

```typescript
import { store as vestigeStore, recall as vestigeRecall } from '../../../skills/vestige-integration/index.mjs';

// 存储时同时写入 vestige
async function storeMemory(text, category, importance) {
  // 1. 存到 LanceDB
  await lancedb.insert({ text, category, importance });
  
  // 2. 重要记忆存到 vestige（FSRS-6）
  if (importance >= 0.8) {
    await vestigeStore({ text, tags: [category], importance });
  }
}

// 检索时合并结果
async function recallMemory(query) {
  // 1. vestige 检索（FSRS-6 排序）
  const vestigeResults = await vestigeRecall(query);
  
  // 2. LanceDB 检索（向量相似度）
  const lanceResults = await lancedb.search(query);
  
  // 3. 合并排序
  return mergeResults(vestigeResults, lanceResults);
}
```

## 架构

```
vestige CLI
  ↓
SQLite Database (~/.vestige/data/vestige.db)
  ├─ memories 表
  ├─ memory_connections 表
  ├─ dream_history 表
  └─ retention_snapshots 表
  ↓
FSRS-6 算法
  ├─ 间隔重复
  ├─ 遗忘曲线
  └─ 记忆巩固
```

## 性能

- **存储**: ~10ms
- **检索**: ~50ms（含 FSRS-6 排序）
- **巩固**: ~1s（100 条记忆）
- **数据库**: SQLite（单文件）

## 限制

- 仅支持文本记忆（不支持图片、音频）
- Embeddings 需要额外配置（fastembed）
- MCP server 模式暂不可用（使用 CLI）

## 故障排除

### Embeddings 未启用

**症状**: "Embeddings not available, falling back to regular ingest"

**解决**:
```bash
# 下载 fastembed 模型
RUST_LOG=debug vestige ingest "test" --tags "test"
```

### 数据库锁定

**症状**: "database is locked"

**解决**:
```bash
# 关闭所有 vestige 进程
pkill -f vestige

# 重新启动
vestige stats
```

## 参考

- GitHub: https://github.com/samvallad33/vestige
- FSRS-6 论文: https://arxiv.org/abs/2307.08716
- 文档: https://github.com/samvallad33/vestige/blob/main/CLAUDE.md
