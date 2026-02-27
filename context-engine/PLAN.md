# Context Engine v1.0 — 执行方案

> 融合 xMemory (ICML 2026) + MemWeaver (WWW'26) + 现有 LanceDB 双层记忆
> 目标：让 Agent 的记忆从"金鱼"进化为"大象"

---

## 一、架构总览

```
┌──────────────────────────────────────────────────────┐
│                   用户消息入口                         │
├──────────────────────────────────────────────────────┤
│  SecureClaw (安全层)                                  │
├──────────────────────────────────────────────────────┤
│  Manifest (模型路由层)                                │
├──────────────────────────────────────────────────────┤
│  Context Engine v1.0 (本方案)                         │
│                                                      │
│  ┌─────────────────────────────────────────────┐     │
│  │  Layer A: 对话上下文 (xMemory)               │     │
│  │  Messages → Episode → Semantic → Theme       │     │
│  │  自顶向下检索 + 不确定性门控展开             │     │
│  ├─────────────────────────────────────────────┤     │
│  │  Layer B: 用户画像 (MemWeaver)               │     │
│  │  行为记忆 (temporal + semantic 双边网络)      │     │
│  │  认知记忆 (分阶段偏好 → 全局画像)           │     │
│  │  联想回忆 (kNN 图随机游走)                   │     │
│  ├─────────────────────────────────────────────┤     │
│  │  Layer C: 双层事实 (现有 LanceDB)            │     │
│  │  fact/decision 铁律 + 时间衰减 + Jina embed  │     │
│  │  语义缓存 + skill 向量索引                   │     │
│  └─────────────────────────────────────────────┘     │
│                                                      │
│  → 合并注入 systemPrompt (用户不可见)                │
├──────────────────────────────────────────────────────┤
│  委派层 (AGENTS.md 规则 + OpenSpec)                   │
├──────────────────────────────────────────────────────┤
│  memory-lancedb-pro (记忆存储层)                      │
└──────────────────────────────────────────────────────┘
```

---

## 二、LanceDB 表设计

### 现有表（保留不动）
| 表名 | 用途 | 记录数 |
|------|------|--------|
| memories | fact/decision 双层记忆 | ~50+ |
| skills | 75 个 skill 向量索引 | 75 |
| semantic_cache | 语义缓存 | 动态增长 |

### 新增表

#### 2.1 themes 表（最高层 — 鸟瞰）
```
{
  theme_id:    string,       // 唯一 ID
  name:        string,       // 主题名称（如 "后端安全"、"UI开发"）
  summary:     string,       // 1-2 句话摘要
  semantic_ids: string[],    // 关联的 semantic 节点 ID
  message_count: number,     // 累计消息数
  last_active: timestamp,    // 最后活跃时间
  embedding:   float[1024],  // Jina v5 向量
  knn_neighbors: string[],   // 最近邻 theme_id（用于图导航）
}
```
- 自动 split：当 semantic_ids.length > 12 时，用 k-means 聚类拆分
- 自动 merge：当 semantic_ids.length < 3 且与邻居相似度 > 0.8 时合并
- 稀疏性-语义引导函数控制 split/merge 决策（xMemory Eq.1）

#### 2.2 semantics 表（语义单元 — 可复用事实）
```
{
  semantic_id:  string,       // 唯一 ID
  theme_id:     string,       // 所属 theme
  content:      string,       // 提取的语义事实（如 "API 认证使用 JWT + refresh token"）
  episode_ids:  string[],     // 来源 episode ID
  created_at:   timestamp,
  updated_at:   timestamp,
  embedding:    float[1024],  // Jina v5 向量
  knn_neighbors: string[],   // 最近邻 semantic_id
}
```
- 从 episode 中用 haiku 提取可复用事实
- 去重：新 semantic 与已有的余弦距离 < 0.15 时合并而非新建
- 每个 semantic 只属于一个 theme

#### 2.3 episodes 表（片段摘要 — 连续消息块）
```
{
  episode_id:   string,       // 唯一 ID
  summary:      string,       // haiku 生成的摘要（50-100 token）
  turn_start:   number,       // 起始消息序号
  turn_end:     number,       // 结束消息序号
  message_count: number,      // 包含的消息数
  session_id:   string,       // 所属会话
  created_at:   timestamp,
  embedding:    float[1024],  // Jina v5 向量
  raw_messages: string,       // 原始消息（JSON，用于 Stage II 展开）
}
```
- 每 5-10 条连续消息生成一个 episode
- 话题切换时强制切分（即使不到 5 条）
- 摘要用 haiku 生成，成本约 $0.001/次

#### 2.4 user_profile 表（用户画像 — MemWeaver）
```
{
  profile_id:   string,       // 唯一 ID
  user_id:      string,       // 用户标识
  phase:        string,       // 时间阶段（如 "2026-02-W4"）
  behavioral:   string,       // 行为记忆：这个阶段做了什么
  cognitive:    string,       // 认知记忆：偏好/习惯/风格
  global_profile: string,     // 全局画像（所有阶段合并）
  updated_at:   timestamp,
  embedding:    float[1024],
}
```
- 每周自动生成一次阶段画像（cron）
- 全局画像 = 所有阶段的认知记忆合并摘要
- 行为记忆从 episodes 提取，认知记忆从 semantics 抽象


---

## 三、检索策略（自顶向下，两阶段）

### Stage I：广度检索（Theme + Semantic 层）

```
用户消息 → Jina embedding 向量化
  ↓
查 themes 表：余弦相似度 top-3 theme
  ↓
拉这 3 个 theme 下的所有 semantics
  ↓
用 kNN 图扩展：检查邻居 theme 是否也相关（防遗漏）
  ↓
贪心子模选择（xMemory Eq.4）：
  - 平衡覆盖度（coverage）和查询相关性（relevance）
  - α=0.5 初始值，后续根据反馈调整
  ↓
输出：5-10 个最相关的 semantic 节点
```

**Token 预算：** ~150 token（每个 semantic 约 15-20 token）

### Stage II：深度展开（Episode + Message 层）

```
判断 Stage I 的 semantics 是否足够回答：
  ↓
方法：用 haiku 快速评估（1 次调用，~$0.0005）
  prompt: "基于以下语义摘要，能否回答用户问题？回答 YES/NO/PARTIAL"
  ↓
  YES → 直接用 semantics，不展开（最省 token）
  PARTIAL → 展开相关 episodes（+200 token）
  NO → 展开到原始 messages（+500 token，上限）
```

**不确定性门控简化版：**
- 生产环境不用 logits（OpenClaw 拿不到），用 haiku 判断替代
- 效果接近，成本极低

### 注入合并

```
systemPrompt 注入顺序（总预算 ~400 token）：

1. Theme 鸟瞰（~50 token）
   "## Active Context\n当前话题: [theme_name]\n相关话题: [theme1], [theme2]"

2. 认知记忆（~100 token）
   "## User Profile\n[global_profile 摘要]"

3. Semantic 事实（~150 token）
   "## Relevant Facts\n- [semantic_1]\n- [semantic_2]\n..."

4. Episode 展开（按需，0-200 token）
   "## Details\n[episode_summary]"

5. fact/decision 记忆（现有 memory-lancedb-pro，~100 token）
   "<relevant-memories>...</relevant-memories>"
```

**总 token 预算：300-500 token（比当前方案省 40-60%）**

---

## 四、构建流程（后台异步）

### 4.1 实时构建（每次对话结束触发）

```
agent_end hook 触发：
  ↓
Step 1: 生成 Episode
  - 取最近 N 条未处理消息
  - haiku 生成摘要（50-100 token）
  - Jina 向量化
  - 存入 episodes 表
  ↓
Step 2: 提取 Semantic
  - haiku 从 episode 提取可复用事实
  - prompt: "从以下对话摘要中提取 1-3 个可复用的事实，每个 < 20 token"
  - 去重检查：与已有 semantics 余弦距离 < 0.15 → 合并
  - 存入 semantics 表
  ↓
Step 3: 归入 Theme
  - 新 semantic 向量 → 查 themes 表最近邻
  - 距离 < 0.3 → 归入该 theme
  - 距离 >= 0.3 → 创建新 theme（haiku 生成名称）
  - 检查 theme 大小：> 12 → split，< 3 → merge
  ↓
Step 4: 更新 kNN 图
  - 重算受影响节点的 top-5 邻居
  - 只更新变化的边，不全量重建
```

### 4.2 周期构建（每周日 cron）

```
Step 1: 用户画像更新
  - 收集本周所有 episodes → 生成行为记忆摘要
  - 收集本周所有 semantics → 生成认知记忆摘要
  - 合并历史认知记忆 → 更新全局画像
  ↓
Step 2: Theme 健康检查
  - 遍历所有 themes
  - 过大(>12) → split
  - 过小(<3) → merge
  - 30 天无活跃 → 标记为 dormant（检索时降权）
  ↓
Step 3: Semantic 去重
  - 全量扫描 semantics 表
  - 余弦距离 < 0.1 的对 → 合并
  - 更新关联的 theme 和 episode 引用
```

### 4.3 成本估算

| 操作 | 频率 | 模型 | 成本/次 |
|------|------|------|---------|
| Episode 生成 | 每次对话结束 | haiku | $0.001 |
| Semantic 提取 | 每次对话结束 | haiku | $0.001 |
| Theme 命名 | 新 theme 创建时 | haiku | $0.0005 |
| Stage II 判断 | 每次检索 | haiku | $0.0005 |
| 周画像更新 | 每周 | sonnet | $0.01 |
| Jina 向量化 | 每次存储 | Jina v5 | $0.0001 |

**日均成本：** ~$0.05（假设 20 次对话/天）
**月均成本：** ~$1.5


---

## 五、实现计划（分 4 个迭代）

### 迭代 1：骨架（2 天）
**目标：** LanceDB 建表 + Episode 生成 + 基础检索

- [ ] LanceDB 创建 themes/semantics/episodes/user_profile 4 张表
- [ ] context-engine 插件 agent_end hook：生成 episode 摘要
- [ ] context-engine 插件 before_prompt_build hook：查 themes → 注入 systemPrompt
- [ ] 测试：发 10 条消息，验证 episode 自动生成

**交付物：** 能自动生成 episode 并按 theme 检索

### 迭代 2：语义层（2 天）
**目标：** Semantic 提取 + Theme 自动管理

- [ ] haiku 从 episode 提取 semantic 事实
- [ ] semantic 去重逻辑（余弦距离 < 0.15 合并）
- [ ] theme 自动归类（最近邻匹配 or 新建）
- [ ] theme split/merge 逻辑
- [ ] kNN 图构建（top-5 邻居）

**交付物：** 完整的 4 层层级自动构建

### 迭代 3：智能检索（2 天）
**目标：** 两阶段检索 + 不确定性门控

- [ ] Stage I：贪心子模选择（coverage + relevance）
- [ ] Stage II：haiku 判断是否需要展开
- [ ] 注入合并逻辑（theme + cognitive + semantic + episode + memory）
- [ ] Token 预算控制（总量 < 500 token）

**交付物：** 完整的自顶向下检索 + 注入

### 迭代 4：用户画像（1 天）
**目标：** MemWeaver 双组件记忆

- [ ] 行为记忆：从 episodes 提取本周行为摘要
- [ ] 认知记忆：从 semantics 抽象偏好/习惯
- [ ] 全局画像：合并历史认知记忆
- [ ] 周 cron 自动更新
- [ ] 注入 systemPrompt 的 User Profile 段

**交付物：** 用户画像自动演化 + 注入

---

## 六、额外想法（超越论文）

### 6.1 跨 Agent 记忆共享
xMemory 和 MemWeaver 都是单 Agent 方案。我们有 7 个 Agent。

**想法：** Theme 层全局共享，Semantic 层按 Agent 隔离。
- main/thinker/coder 共享 "coding" theme 下的 semantics
- artist 只看到 "design" theme
- 委派时自动传递相关 theme 的 semantics 作为上下文

### 6.2 反馈驱动的检索权重调整
论文没解决的：检索结果好不好？

**想法：** 每次回答后记录 {query, retrieved_themes, retrieved_semantics, user_reaction}
- user_reaction: 用户继续追问同话题 = 不满意（检索不够）
- user_reaction: 用户说"对"/"好的" = 满意
- 用这个信号调整 Stage I 的 α 参数（coverage vs relevance 平衡）

### 6.3 预测性预加载
论文是被动检索。我们可以主动预测。

**想法：** 基于时间模式预加载
- 用户每天早上 9 点聊代码 → 9 点自动预加载 "coding" theme
- 用户周五下午聊部署 → 周五自动预加载 "deployment" theme
- 实现：cron 分析 episodes 的时间分布，生成预加载规则

### 6.4 记忆遗忘曲线
现有 memory-lancedb-pro 有 60 天半衰期。但 theme 层不应该遗忘。

**想法：** 分层遗忘策略
- Theme: 永不遗忘（鸟瞰层，token 极少）
- Semantic: 慢遗忘（180 天半衰期，可复用事实有长期价值）
- Episode: 快遗忘（30 天半衰期，细节价值递减）
- Message: 最快遗忘（7 天后只保留 episode 摘要，原文删除）

### 6.5 语义缓存升级
现有 semantic_cache 是扁平的。可以升级为 theme 级缓存。

**想法：** 同一个 theme 下的相似问题共享缓存
- 缓存 key = theme_id + query_embedding
- 命中率预计提升 2-3 倍（同话题问题天然相似）

### 6.6 可观测性
OpenViking 的可视化检索轨迹很好。我们也需要。

**想法：** 每次检索记录轨迹到 LanceDB
```
{
  query, timestamp,
  matched_themes: [...],
  selected_semantics: [...],
  expanded_episodes: [...],
  stage2_decision: "YES/PARTIAL/NO",
  total_tokens_injected: N,
  user_satisfaction: "unknown" → 后续标注
}
```
- skill-dashboard.py 可以读这个表生成检索效果报告
- 周报里加入"检索命中率"和"平均注入 token"指标

---

## 七、风险和缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| haiku 生成的摘要质量差 | 语义丢失 | 定期人工抽检 + 反馈信号自动标记 |
| theme split/merge 震荡 | 结构不稳定 | 加冷却期（split 后 24h 内不 merge） |
| LanceDB 表太多性能下降 | 检索变慢 | 监控查询延迟，必要时合并小表 |
| 向量化成本超预期 | 月费用增加 | Jina 有免费额度，超出切本地模型 |
| 与 memory-lancedb-pro 冲突 | 双重注入 | 明确分工：memory 管 fact/decision，context-engine 管其余 |

---

## 八、成功指标

| 指标 | 当前值 | 目标值 | 测量方式 |
|------|--------|--------|----------|
| 每次注入 token 数 | ~300 (memory only) | < 500 (全量) | 日志统计 |
| 话题切换时的上下文相关性 | 低（正则分类） | 高（向量匹配） | 人工评估 |
| 跨 session 记忆召回率 | 0%（无持久化） | > 60% | 测试问答 |
| 用户画像准确度 | 无 | > 70% | 人工评估 |
| 构建成本 | $0/天 | < $0.05/天 | API 账单 |

---

## 九、与现有系统的关系

```
context-engine v1.0 (本方案)
  ├── 替代：context-engine v0.2（正则分类 + 内存 Map）
  ├── 保留：memory-lancedb-pro（fact/decision 双层记忆）
  ├── 保留：semantic_cache 表（升级为 theme 级缓存）
  ├── 保留：skills 表（75 个 skill 向量索引）
  ├── 集成：Manifest（模型路由，haiku 用于构建，sonnet 用于画像）
  └── 集成：SecureClaw（安全审计不变）
```

---

*文档版本: v1.0*
*创建时间: 2026-02-28 01:45*
*基于: xMemory (arxiv 2602.02007) + MemWeaver (arxiv 2510.07713)*
*作者: boton + AI*
