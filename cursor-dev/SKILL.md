# Cursor Development Skill

## 描述

自动使用 Cursor MCP 系统执行开发任务。当用户要求"用 Cursor 开发"、"让 Cursor 实现"时，自动创建任务并通过 MCP Bridge 派发给 Cursor IDE。

## 触发词

- "用 Cursor 开发"
- "让 Cursor 实现"
- "Cursor 帮我做"
- "用 Cursor 完成"
- "交给 Cursor"
- "Cursor 来做"

## 工作流程

1. 解析用户需求（任务描述 + 文件列表）
2. 调用 `cursor-task-create.sh` 创建任务
3. 提示用户在 Cursor Agent 中执行
4. 可选：使用 `cursor-mcp-auto.sh` 尝试自动化

## 使用方式

### 方式 1: 简单任务（推荐）

```
用户: 用 Cursor 创建一个 hello.ts 文件

Agent: 
1. 解析需求: 创建 hello.ts 文件
2. 调用: cursor-task-create.sh "创建 hello.ts 文件" '["hello.ts"]'
3. 提示用户在 Cursor 中执行
```

### 方式 2: 复杂任务

```
用户: 让 Cursor 实现用户登录功能

Agent:
1. 解析需求: 实现用户登录功能
2. 推断文件: auth.ts, login.tsx, types.ts
3. 调用: cursor-task-create.sh "实现用户登录功能" '["auth.ts", "login.tsx", "types.ts"]'
4. 提示用户在 Cursor 中执行
```

### 方式 3: 基于文档的任务

```
用户: 用 Cursor 开发 openclaw-improvement-plan.md 中的 Metrics 系统

Agent:
1. 读取文档内容
2. 提取 P0 任务: Metrics 收集系统
3. 生成详细需求
4. 调用: cursor-task-create.sh "实现 Metrics 收集系统..." '["plugins/metrics-collector/..."]'
5. 提示用户在 Cursor 中执行
```

## 实现逻辑

### 步骤 1: 解析用户需求

```typescript
interface TaskRequest {
  description: string;  // 任务描述
  files: string[];      // 涉及的文件
  workdir?: string;     // 工作目录（可选）
}

function parseUserRequest(input: string): TaskRequest {
  // 从用户输入中提取任务描述和文件列表
  // 如果没有明确文件，根据任务类型推断
}
```

### 步骤 2: 创建任务

```bash
# 调用简化脚本（推荐）
cursor-task-create.sh "$description" "$files_json"

# 或使用自动化脚本（可能不稳定）
cursor-mcp-auto.sh "$description" "$files_json"
```

### 步骤 3: 提示用户

```
✅ 任务已创建: task-xxx

🎯 在 Cursor 中执行：
1. 打开 Cursor Agent (Cmd+Shift+L)
2. 输入: 使用 check_pending_tasks 检查待处理任务
3. 输入: 使用 execute_task 执行任务 task-xxx
4. 点击"允许"
5. 完成！
```

## 文件推断规则

根据任务类型自动推断需要的文件：

| 任务类型 | 推断文件 |
|---------|---------|
| 创建组件 | `components/ComponentName.tsx` |
| 实现 API | `api/endpoint.ts`, `types.ts` |
| 添加功能 | `features/feature-name/index.ts` |
| 修复 bug | 从错误信息中提取文件路径 |
| 实现插件 | `plugins/plugin-name/index.ts`, `package.json` |

## 错误处理

### 场景 1: MCP Bridge 未运行

```
❌ MCP Bridge 未运行
启动命令: cd ~/.openclaw/workspace/mcp-servers/openclaw-cursor-bridge && npm start
```

### 场景 2: Cursor 未打开

```
⚠️ Cursor 未运行
正在启动 Cursor...
```

### 场景 3: 任务创建失败

```
❌ 任务创建失败
原因: [错误信息]
建议: [解决方案]
```

## 高级功能

### 批量任务

```
用户: 用 Cursor 实现以下功能：
1. 用户登录
2. 用户注册
3. 密码重置

Agent:
创建 3 个任务:
- task-1: 实现用户登录
- task-2: 实现用户注册
- task-3: 实现密码重置

在 Cursor 中依次执行
```

### 基于文档的任务

```
用户: 用 Cursor 开发 docs/plan.md 中的所有 P0 任务

Agent:
1. 读取 docs/plan.md
2. 提取所有 P0 任务
3. 为每个任务创建 MCP 任务
4. 提示用户在 Cursor 中批量执行
```

## 配置

### 默认工作目录

```bash
DEFAULT_WORKDIR="~/.openclaw/workspace"
```

### 默认文件模式

```yaml
# 根据任务类型选择默认文件
component: ["components/{name}.tsx"]
api: ["api/{name}.ts", "types/{name}.ts"]
plugin: ["plugins/{name}/index.ts", "plugins/{name}/package.json"]
```

## 示例对话

### 示例 1: 简单文件创建

```
用户: 用 Cursor 创建一个 utils.ts 文件

Agent: 
✅ 任务已创建: task-xxx
📋 任务: 创建 utils.ts 文件
📁 文件: utils.ts

🎯 在 Cursor Agent 中执行:
使用 check_pending_tasks 检查待处理任务
使用 execute_task 执行任务 task-xxx
```

### 示例 2: 功能实现

```
用户: 让 Cursor 实现一个 Metrics 收集系统

Agent:
✅ 任务已创建: task-xxx
📋 任务: 实现 Metrics 收集系统
📁 文件: 
  - plugins/metrics-collector/index.ts
  - plugins/metrics-collector/storage.ts
  - plugins/metrics-collector/types.ts
  - plugins/metrics-collector/package.json

🎯 在 Cursor Agent 中执行:
使用 check_pending_tasks 检查待处理任务
使用 execute_task 执行任务 task-xxx
```

### 示例 3: 基于文档

```
用户: 用 Cursor 开发 improvement-plan.md 中的 P0 任务

Agent:
📖 读取文档: improvement-plan.md
🔍 找到 2 个 P0 任务:
  1. Metrics 收集系统
  2. Cron Jobs 修复

✅ 已创建 2 个任务:
  - task-xxx: Metrics 收集系统
  - task-yyy: Cron Jobs 修复

🎯 在 Cursor Agent 中依次执行
```

## 注意事项

1. **MCP Bridge 必须运行**: 确保 `localhost:3000` 可访问
2. **Cursor 必须打开**: 自动化脚本会尝试启动
3. **需要手动确认**: Cursor 的"允许"按钮无法绕过
4. **文件路径**: 相对于工作目录的路径

## 相关文件

- 任务创建脚本: `scripts/cursor-task-create.sh`
- 自动化脚本: `scripts/cursor-mcp-auto.sh`
- 使用指南: `scripts/CURSOR_MCP_BEST_PRACTICE.md`
- MCP Bridge: `mcp-servers/openclaw-cursor-bridge/`

## 版本历史

- v1.0.0 (2026-03-04): 初始版本
  - 支持简单任务创建
  - 支持文件推断
  - 支持批量任务

---

*创建时间: 2026-03-04*
*作者: OpenClaw Team*
