# Cursor Development Skill

## 🎯 功能

自动将开发任务派发给 Cursor IDE，通过 MCP 协议实现 OpenClaw 和 Cursor 的无缝协作。

## 🚀 使用方式

### 触发词

当用户说以下任何一句话时，自动触发此 skill：

- "用 Cursor 开发..."
- "让 Cursor 实现..."
- "Cursor 帮我做..."
- "用 Cursor 完成..."
- "交给 Cursor..."
- "Cursor 来做..."

### 示例

```
用户: 用 Cursor 创建一个 hello.ts 文件

系统: 
✅ 任务已创建: task-xxx
📋 任务: 创建 hello.ts 文件
📁 文件: hello.ts

🎯 在 Cursor Agent 中执行:
1. 打开 Cursor Agent (Cmd+Shift+L)
2. 输入: 使用 check_pending_tasks 检查待处理任务
3. 输入: 使用 execute_task 执行任务 task-xxx
4. 点击"允许"
5. 完成！
```

## 📋 工作流程

```
用户输入 "用 Cursor 开发 X"
    ↓
Skill 解析需求
    ↓
推断需要的文件
    ↓
创建 MCP 任务
    ↓
提示用户在 Cursor 中执行
    ↓
Cursor 自动完成开发
    ↓
结果反馈到飞书群
```

## 🛠️ 文件推断规则

Skill 会根据任务描述自动推断需要的文件：

| 任务类型 | 推断文件 |
|---------|---------|
| 创建 .ts 文件 | 提取文件名 |
| 实现组件 | `components/Component.tsx` |
| 实现 API | `api/endpoint.ts`, `types.ts` |
| 实现插件 | `plugins/name/index.ts`, `package.json` |
| Metrics 系统 | `plugins/metrics-collector/*` |

## 📁 文件结构

```
skills/cursor-dev/
├── SKILL.md           # Skill 文档
├── README.md          # 使用说明（本文件）
└── execute.sh         # 执行脚本
```

## 🔧 配置

### 前置条件

1. **MCP Bridge 必须运行**:
   ```bash
   cd ~/.openclaw/workspace/mcp-servers/openclaw-cursor-bridge
   npm start
   ```

2. **Cursor 必须配置 MCP**:
   - 配置文件: `~/.cursor/mcp.json`
   - 包含 `openclaw-bridge` 服务器

### 执行模式

Skill 支持两种模式：

#### 模式 1: Simple（推荐，默认）

只创建任务，用户手动在 Cursor 中执行：

```bash
./execute.sh "用 Cursor 创建文件"
```

**优点**: 100% 可靠

#### 模式 2: Auto（实验性）

尝试自动打开 Cursor Agent 并发送命令：

```bash
./execute.sh "用 Cursor 创建文件" auto
```

**优点**: 更自动化
**缺点**: 可能不稳定（Agent 窗口可能关闭）

## 🎓 高级用法

### 批量任务

```bash
# 创建多个任务
./execute.sh "用 Cursor 实现登录功能"
./execute.sh "用 Cursor 实现注册功能"
./execute.sh "用 Cursor 实现密码重置"

# 在 Cursor 中依次执行
```

### 基于文档的任务

```bash
# 从文档中提取任务
./execute.sh "用 Cursor 开发 improvement-plan.md 中的 Metrics 系统"
```

## 📊 示例对话

### 示例 1: 简单文件

```
用户: 用 Cursor 创建一个 utils.ts 文件

Agent: 
[调用 cursor-dev skill]
✅ 任务已创建: task-xxx
📁 文件: utils.ts

🎯 在 Cursor Agent 中执行:
使用 check_pending_tasks 检查待处理任务
使用 execute_task 执行任务 task-xxx
```

### 示例 2: 复杂功能

```
用户: 让 Cursor 实现 Metrics 收集系统

Agent:
[调用 cursor-dev skill]
✅ 任务已创建: task-xxx
📁 文件: 
  - plugins/metrics-collector/index.ts
  - plugins/metrics-collector/storage.ts
  - plugins/metrics-collector/types.ts
  - plugins/metrics-collector/package.json

🎯 在 Cursor Agent 中执行:
使用 check_pending_tasks 检查待处理任务
使用 execute_task 执行任务 task-xxx
```

## 🔍 故障排查

### 问题 1: MCP Bridge 未运行

```
❌ 错误: MCP Bridge 未运行

解决方案:
cd ~/.openclaw/workspace/mcp-servers/openclaw-cursor-bridge
npm start
```

### 问题 2: 任务创建失败

```
❌ 错误: 任务创建失败

检查:
1. MCP Bridge 是否运行 (curl http://localhost:3000/health)
2. 网络连接是否正常
3. 查看 MCP Bridge 日志
```

### 问题 3: Cursor 没有执行

```
⚠️ 任务状态: pending

原因:
- Cursor Agent 没有打开
- 或者没有在 Cursor 中执行命令

解决方案:
1. 打开 Cursor Agent (Cmd+Shift+L)
2. 手动输入命令
```

## 📚 相关文档

- **MCP Bridge**: `mcp-servers/openclaw-cursor-bridge/README.md`
- **最佳实践**: `scripts/CURSOR_MCP_BEST_PRACTICE.md`
- **使用指南**: `scripts/CURSOR_MCP_DELIVERY.md`

## 🎊 总结

**Cursor Development Skill** 让你可以通过自然语言将开发任务派发给 Cursor IDE：

- ✅ 自动解析需求
- ✅ 自动推断文件
- ✅ 自动创建任务
- ✅ 简单可靠（2 条命令）

**使用方式**: 只需说"用 Cursor 开发 X"，剩下的交给系统！

---

*创建时间: 2026-03-04*
*版本: v1.0.0*
