---
name: unified-search
version: 0.2.0
description: 统一搜索接口，整合 LSS、LanceDB、文件系统和 Web 搜索
author: boton
created: 2026-03-02
updated: 2026-03-02
triggers:
  - 搜索
  - 查询
  - 查找
  - 找
  - search
  - find
  - research
examples:
  - "搜索 ToolBox 的认证流程"
  - "查找 ClipMind 的架构文档"
  - "search for Smart Camera implementation"
  - "find authentication code in ToolBox"
dependencies:
  - lss (installed via pipx)
  - memory_recall (built-in)
  - web_search (built-in)
  - ripgrep (optional)
priority: 8
---

# Unified Search Skill

统一搜索接口，智能路由到最合适的搜索源。

## 🎯 核心功能

### 智能路由
- 自动识别查询意图
- 选择最合适的搜索源
- 支持多源组合搜索
- 自动降级策略

### 搜索源

#### 1. LSS (Local Semantic Search) ⭐ 新增
- **用途**: 本地项目文档搜索
- **技术**: BM25 + embeddings + RRF (Reciprocal Rank Fusion)
- **索引**: ToolBox, ClipMind, VaultMind 项目
- **优势**: 
  - 混合搜索（关键词 + 语义）
  - 100% 离线可用
  - 高性能（0.91 NDCG@10）
  - 实时文件监控
- **命令**: `lss "query" ~/projects/ToolBox --json`
- **适配器**: `sources/lss.mjs`

#### 2. LanceDB Memory
- **用途**: 长期记忆搜索
- **类型**: fact, decision, lesson, entity
- **返回**: 记忆条目 + 时间戳 + 重要性
- **工具**: `memory_recall`

#### 3. 文件系统搜索
- **用途**: 代码搜索
- **工具**: ripgrep (rg)
- **范围**: workspace 目录
- **返回**: 文件路径 + 代码片段

#### 4. Web Search
- **用途**: 网络搜索
- **工具**: `web_search` (Brave API)
- **返回**: 标题 + URL + 摘要

#### 5. Deep Search (委派)
- **用途**: 深度调研
- **委派**: `deep-search` skill
- **技术**: Exa → Tavily → Crawl4AI 三层降级

## 📋 路由规则

### 优先级排序

| 优先级 | 规则 | 搜索源 | 触发关键词 |
|--------|------|--------|-----------|
| 11 | 深度搜索 | deep-search | 深度搜索, deep search, 详细调研 |
| 10 | 项目文档 | lss | ToolBox, ClipMind, VaultMind |
| 9.5 | 时间敏感 | web | 最新, latest, 今天, 2026 |
| 9 | 记忆搜索 | memory | 记忆, 决策, 教训, 之前 |
| 8 | 代码搜索 | files | 代码, 函数, class, .js, .py |
| 7 | 网络搜索 | web | 搜索网络, search web, 在线 |

### 路由逻辑

```javascript
// 1. 检测深度搜索关键词 → 委派给 deep-search skill
if (query.includes('深度搜索') || query.includes('deep search')) {
  return { delegate: 'deep-search' };
}

// 2. 检测项目名 → LSS 搜索
if (query.includes('ToolBox') || query.includes('ClipMind')) {
  return { sources: ['lss'], project: 'toolbox' };
}

// 3. 检测时间敏感词 → Web 搜索
if (query.includes('最新') || query.includes('今天')) {
  return { sources: ['web'] };
}

// 4. 检测记忆关键词 → Memory 搜索
if (query.includes('之前') || query.includes('决策')) {
  return { sources: ['memory'] };
}

// 5. 多规则匹配 → 组合搜索
if (matchedRules.length > 1) {
  return { sources: [rule1.source, rule2.source] };
}

// 6. 默认策略 → LSS + Memory
return { sources: ['lss', 'memory'] };
```

## 🔧 使用方法

### 命令行接口

```bash
node ~/.openclaw/workspace/skills/unified-search/search.mjs \
  --query "搜索关键词" \
  --sources "lss,memory,files,web" \
  --project "toolbox" \
  --limit 5
```

### 路由测试

```bash
node ~/.openclaw/workspace/skills/unified-search/router.mjs
```

### LSS 适配器测试

```bash
node ~/.openclaw/workspace/skills/unified-search/sources/lss.mjs "authentication"
```

## 📊 示例

### 示例 1: 项目文档搜索
```
用户: "搜索 ToolBox 的认证流程"
路由: sources=['lss'], project='toolbox'
结果: ToolBox 项目中关于认证的文档片段
```

### 示例 2: 记忆搜索
```
用户: "我们之前对 context-engine 做了什么决策"
路由: sources=['memory']
结果: 相关的决策记录和讨论历史
```

### 示例 3: 组合搜索
```
用户: "ToolBox 的认证方案我们之前讨论过吗"
路由: sources=['lss', 'memory'], project='toolbox'
结果: 项目文档 + 历史讨论记录
```

### 示例 4: 深度搜索委派
```
用户: "深度搜索 xMemory 论文"
路由: delegate='deep-search'
结果: 委派给 deep-search skill 执行
```

### 示例 5: 时间敏感查询
```
用户: "最新的 OpenClaw 功能"
路由: sources=['web']
结果: 网络搜索最新信息
```

## 🚀 安装和配置

### 1. 安装 LSS

```bash
# 安装 pipx (如果未安装)
brew install pipx

# 安装 LSS (离线模式)
pipx install 'local-semantic-search[local]'

# 配置为离线模式
lss config provider local
```

### 2. 验证安装

```bash
# 检查 LSS 是否可用
which lss

# 测试搜索
lss "test query" ~/.openclaw/workspace --json
```

### 3. 注册 Skill

```bash
cd ~/.openclaw/workspace
python3 scripts/skill-register.py
```

## 🔄 迁移说明

### 从 QMD 迁移到 LSS

**变更**:
- ✅ 搜索源从 `qmd` 改为 `lss`
- ✅ 路由规则已更新
- ✅ 测试用例已更新
- ✅ LSS 适配器已创建

**优势**:
- 🚀 更好的性能（0.91 NDCG@10 vs QMD）
- 🔒 100% 离线可用
- 🛠️ 更稳定（无 M1 Mac 兼容性问题）
- 📊 实时文件监控

**兼容性**:
- LSS 和 QMD 使用相同的混合搜索架构（BM25 + embeddings + RRF）
- API 接口保持一致
- 搜索结果格式统一

## 📝 待办事项

- [ ] 实现主搜索逻辑 (`search.mjs`)
- [ ] 创建 Memory 适配器 (`sources/memory.mjs`)
- [ ] 创建 Files 适配器 (`sources/files.mjs`)
- [ ] 创建 Web 适配器 (`sources/web.mjs`)
- [ ] 实现结果融合和去重
- [ ] 添加搜索缓存
- [ ] 集成到 OpenClaw agent

## 🐛 故障排查

### LSS SSL 警告
```
Local embedding failed: [SSL: UNEXPECTED_EOF_WHILE_READING]
```
**原因**: embeddings 模型下载失败  
**影响**: 仅影响语义搜索，BM25 关键词搜索仍可用  
**解决**: 忽略警告，或手动下载模型

### LSS 未找到
```
zsh:1: command not found: lss
```
**解决**: 
```bash
pipx ensurepath
source ~/.zshrc
```

## 📚 参考资料

- [LSS GitHub](https://github.com/kortix-ai/lss)
- [LSS PyPI](https://pypi.org/project/local-semantic-search/)
- [Deep Search Skill](~/.openclaw/workspace/skills/deep-search/)
- [QMD Integration Plan](~/.openclaw/workspace/docs/qmd-integration-plan.md)
