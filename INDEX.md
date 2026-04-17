# OpenClaw Skills 索引

**总数**：62 个技能  
**最后更新**：2026-03-11 09:31

## 📊 分类统计

| 分类 | 数量 | 占比 |
|------|------|------|
| 💻 开发类 | 15 | 24% |
| 🛠️ 工作流类 | 11 | 18% |
| 📈 营销类 | 11 | 18% |
| 🎨 设计类 | 8 | 13% |
| 🤖 AI工具类 | 5 | 8% |
| 📝 文档类 | 4 | 6% |
| 🔍 搜索类 | 3 | 5% |
| 🗄️ 数据库类 | 1 | 2% |
| 🎯 其他 | 4 | 6% |

## 🎨 设计类 (8个)

- `apple-hig` - Apple 人机界面指南
- `canvas-design` - Canvas 设计
- `catering-design` - 餐饮设计
- `frontend-design` - 前端设计
- `mobile-design` - 移动端设计
- `tailwind-design-system` - Tailwind 设计系统
- `ui-ux-pro-max` - UI/UX 专业版
- `web-design-guidelines` - Web 设计指南

## 💻 开发类 (15个)

### iOS/Swift (9个)
- `ios` - iOS 开发
- `ios-simulator` - iOS 模拟器
- `swift` - Swift 语言
- `swift-architecture-skill` - Swift 架构
- `swift-concurrency-expert` - Swift 并发专家
- `swiftui-liquid-glass` - SwiftUI Liquid Glass
- `swiftui-performance-audit` - SwiftUI 性能审计
- `swiftui-ui-patterns` - SwiftUI UI 模式
- `swiftui-view-refactor` - SwiftUI 视图重构
- `xcode` - Xcode 开发

### Web/React (5个)
- `next-best-practices` - Next.js 最佳实践
- `remotion-best-practices` - Remotion 最佳实践
- `vercel-composition-patterns` - Vercel 组合模式
- `vercel-react-best-practices` - Vercel React 最佳实践
- `vercel-react-native-skills` - Vercel React Native

## 🤖 AI工具类 (5个)

- `agent-browser` - 浏览器自动化
- `agent-tools` - AI 工具集（150+ 应用）
- `ai-image-generation` - AI 图像生成
- `cursor-gui` ⭐ - Cursor GUI 模式（2026-03-11 新增）
- `mcp-builder` - MCP 服务器构建

## 📝 文档类 (4个)

- `docx` - Word 文档处理
- `pdf` - PDF 处理
- `pptx` - PowerPoint 处理
- `xlsx` - Excel 处理

## 🔍 搜索类 (3个)

- `brave-search` - Brave 搜索
- `browser-use` - 浏览器使用
- `deep-search` - 深度搜索（Exa → Tavily → Jina）

## 📈 营销类 (11个)

- `content-strategy` - 内容策略
- `copy-editing` - 文案编辑
- `copywriting` - 文案写作
- `larry` - TikTok 应用营销
- `marketing-ideas` - 营销创意
- `marketing-psychology` - 营销心理学
- `page-cro` - 页面转化优化
- `pricing-strategy` - 定价策略
- `product-marketing-context` - 产品营销上下文
- `programmatic-seo` - 程序化 SEO
- `seo-audit` - SEO 审计
- `social-content` - 社交媒体内容

## 🛠️ 工作流类 (11个)

- `brainstorming` - 头脑风暴
- `executing-plans` - 执行计划
- `find-skills` - 查找技能
- `reflection` - 反思
- `requesting-code-review` - 请求代码审查
- `skill-creator` - 技能创建器
- `subagent-driven-development` - 子代理驱动开发
- `systematic-debugging` - 系统化调试
- `test-driven-development` - 测试驱动开发
- `using-superpowers` - 使用超能力
- `webapp-testing` - Web 应用测试
- `writing-plans` - 编写计划

## 🗄️ 数据库类 (1个)

- `supabase-postgres-best-practices` - Supabase Postgres 最佳实践

## 🎯 其他 (4个)

- `apple-developer-toolkit` - Apple 开发工具包
- `markdown-to-html` - Markdown 转 HTML

## ⭐ 最新添加

### cursor-gui (2026-03-11)

**功能**：使用 Cursor GUI 模式执行编程任务

**工作流程**：
```
OpenClaw → Cursor Scheduler → agent -c → Cursor Composer → 完成
```

**文档**：
- `SKILL.md` - 完整使用指南（8.7KB）
- `EXAMPLES.md` - 10 个使用示例（7.1KB）
- `QUICKREF.md` - 快速参考（2.2KB）

**使用**：
```bash
curl -X POST http://localhost:2099/tasks \
  -H "Content-Type: application/json" \
  -d '{"type":"code","payload":{"description":"任务","useGui":true},"workdir":"/path","timeout":600}'
```

## 📊 技能覆盖

### 开发领域
- ✅ iOS/Swift 开发（9 个技能）
- ✅ Web/React 开发（5 个技能）
- ✅ 数据库（1 个技能）

### 设计领域
- ✅ UI/UX 设计（8 个技能）
- ✅ 前端设计
- ✅ 移动端设计

### 营销领域
- ✅ 内容营销（11 个技能）
- ✅ SEO 优化
- ✅ 转化优化

### AI 工具
- ✅ 浏览器自动化
- ✅ 图像生成
- ✅ Cursor 集成 ⭐

### 工作流
- ✅ 计划和执行
- ✅ 测试和调试
- ✅ 代码审查

## 🔗 相关资源

- **Skills 位置**：`~/.openclaw/workspace/.agents/skills/`
- **ClawHub**：https://clawhub.com
- **文档**：https://docs.openclaw.ai

---

**统计时间**：2026-03-11 09:31  
**总技能数**：62 个  
**最新技能**：cursor-gui

## 🔍 Cursor Skills 详细对比

系统中有 **2 个** Cursor 相关的 skills：

### 1. cursor-dev (旧版)
- **位置**：`~/.openclaw/workspace/skills/cursor-dev/`
- **创建**：2026-03-04
- **方式**：MCP Bridge（半自动）
- **特点**：需要在 Cursor Agent 中手动执行

### 2. cursor-gui (新版) ⭐
- **位置**：`~/.openclaw/workspace/.agents/skills/cursor-gui/`
- **创建**：2026-03-11
- **方式**：Cursor Scheduler + GUI（全自动）
- **特点**：自动打开 Cursor Composer，无需手动操作

### 对比表

| 特性 | cursor-dev | cursor-gui ⭐ |
|------|-----------|--------------|
| 自动化 | 半自动 | 全自动 |
| 速度 | 快 | 慢（60-120s） |
| 操作 | 需手动确认 | 无需操作 |
| 适用 | 简单任务 | 复杂任务 |
| 文档 | 基础 | 完整 |

**推荐**：优先使用 `cursor-gui`（新版），更强大和自动化！

