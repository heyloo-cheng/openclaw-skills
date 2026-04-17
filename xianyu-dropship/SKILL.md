# 闲鱼无货源自动化系统

自动监控闲鱼、淘宝、拼多多等平台的低价商品，AI 分析后通知你，确认后自动发布到闲鱼。

## 触发词

当用户提到以下关键词时，激活此 Skill：

- 部署闲鱼系统 / 安装闲鱼系统
- 启动闲鱼监控 / 开始监控闲鱼
- 停止闲鱼监控 / 暂停监控
- 闲鱼监控状态 / 闲鱼状态 / 查看状态
- 查看闲鱼日志 / 闲鱼日志
- 添加监控任务 / 新增任务
- 查看待处理商品 / 待处理商品 / 待发布商品

## 功能说明

### 1. 首次部署

**命令：** 部署闲鱼系统

**执行：**
```bash
cd ~/.openclaw/workspace/scripts
bash deploy-dropship-system.sh
```

**流程：**
1. 检查依赖（Python、Node、Redis）
2. 安装 Python 包
3. 配置环境变量
4. 引导用户配置飞书 Webhook
5. 启动所有服务
6. 运行测试
7. 显示状态

### 2. 启动监控

**命令：** 启动闲鱼监控

**执行：**
```bash
cd ~/.openclaw/workspace/scripts
bash manage-dropship.sh start
```

**说明：**
- 启动 Redis
- 启动 ai-goofish-monitor（闲鱼监控）
- 启动 xianyu-agent（商品发布）
- 启动订单监听器
- 显示启动状态

### 3. 停止监控

**命令：** 停止闲鱼监控

**执行：**
```bash
cd ~/.openclaw/workspace/scripts
bash manage-dropship.sh stop
```

### 4. 查看状态

**命令：** 闲鱼监控状态

**执行：**
```bash
cd ~/.openclaw/workspace/scripts
bash manage-dropship.sh status
```

**返回信息：**
- 各服务运行状态
- 待处理商品数量
- 今日统计数据

### 5. 查看日志

**命令：** 查看闲鱼日志

**执行：**
```bash
cd ~/.openclaw/workspace/scripts
bash manage-dropship.sh logs
```

### 6. 测试系统

**命令：** 测试闲鱼系统

**执行：**
```bash
cd ~/.openclaw/workspace/scripts
bash manage-dropship.sh test
```

## 工作流程

```
1. 系统自动监控平台
   ├─ 闲鱼：每 10 分钟
   ├─ 淘宝：每 30 分钟（Browser Relay）
   └─ 拼多多：每 30 分钟（Browser Relay）

2. 发现低价商品
   └─ AI 分析（价值、风险、利润）

3. 飞书通知你
   ├─ 商品详情
   ├─ 价格对比
   └─ 操作指令

4. 你确认发布
   └─ 回复 "发布 product_xxx"

5. 自动发布到闲鱼
   └─ 填充商品信息、计算价格

6. 买家下单
   └─ 飞书通知（包含买家地址）

7. 你去原链接购买
   └─ 填写买家地址

8. 发货
   └─ 回复 "已购买 order_xxx [快递单号]"

9. 自动更新物流
   └─ 买家可查看物流

10. 交易完成
    └─ 赚取差价 ✅
```

## 使用示例

### 首次使用

```
你：部署闲鱼系统

Agent：
开始部署闲鱼无货源自动化系统...

✅ 检查依赖
✅ 安装 Python 包
✅ 配置环境变量

请提供飞书 Webhook URL：
（在飞书群中添加自定义机器人，复制 Webhook URL）

你：https://open.feishu.cn/open-apis/bot/v2/hook/xxx

Agent：
✅ 配置完成
✅ 启动 Redis
✅ 启动 ai-goofish-monitor
✅ 启动 xianyu-agent
✅ 启动订单监听器

🎉 部署完成！系统已启动。

下一步：
1. 访问 http://localhost:8181 配置监控任务
2. 或者说 "添加监控任务 AirPods Pro 2"
```

### 日常使用

```
你：闲鱼监控状态

Agent：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  闲鱼无货源监控系统 - 状态
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 服务状态
├─ Redis: ✅ 运行中
├─ ai-goofish-monitor: ✅ 运行中 (端口 8181)
├─ xianyu-agent: ✅ 运行中 (端口 8080)
└─ 订单监听器: ✅ 运行中

📈 今日统计
├─ 发现商品: 15 个
├─ 发布商品: 3 个
├─ 收到订单: 1 个
└─ 待处理商品: 2 个

⏰ 下次监控: 10:30 (5 分钟后)
```

## 配置说明

### 环境变量

在 `~/.openclaw/workspace/.env` 中配置：

```bash
# 飞书配置
FEISHU_WEBHOOK=https://open.feishu.cn/open-apis/bot/v2/hook/xxx
FEISHU_CHAT_ID=oc_xxxxxxxxxxxxxx

# Redis 配置
REDIS_URL=redis://localhost:6379

# API 配置
XIANYU_API_URL=http://localhost:8080
MONITOR_API_URL=http://localhost:8181

# 利润和风险阈值
MIN_PROFIT_RATE=0.3
MAX_RISK_SCORE=0.3
```

### 监控任务配置

访问 http://localhost:8181 或编辑配置文件添加监控任务。

## 注意事项

### 1. 运行时间

- 只在工作时间运行（9:00-22:00）
- 避免深夜运行
- 模拟真人使用习惯

### 2. 频率控制

- 闲鱼：每 10 分钟
- 淘宝/拼多多：每 30 分钟
- 不要太频繁

### 3. 账号安全

- 使用小号测试
- 不要在同一 IP 运行多个账号
- 定期更换代理

### 4. 数据安全

- 不要在日志中记录敏感信息
- 定期备份配置文件
- 使用环境变量存储密钥

## 故障排查

### 问题 1：服务启动失败

**检查：**
```bash
# 查看日志
bash manage-dropship.sh logs

# 检查端口占用
lsof -i :8080
lsof -i :8181
```

### 问题 2：飞书收不到通知

**检查：**
```bash
# 测试 Webhook
curl -X POST $FEISHU_WEBHOOK \
  -H "Content-Type: application/json" \
  -d '{"msg_type":"text","content":{"text":"测试消息"}}'
```

### 问题 3：Redis 连接失败

**解决：**
```bash
# 启动 Redis
brew services start redis

# 测试连接
redis-cli ping
```

## 相关文档

- 快速开始：`docs/xianyu-dropship-quickstart.md`
- 配置指南：`docs/xianyu-dropship-config-guide.md`
- Browser Relay 指南：`docs/browser-relay-monitor-guide.md`
- 反检测增强：`docs/playwright-anti-detection-enhancement.md`

## 技术栈

- Python 3.8+
- Node.js 16+
- Redis
- OpenClaw
- Playwright / Browser Relay
- 飞书 API

## 更新日志

- 2026-03-12: 初始版本
  - 基础监控功能
  - 飞书通知
  - 自动发布
  - 订单处理

---

**开发者：** OpenClaw Agent  
**版本：** 1.0.0  
**最后更新：** 2026-03-12
