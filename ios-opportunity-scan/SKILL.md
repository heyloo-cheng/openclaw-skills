---
name: ios-opportunity-scan
description: |
  iOS 开发方向从零调研工作流。当用户没有明确 App 方向，想通过数据决策时激活。
  触发词：「帮我做 iOS 开发方向调研」「iOS 软件调查」「不知道做什么 App」「帮我找 iOS 开发方向」
  执行四步：市场扫描→用户选方向→深度调研→最终决策建议。
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
  - WebSearch
  - WebFetch

## 搜索工具优先级
优先使用 deep-search skill 进行深度搜索：
```bash
node ~/.openclaw/workspace/skills/deep-search/scripts/search-engine.mjs \
  --query "查询词" --depth deep
```
deep-search 不可用时降级到 web_search + web_fetch。
---

# iOS 开发方向从零调研工作流

用户没有明确 App 方向，想通过数据来决策。执行完整的四步流程。

---

## 第一步：市场扫描（找机会地图）

目标：发现 15-20 个潜在 iOS 机会方向，不限品类。

### 1A. 运行 hunter signal-scan

参考 hunter skill 的 signal-scan，扫描以下品类（每个品类用 web_fetch/web_search 搜索）：

**扫描品类清单（优先级排序）：**
1. 健康与健身（Health & Fitness）
2. 效率工具（Productivity）
3. 财务管理（Finance）
4. 教育学习（Education）
5. 生活方式（Lifestyle）
6. 社交（Social）
7. 摄影与视频（Photo & Video）
8. 饮食与营养（Food & Nutrition）

**每个品类搜索：**
```
"{品类} app problems reddit 2025 2026 unsolved"
"best {品类} app ios missing features"
"top grossing {品类} app store revenue"
"{品类} app 差评 知乎 2025"
```

### 1B. 评分标准

对每个发现的机会方向打分：

| 维度 | 1分 | 3分 | 5分 |
|------|-----|-----|-----|
| 市场规模 | 小众 | 中等 | 大众 |
| 竞争激烈度（越低越好）| 巨头垄断 | 有竞争 | 空白市场 |
| 付费意愿 | 免费为主 | 部分付费 | 高付费意愿 |
| 独立开发可行性 | 需要大团队 | 小团队 | 1人可做 |

### 1C. 输出机会地图

格式：
```
# iOS 机会地图

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

## 第三步：对选定方向深度调研

对用户选择的每个方向，依次执行 `ios-market-research` skill 的完整流程：

1. 痛点扫描
2. Exa 竞品研究
3. 用户场景研究
4. 三段式用户洞察（用户画像/痛点/痒点/爽点）
5. 可行性评分矩阵

每个方向报告保存为：
```
/Users/boton/Obsidian/MyKnowledge/IOS Market Research/iOS调研-{方向名}-{YYYY-MM-DD}.md
```

---

## 第四步：横向对比 + 最终决策建议

对比所有调研方向，生成最终决策报告：

```markdown
# iOS 开发方向最终决策报告

## 调研摘要
共调研 X 个方向，历时 X 小时

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

## 时间预算
- MVP 开发：X 周
- 上线目标：YYYY-MM-DD
```

保存到：`/Users/boton/Obsidian/MyKnowledge/IOS Market Research/iOS开发方向决策报告-{YYYY-MM-DD}.md`

---

## 触发词

- 「帮我做 iOS 开发方向调研」
- 「iOS 软件调查」
- 「不知道做什么 App，帮我调研」
- 「帮我找 iOS 开发方向」
- 「用数据决策 iOS 开发方向」
- 「iOS 市场机会扫描」

## 注意事项

- 第一步完成后**必须暂停等待用户选择**，不要自动进入第三步
- 每个方向深度调研需要 1-2 小时，提前告知用户时间
- 所有结论必须基于真实搜索数据，不编造
- 最终报告必须给出明确的「建议做 / 不建议做」结论，不模糊
