# Memos Capture Skill

自动捕获 agent 的决策、学习和重要对话到 Memos。

## 触发条件

- 用户说"记住这个"、"保存到 memos"
- Agent 做出重要决策
- 学到新知识或踩坑

## 工作流程

1. 提取关键信息（决策/教训/知识点）
2. 调用 Memos API 创建 memo
3. 打标签（#decision、#lesson、#knowledge）
4. 返回 memo URL

## API 配置

```bash
# 环境变量
export MEMOS_URL="http://localhost:5230"
export MEMOS_TOKEN="your-access-token"
```

## 使用示例

**用户**: "记住：切换 API 供应商时必须更新 3 类文件"

**Agent**: 
1. 提取关键信息
2. 创建 memo：
   ```
   #lesson #openclaw
   切换 API 供应商时必须更新：
   1. openclaw.json (全局配置)
   2. agents/*/models.json (agent 级配置)
   3. agents/*/auth-profiles.json (认证配置)
   ```
3. 返回：✅ 已保存到 Memos: http://localhost:5230/m/123

## 自动捕获规则

- **决策**: 包含"决定"、"选择"、"采用"关键词 → #decision
- **教训**: 包含"坑"、"错误"、"失败"关键词 → #lesson
- **知识**: 包含"发现"、"学到"、"原来"关键词 → #knowledge
- **配置**: 涉及配置文件修改 → #config

## 脚本

```bash
#!/bin/bash
# scripts/memos-create.sh
MEMOS_URL="${MEMOS_URL:-http://localhost:5230}"
MEMOS_TOKEN="${MEMOS_TOKEN}"

curl -X POST "$MEMOS_URL/api/v1/memos" \
  -H "Authorization: Bearer $MEMOS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"content\": \"$1\"}"
```
