# Logseq Integration Skill

将 agent 的记忆和决策写入 Logseq 知识图谱。

## 配置

```bash
# Logseq 图谱路径（你的笔记目录）
export LOGSEQ_GRAPH_PATH="$HOME/Documents/logseq-graph"
```

## 文件结构

```
logseq-graph/
├── journals/           # 日志（按日期）
│   └── 2026_03_02.md
├── pages/              # 页面（按主题）
│   ├── OpenClaw.md
│   ├── API Providers.md
│   └── Troubleshooting.md
└── logseq/
    └── config.edn
```

## 自动写入规则

### 1. 日志条目（journals/）

每天的对话和决策自动追加到当天的日志：

```markdown
## 21:44 切换 API 供应商
- 问题：飞书群 403 错误
- 根因：旧 API key 失效 + 模型 ID 缺少 provider 前缀
- 解决：更新 3 类配置文件
- 文档：[[docs/switch-api-provider.md]]
- 标签：#troubleshooting #openclaw #feishu
```

### 2. 主题页面（pages/）

重要知识点创建独立页面：

```markdown
# API Providers

## 切换供应商 Checklist
- [ ] 更新 `openclaw.json` 的 `models.providers`
- [ ] 更新所有 agent 的 `models.json`
- [ ] 更新所有 agent 的 `auth-profiles.json`
- [ ] 模型 ID 必须带 `provider/` 前缀
- [ ] 重启 gateway

## 相关文档
- [[docs/switch-api-provider.md]]
- [[scripts/switch-provider.sh]]

## 历史记录
- [[2026_03_02]] 首次切换到 hone.vvvv.ee
```

## 脚本实现

```bash
#!/bin/bash
# scripts/logseq-append.sh
GRAPH_PATH="${LOGSEQ_GRAPH_PATH:-$HOME/Documents/logseq-graph}"
DATE=$(date +%Y_%m_%d)
TIME=$(date +%H:%M)
JOURNAL="$GRAPH_PATH/journals/$DATE.md"

# 创建日志文件（如果不存在）
if [ ! -f "$JOURNAL" ]; then
  echo "---" > "$JOURNAL"
  echo "title: $DATE" >> "$JOURNAL"
  echo "---" >> "$JOURNAL"
  echo "" >> "$JOURNAL"
fi

# 追加条目
cat >> "$JOURNAL" << EOF
## $TIME $1
$2

EOF
```

## 使用示例

### 记录决策
```bash
./scripts/logseq-append.sh "切换 API 供应商" "
- 问题：飞书群 403
- 解决：更新 3 类配置
- 标签：#openclaw #troubleshooting
"
```

### 创建主题页面
```bash
# scripts/logseq-create-page.sh
GRAPH_PATH="${LOGSEQ_GRAPH_PATH:-$HOME/Documents/logseq-graph}"
PAGE_NAME="$1"
CONTENT="$2"
PAGE_FILE="$GRAPH_PATH/pages/${PAGE_NAME// /_}.md"

cat > "$PAGE_FILE" << EOF
# $PAGE_NAME

$CONTENT
EOF
```

## 双向链接

在日志中引用页面会自动创建反向链接：

```markdown
## 21:44 切换 API 供应商
- 参考：[[API Providers]]
- 工具：[[OpenClaw]]
```

Logseq 会在 `API Providers` 页面自动显示所有引用它的日志。

## 图谱可视化

Logseq 内置图谱视图，可以看到：
- 哪些主题被频繁引用
- 知识点之间的关联
- 时间线上的决策演进
