#!/bin/bash
# Cursor Development Skill - 实现脚本
# 当用户说"用 Cursor 开发"时自动调用

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$SCRIPT_DIR/../.."
CURSOR_TASK_CREATE="$WORKSPACE_ROOT/scripts/cursor-task-create.sh"
CURSOR_MCP_AUTO="$WORKSPACE_ROOT/scripts/cursor-mcp-auto.sh"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

# 解析用户需求
parse_request() {
    local input="$1"
    
    # 提取任务描述（去掉触发词）
    local description=$(echo "$input" | sed -E 's/(用|让|交给|帮我) *Cursor *(开发|实现|做|完成|来做) *//g')
    
    echo "$description"
}

# 推断文件列表
infer_files() {
    local description="$1"
    
    # 简单的文件推断逻辑
    if echo "$description" | grep -qi "创建.*\.ts"; then
        # 提取文件名
        local filename=$(echo "$description" | grep -oE '[a-zA-Z0-9_-]+\.ts' | head -1)
        echo "[\"$filename\"]"
    elif echo "$description" | grep -qi "组件"; then
        echo "[\"components/Component.tsx\"]"
    elif echo "$description" | grep -qi "API"; then
        echo "[\"api/endpoint.ts\", \"types.ts\"]"
    elif echo "$description" | grep -qi "插件"; then
        echo "[\"plugins/plugin-name/index.ts\", \"plugins/plugin-name/package.json\"]"
    elif echo "$description" | grep -qi "Metrics"; then
        echo "[\"plugins/metrics-collector/index.ts\", \"plugins/metrics-collector/storage.ts\", \"plugins/metrics-collector/types.ts\", \"plugins/metrics-collector/package.json\"]"
    else
        # 默认
        echo "[\"index.ts\"]"
    fi
}

# 主函数
main() {
    local user_input="${1:-}"
    local mode="${2:-simple}"  # simple 或 auto
    
    if [ -z "$user_input" ]; then
        cat <<EOF
用法: $0 <user_input> [mode]

示例:
  $0 "用 Cursor 创建一个 hello.ts 文件"
  $0 "让 Cursor 实现 Metrics 系统" auto

参数:
  user_input  用户输入（包含触发词）
  mode        执行模式（simple: 只创建任务, auto: 尝试自动化）
EOF
        exit 1
    fi
    
    log "========================================="
    log "Cursor Development Skill"
    log "========================================="
    
    # 解析需求
    local description=$(parse_request "$user_input")
    log "📋 任务描述: $description"
    
    # 推断文件
    local files=$(infer_files "$description")
    log "📁 推断文件: $files"
    
    # 创建任务
    if [ "$mode" = "auto" ]; then
        log "🚀 使用自动化模式..."
        "$CURSOR_MCP_AUTO" "$description" "$files"
    else
        log "📝 使用简单模式（推荐）..."
        "$CURSOR_TASK_CREATE" "$description" "$files"
    fi
}

main "$@"
