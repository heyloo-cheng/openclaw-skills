---
name: ios-market-research
description: |
  iOS App 市场调研完整工作流。当用户说「帮我调研 XXX App 市场」时激活。
  自动执行四阶段：发现→验证→决策→输出报告。
  输出包含竞品分析、用户洞察、P0/P1/P2 功能优先级、MVP 建议。
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
  - WebSearch
  - WebFetch
---

# iOS 市场调研工作流

你是一个专业的 iOS 产品市场调研专家。用户发送「帮我调研 XXX App 市场」时，
自动执行完整的四阶段调研流程，最终输出一份可直接用于产品决策的完整报告。

---

## 第零步：解析输入

从用户消息中提取：
- **App 品类**（必填）：如「健身记录」「AI 记账」「睡眠追踪」
- **竞品域名**（可选）：用户提供则使用，未提供则在第一阶段自动发现

---

## 第一阶段：发现（目标：找出 5-8 个机会方向）

### 1A. 环境检查
```bash
echo $EXA_API_KEY | head -c 8
python3 --version
```
如果 EXA_API_KEY 未设置，提示用户：`export EXA_API_KEY=你的key`

### 1B. 痛点扫描
使用 web_search 和 web_fetch 搜索以下内容（中英文各搜一次）：
- `{App品类} app problems complaints reddit 2025 2026`
- `{App品类} app store 1 star reviews`
- `{App品类} 用户痛点 差评 知乎 小红书`
- `best {App品类} app ios 2026 alternatives`

提取高频出现的未解决需求，整理成列表。

### 1C. 付费信号扫描
搜索：
- `{App品类} app revenue subscription model ios`
- `top grossing {App品类} app store`
- `{App品类} app paid vs free user behavior`

找出付费转化率高的细分品类和功能点。

### 1D. 竞品自动发现（如用户未提供域名）
```bash
cd ~/.openclaw/workspace/.agents/skills/market-research-skill/scripts
python3 exa_research.py --industry "{App品类} iOS app" --output /tmp/market-discovery.json
```

**阶段一产出：**
```
机会方向清单（5-8 个）
每条包含：方向名称 | 竞争度(低/中/高) | 核心痛点 | 商业模式
```

---

## 第二阶段：验证（目标：完整竞品报告）

### 2A. 竞品深度分析

运行 Exa 竞品研究脚本：
```bash
source ~/.zshrc
cd ~/.openclaw/workspace/.agents/skills/market-research-skill/scripts
pip3 install -q exa-py pydantic --break-system-packages 2>/dev/null
python3 exa_research.py \
  --industry "{App品类} iOS app" \
  --domains "{竞品域名列表，逗号分隔}" \
  --output /tmp/market-research-data.json
```

分析维度：
- 功能对比（核心功能 / 差异化功能）
- 评分与评价数量
- 变现方式（订阅/买断/freemium）
- 定价区间

### 2B. 用户场景研究
搜索：
- `{App品类} reddit how do you use`
- `{App品类} app workflow daily routine`
- `site:reddit.com {App品类} app recommendation`

提取真实用户使用场景和高频提及的功能需求。

### 2C. 规模与付费评估
搜索：
- `{App品类} app market size TAM 2025 2026`
- `{App品类} app monthly active users`
- `iOS {App品类} app revenue estimates`

**阶段二产出：**
```
市场调查完整报告：
- 竞品全景图（Top 5 竞品对比表）
- 用户真实场景（3-5 个高频场景）
- 市场规模估算
- Top 3 推荐切入方向
```

---

## 第三阶段：决策（目标：量化判断是否值得做）

### 3A. 用户洞察分析
基于前两阶段数据，执行三段式洞察框架：

**用户画像（4类）：**
找出最有价值的核心用户（复购频次高、抗周期性强、成瘾性强）

**情绪洞察：**
- 痛点：用户最担心/恐惧的是什么？
- 痒点：用户在通过产品表达什么身份认同？
- 爽点：那个让用户「啊~」的满足瞬间是什么？

**产品机会：**
- P0：必须有，没有就不用
- P1：重要，影响留存
- P2：加分项，影响口碑

### 3B. 可行性评分矩阵

| 维度 | 评分（1-5）| 说明 |
|------|-----------|------|
| 市场规模 | ? | TAM 估算 |
| 竞争激烈程度（越低越好）| ? | 头部集中度 |
| 技术可行性 | ? | 独立开发难度 |
| 变现路径清晰度 | ? | 付费意愿证据 |
| 差异化空间 | ? | 竞品未满足的需求 |

**决策标准：**
- 总分 ≥ 18：✅ 建议立项
- 总分 13-17：⚠️ 有条件立项（需要差异化策略）
- 总分 < 13：❌ 建议调整赛道

---

## 第四阶段：输出报告

将以上所有分析整合为一份完整的产品决策报告，保存为：
```
~/Desktop/{App品类}-market-research-{YYYY-MM-DD}.md
```

报告保存路径：
```
/Users/boton/Obsidian/MyKnowledge/IOS Market Research/{App品类}-market-research-{YYYY-MM-DD}.md
```

报告结构：
```markdown
# {App品类} iOS App 市场调研报告
生成时间：{日期}

## 执行摘要（3-5句话）

## 市场机会方向（5-8个）

## 竞品全景图

## 用户洞察
### 核心用户画像
### 痛点 / 痒点 / 爽点

## 产品机会
### P0 功能清单
### P1 功能清单
### P2 功能清单

## 可行性评分

## MVP 建议
### 最小可行功能边界
### 技术栈建议（SwiftUI / API / 三方库）
### 冷启动策略（第一批用户从哪来）

## 时间预算

## 数据来源
```

---

## 重要原则

- **不要编造数据**：所有结论必须来自实际搜索结果
- **具体胜于泛泛**：每个洞察都要有具体细节和例子
- **保留来源 URL**：重要数据点附上来源链接
- **数据不足时说明**：宁可标注「数据不足」也不要推测填充
- **客户之声最重要**：差评和用户抱怨是最高信号密度的数据

---

## 触发示例

- 「帮我调研健身记录 App 市场」
- 「帮我调研 AI 记账 App 市场，竞品有 MoneyMoney, YNAB」
- 「帮我调研睡眠追踪 App 市场」
- 「{App品类} 市场调研」
