#!/bin/bash
# skill-watcher.sh — 监控 skills/ 目录变化，自动触发注册
# Usage: nohup bash skill-watcher.sh &
# 依赖 fswatch: brew install fswatch

SKILLS_DIR="$HOME/.openclaw/workspace/skills"
REGISTER_SCRIPT="$HOME/.openclaw/workspace/scripts/skill-register.py"
LAST_RUN=0
COOLDOWN=10  # 秒，防止频繁触发

echo "[skill-watcher] Watching $SKILLS_DIR for changes..."

fswatch -r -e ".*" -i "SKILL\\.md$" "$SKILLS_DIR" | while read -r changed_file; do
  NOW=$(date +%s)
  DIFF=$((NOW - LAST_RUN))
  
  if [ "$DIFF" -lt "$COOLDOWN" ]; then
    continue
  fi
  LAST_RUN=$NOW
  
  SKILL_NAME=$(basename "$(dirname "$changed_file")")
  echo ""
  echo "[skill-watcher] $(date '+%Y-%m-%d %H:%M:%S') 检测到变更: $SKILL_NAME"
  
  # 1. 基础验证
  if ! head -1 "$changed_file" | grep -q "^---"; then
    echo "  ⚠️  $SKILL_NAME — 缺少 frontmatter"
  else
    echo "  ✅ $SKILL_NAME — frontmatter 存在"
  fi
  
  # 2. 检查 triggers
  if ! python3 -c "
import json
t = json.load(open('$HOME/.openclaw/workspace/data/skill-triggers.json'))
if '$SKILL_NAME' not in t:
    print('  ⚠️  $SKILL_NAME — 未定义 triggers，请添加到 skill-triggers.json')
    exit(1)
else:
    print('  ✅ $SKILL_NAME — triggers 已定义 (' + str(len(t['$SKILL_NAME'].get('triggers',[]))) + ' 个)')
" 2>/dev/null; then
    true  # warning already printed
  fi
  
  # 3. 重新注册
  echo "  🔄 更新 registry..."
  python3 "$REGISTER_SCRIPT" 2>&1 | tail -1
  
  # 4. 自动 git commit (版本管理)
  cd "$SKILLS_DIR"
  if git diff --quiet "$changed_file" 2>/dev/null; then
    echo "  ℹ️  无实际变更"
  else
    git add "$changed_file"
    git commit -m "auto: update $SKILL_NAME SKILL.md" --no-verify 2>/dev/null
    echo "  📦 已自动提交版本"
  fi
  
  echo "[skill-watcher] Done."
done
