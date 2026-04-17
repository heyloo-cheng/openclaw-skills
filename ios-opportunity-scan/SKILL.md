---
name: ios-opportunity-scan
description: |
  iOS 开发方向从零调研工作流。当用户没有明确 App 方向，想通过数据决策时激活。
  触发词：「帮我做 iOS 开发方向调研」「iOS 软件调查」「不知道做什么 App」「帮我找 iOS 开发方向」
  核心升级：集成 dispatching-parallel-agents 并行方法论 + 推荐追踪系统 + 自主学习。
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
  - WebSearch
  - WebFetch
  - sessions_spawn
  - sessions_send
  - sessions_yield
  - sessions_list
  - Feishu_IM_Bot_SendMessage
  - Feishu_IM_Bot_GetCurrentUserMessageList

## 搜索工具优先级
优先使用 deep-search skill 进行深度搜索：
```bash
node ~/.openclaw/workspace/skills/deep-search/scripts/search-engine.mjs \
  --query "查询词" --depth deep
```
deep-search 不可用时降级到 web_search + web_fetch。
---

# iOS 开发方向从零调研工作流

> ⚡ **性能 + 智能化升级**：并行执行 + 推荐追踪 + 自主学习

---

## Step 0：读取历史积累（学习）

**目标**：在扫描之前，先知道系统已经学到了什么。

### 0A. 读取推荐追踪文件
```bash
cat ~/Obsidian/MyKnowledge/IOS/RECOMMENDATION_TRACKER.md
```

### 0B. 提取「高置信度特征」
从 tracker 中提取：
- **✅ 有效的差异化标签**（用户反馈好、多次佐证）
- **❌ 低效的差异化标签**（用户已麻木、不驱动决策）
- **🔥 跨方向共通信号**（iOS 版本更新、政策变化等）

### 0C. 注入扫描上下文
将以上特征以「参考」形式注入到第一步扫描的 prompt 中：
```
【系统历史学习】
本方向历史推荐 X 次。
已验证有效信号：...
已验证无效信号：...
今日扫描请重点关注：...
```

**目的**：让调研越来越聪明，不重复已知的结论。

---

## 第一步：市场扫描（找机会地图）

### 1A. 环境检查
```bash
echo $EXA_API_KEY | head -c 8
python3 --version
```
如果 EXA_API_KEY 未设置，提示用户：`export EXA_API_KEY=你的key`

### 1B. 痛点扫描

**扫描品类清单（优先级排序）：**
1. 健康与健身（Health & Fitness）
2. 效率工具（Productivity）
3. 财务管理（Finance）
4. 教育学习（Education）
5. 生活方式（Lifestyle）
6. 社交（Social）
7. 摄影与视频（Photo & Video）
8. 饮食与营养（Food & Nutrition）

**每个品类搜索（中英文各一次）：**
```
"{品类} app problems complaints reddit 2025 2026 unsolved"
"best {品类} app ios missing features"
"top grossing {品类} app store revenue"
"{品类} app 差评 知乎 小红书 2025"
```

**优先关注（来自 Step 0 的高置信度特征）：**
- "免费版形同虚设" 类问题
- "订阅套路被扒" 类问题
- "iOS 系统改版引发混乱" 类问题
- 任何符合历史验证有效信号的方向

### 1C. 评分标准

| 维度 | 1分 | 3分 | 5分 |
|------|-----|-----|-----|
| 市场规模 | 小众 | 中等 | 大众 |
| 竞争激烈度（越低越好）| 巨头垄断 | 有竞争 | 空白市场 |
| 付费意愿 | 免费为主 | 部分付费 | 高付费意愿 |
| 独立开发可行性 | 需要大团队 | 小团队 | 1人可做 |

### 1D. 输出机会地图

格式：
```
# iOS 机会地图
生成时间：{YYYY-MM-DD}

## 强烈推荐（总分 ≥ 16）
1. [方向名称] - 总分：X/20
   核心痛点：...
   竞争现状：...
   付费信号：...

## 值得关注（总分 12-15）
...

## 暂不建议（总分 < 12）
...
```

完成后**暂停，询问用户**：
> 「这是当前 iOS 市场机会地图，共发现 XX 个方向。
> 请选择 2-3 个你感兴趣的方向（填序号即可），我将对它们进行深度调研。」

---

## 第二步：等待用户选择方向

用户回复选择后，进入第三步。

---

## 第三步：并行深度调研（dispatching-parallel-agents 模式）

> ⚡ **性能优化**：遵循 dispatching-parallel-agents 原则，并行调度多个独立 subagent。

### 3A. 识别独立任务域

每个方向的调研是完全独立的：
- 饮食营养 → 独立的 deep-search + 竞品研究
- 健康健身 → 独立的 deep-search + 竞品研究
- 财务管理 → 独立的 deep-search + 竞品研究

### 3B. 构造子 agent 任务

每个子 agent 的任务必须包含：
- **具体范围**：品类名称 + 关键词 + 竞品列表
- **明确目标**：执行完整的 ios-market-research 流程
- **报告保存路径**：每个方向独立文件
- **今日日期**：用于追踪

### 3C. 并行 dispatch

**构造示例（假设用户选了 2 个方向）**：

```
sessions_spawn(
  task="
对「{方向1名称}」iOS App 市场进行深度调研，完整执行 ios-market-research skill 流程。
品类关键词：{关键词列表}
竞品示例：{竞品域名}
今日日期：{YYYY-MM-DD}
报告保存到：~/Obsidian/MyKnowledge/IOS/IOS Market Research/iOS调研-{方向1}-{YYYY-MM-DD}.md
",
  runtime="subagent",
  runTimeoutSeconds=600,
  label="ios-research-{方向1}"
)

sessions_spawn(
  task="
对「{方向2名称}」iOS App 市场进行深度调研，完整执行 ios-market-research skill 流程。
品类关键词：{关键词列表}
竞品示例：{竞品域名}
今日日期：{YYYY-MM-DD}
报告保存到：~/Obsidian/MyKnowledge/IOS/IOS Market Research/iOS调研-{方向2}-{YYYY-MM-DD}.md
",
  runtime="subagent",
  runTimeoutSeconds=600,
  label="ios-research-{方向2}"
)
```

### 3D. 收集结果

等待所有 subagent 完成（自动回调），验证各方向报告已保存。

### 3E. 超时处理

如果某个 subagent 超时：
- 其他已完成的报告不受影响
- 超时方向标记为「数据不完整」
- 在第四步对比时降级处理

---

## 第四步：横向对比 + 最终决策建议

对比所有调研方向，生成最终决策报告：

```markdown
# iOS 开发方向最终决策报告
生成时间：{YYYY-MM-DD}

## 调研摘要
共调研 X 个方向

## 横向对比表
| 方向 | 市场规模 | 竞争度 | 付费意愿 | 可行性 | 总分 |
|------|---------|--------|---------|--------|------|
| 方向A | ... | ... | ... | ... | XX |
| 方向B | ... | ... | ... | ... | XX |

## 最终推荐
**建议做：[方向名称]**

理由：
- ...
- ...

## 切入策略
- 差异化定位：...
- 目标用户：...
- MVP 核心功能（3个）：...
- 冷启动策略：...
- 变现方式：...

## 今日新增信号（用于追踪）
- {信号1}
- {信号2}
- {信号3}

## 信号来源
- {URL 或来源}
```

保存到：`~/Obsidian/MyKnowledge/IOS/IOS Market Research/iOS开发方向决策报告-{YYYY-MM-DD}.md`

---

## 第五步：更新推荐追踪

读取 tracker，更新今日推荐记录。

### 5A. 判断推荐状态

```
今日推荐是新方向？
  ├─ 是 → 新增推荐条目，记录全部信息
  └─ 否 → 更新已有条目，分析今日变化
```

### 5B. 推荐追踪文件格式

如果文件不存在，创建：
```markdown
# iOS 推荐追踪系统
创建时间：{YYYY-MM-DD}

---

## 📊 每日信号状态

| 日期 | 扫描方向数 | 有无变化 | 变化类型 | 报告发送 |
|------|-----------|---------|---------|---------|
| {YYYY-MM-DD} | X | ... | ... | ✅/❌ |
```

### 5C. 推荐条目格式

```markdown
### {方向名称}（{YYYY-MM-DD}）
**推荐指数**：⭐⭐⭐⭐⭐
**热度趋势**：▲ 持续上升 / ▼ 下降 / ➡️ 持平

**历史推荐记录**：
- {历史日期1}：首次推荐，理由：...
- {历史日期2}：重复推荐，变化：...

**🔥 今日新增信号**：
- {新增痛点/需求}

**📉 减弱信号**：
- {已解决/减弱的痛点}

**💡 调研洞察**：
{一句话总结今日调研最重要的发现}

**信号来源**：
- {来源1 URL}
- {来源2 URL}
```

### 5D. 高置信度特征更新

在 tracker 末尾追加「系统学习到的规律」：
```markdown
## 🧠 系统学习到的规律

### ✅ 有效的差异化标签
- {标签1}（来源：{推荐日期}）
- {标签2}（来源：{推荐日期}）

### ❌ 低效的差异化标签
- {标签1}（来源：{推荐日期}）

### 🔥 跨方向共通信号
- {信号1}（影响：{相关方向}）
```

### 5E. 保存 tracker
保存到：`~/Obsidian/MyKnowledge/IOS/RECOMMENDATION_TRACKER.md`

---

## 第六步：智能发送决策

### 6A. 判断是否发送报告

基于以下条件判断今日报告是否值得发送：

| 触发条件 | 说明 | 发送？ |
|---------|------|--------|
| **新方向首次推荐** | 之前没推荐过 | ✅ |
| **已有方向热度升级** | 新增重要信号 | ✅ |
| **无实质变化** | 和历史记录高度重复 | ❌ |

### 6B. 发送逻辑

```
有值得发的内容？
  ├─ 是 → 生成并发送完整报告到飞书群
  └─ 否 → 更新 tracker，记录「今日无实质变化」
           向飞书群发送简短通知：
           「📊 iOS 市场追踪 {YYYY-MM-DD}：今日无实质变化，已更新 tracker。
            上次推荐：{方向}（{日期}），信心度：⭐⭐⭐⭐⭐」
```

### 6C. 发送模板（有实质变化）

```
📱 iOS 开发方向调研报告 {YYYY-MM-DD}

🔍 今日推荐：{方向名称}
💡 核心洞察：{1句话}

🔥 新增信号：
• {信号1}
• {信号2}

📈 vs 上次推荐：
{对比说明}

📄 完整报告已保存至 Obsidian
```

---

## 触发词

- 「帮我做 iOS 开发方向调研」
- 「iOS 软件调查」
- 「不知道做什么 App，帮我调研」
- 「帮我找 iOS 开发方向」
- 「用数据决策 iOS 开发方向」
- 「iOS 市场机会扫描」
- 「做一次 iOS 市场调研」

## 核心原则

1. **不发则已，发则有料** — 无实质变化不发完整报告
2. **持续学习** — 每次调研都更新 tracker 的高置信度特征
3. **并行优先** — 多个方向并行调研，节省时间
4. **数据真实** — 所有结论必须来自实际搜索，不编造
5. **明确结论** — 最终报告必须给出「建议做 / 不建议做 / 调整方向」
