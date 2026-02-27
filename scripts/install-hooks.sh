#!/bin/bash
# install-hooks.sh — 安装 git hooks 到指定项目
# Usage: bash install-hooks.sh [project-dir]
# 不指定则安装到所有已知项目

HOOKS_DIR="$HOME/.openclaw/workspace/scripts/hooks"
PROJECTS=(
  "$HOME/Developer/ToolBox"
  "$HOME/Developer/ClipMind"
  "$HOME/Developer/VaultMind"
  "$HOME/.openclaw/workspace/skills"
)

install_hooks() {
  local proj="$1"
  if [ ! -d "$proj/.git" ]; then
    echo "⏭️  $proj — 不是 git 仓库，跳过"
    return
  fi
  
  local hooks_target="$proj/.git/hooks"
  mkdir -p "$hooks_target"
  
  for hook in "$HOOKS_DIR"/*; do
    [ -f "$hook" ] || continue
    local name=$(basename "$hook")
    cp "$hook" "$hooks_target/$name"
    chmod +x "$hooks_target/$name"
    echo "✅ $proj — 安装 $name"
  done
}

if [ -n "$1" ]; then
  install_hooks "$1"
else
  for proj in "${PROJECTS[@]}"; do
    install_hooks "$proj"
  done
fi

echo ""
echo "Done. Hooks installed from: $HOOKS_DIR"
