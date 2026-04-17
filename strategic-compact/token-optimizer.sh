#!/bin/bash
# OpenClaw Token 优化器
# 监控 token 使用情况并提供优化建议

set -e

# 配置
SESSION_ID="${CLAUDE_SESSION_ID:-${PPID:-default}}"
TOKEN_FILE="/tmp/claude-token-stats-${SESSION_ID}"
THRESHOLD="${TOKEN_THRESHOLD:-50000}"
WARNING_THRESHOLD="${TOKEN_WARNING_THRESHOLD:-80000}"

# 统计文件
STATS_DIR="${TOKEN_STATS_DIR:-$HOME/.claude/token-stats}"
mkdir -p "$STATS_DIR"

# 初始化或更新统计
init_stats() {
    if [ ! -f "$TOKEN_FILE" ]; then
        echo "{\"tool_calls\":0,\"reads\":0,\"edits\":0,\"writes\":0,\"searches\":0,\"session_start\":\"$(date -Iseconds)\"}" > "$TOKEN_FILE"
    fi
}

# 更新统计
update_stats() {
    local tool="$1"
    local current=$(cat "$TOKEN_FILE")
    
    case "$tool" in
        Read)
            new_reads=$(echo "$current" | grep -o '"reads":[0-9]*' | grep -o '[0-9]*')
            new_reads=$((new_reads + 1))
            current=$(echo "$current" | sed "s/\"reads\":[0-9]*/\"reads\":$new_reads/")
            ;;
        Edit)
            new_edits=$(echo "$current" | grep -o '"edits":[0-9]*' | grep -o '[0-9]*')
            new_edits=$((new_edits + 1))
            current=$(echo "$current" | sed "s/\"edits\":[0-9]*/\"edits\":$new_edits/")
            ;;
        Write)
            new_writes=$(echo "$current" | grep -o '"writes":[0-9]*' | grep -o '[0-9]*')
            new_writes=$((new_writes + 1))
            current=$(echo "$current" | sed "s/\"writes\":[0-9]*/\"writes\":$new_writes/")
            ;;
        Grep|Search)
            new_searches=$(echo "$current" | grep -o '"searches":[0-9]*' | grep -o '[0-9]*')
            new_searches=$((new_searches + 1))
            current=$(echo "$current" | sed "s/\"searches\":[0-9]*/\"searches\":$new_searches/")
            ;;
    esac
    
    # 更新总工具调用数
    new_count=$(echo "$current" | grep -o '"tool_calls":[0-9]*' | grep -o '[0-9]*')
    new_count=$((new_count + 1))
    current=$(echo "$current" | sed "s/\"tool_calls\":[0-9]*/\"tool_calls\":$new_count/")
    
    echo "$current" > "$TOKEN_FILE"
}

# 获取统计
get_stats() {
    if [ -f "$TOKEN_FILE" ]; then
        cat "$TOKEN_FILE"
    else
        echo "{\"tool_calls\":0,\"reads\":0,\"edits\":0,\"writes\":0,\"searches\":0,\"session_start\":\"unknown\"}"
    fi
}

# 估算 token 使用量（粗略估算）
estimate_tokens() {
    local stats="$1"
    local tool_calls=$(echo "$stats" | grep -o '"tool_calls":[0-9]*' | grep -o '[0-9]*')
    
    # 每个工具调用平均约 500 tokens（包括输入和输出）
    local estimated=$((tool_calls * 500))
    echo "$estimated"
}

# 建议优化
suggest_optimization() {
    local stats="$1"
    local estimated_tokens="$2"
    
    local tool_calls=$(echo "$stats" | grep -o '"tool_calls":[0-9]*' | grep -o '[0-9]*')
    local reads=$(echo "$stats" | grep -o '"reads":[0-9]*' | grep -o '[0-9]*')
    local edits=$(echo "$stats" | grep -o '"edits":[0-9]*' | grep -o '[0-9]*')
    local writes=$(echo "$stats" | grep -o '"writes":[0-9]*' | grep -o '[0-9]*')
    local searches=$(echo "$stats" | grep -o '"searches":[0-9]*' | grep -o '[0-9]*')
    
    echo "📊 Token 使用统计"
    echo "================="
    echo "  工具调用: $tool_calls"
    echo "  读取操作: $reads"
    echo "  编辑操作: $edits"
    echo "  写入操作: $writes"
    echo "  搜索操作: $searches"
    echo ""
    echo "  估算 token: ~$estimated_tokens"
    echo ""
    
    # 根据工具使用模式给出建议
    if [ "$estimated_tokens" -gt "$WARNING_THRESHOLD" ]; then
        echo "⚠️  警告: 上下文即将耗尽，建议立即压缩!"
        echo ""
        echo "建议操作:"
        echo "  1. /compact 保存当前进度"
        echo "  2. 将会话状态保存到文件"
        echo "  3. 清理不必要的读取缓存"
    elif [ "$estimated_tokens" -gt "$THRESHOLD" ]; then
        echo "💡 建议: 考虑压缩以优化性能"
        echo ""
        echo "可选操作:"
        echo "  1. /compact 进入下一阶段"
        echo "  2. 保存重要状态到文件"
    else
        echo "✅ 状态正常: 继续当前工作"
    fi
    
    # 给出具体的优化建议
    echo ""
    echo "📝 优化建议:"
    
    # 如果读取过多
    if [ "$reads" -gt 50 ]; then
        echo "  • 读取操作较多: 考虑使用 Grep 替代 Read 来定位内容"
    fi
    
    # 如果搜索过多
    if [ "$searches" -gt 30 ]; then
        echo "  • 搜索操作较多: 使用更精确的搜索模式减少结果"
    fi
    
    # 如果编辑过多
    if [ "$edits" -gt 20 ]; then
        echo "  • 编辑操作较多: 考虑批量修改而非零散编辑"
    fi
    
    # 如果写入过少（可能需要保存进度）
    if [ "$writes" -lt 3 ] && [ "$tool_calls" -gt 30 ]; then
        echo "  • 建议定期保存进度到文件，避免丢失"
    fi
}

# 主逻辑
main() {
    local command="$1"
    
    init_stats
    
    case "$command" in
        stats)
            # 显示统计
            stats=$(get_stats)
            estimated=$(estimate_tokens "$stats")
            echo "$stats" | python3 -m json.tool 2>/dev/null || echo "$stats"
            echo ""
            echo "估算 token: ~$estimated"
            ;;
        suggest)
            # 建议优化
            stats=$(get_stats)
            estimated=$(estimate_tokens "$stats")
            suggest_optimization "$stats" "$estimated"
            ;;
        ""|track)
            # 更新统计（默认）
            tool="$2"
            if [ -n "$tool" ]; then
                update_stats "$tool"
            fi
            ;;
        reset)
            # 重置统计
            rm -f "$TOKEN_FILE"
            echo "✅ 统计已重置"
            ;;
        *)
            echo "OpenClaw Token Optimizer"
            echo "======================="
            echo ""
            echo "用法:"
            echo "  token-optimizer.sh           # 跟踪工具调用（默认）"
            echo "  token-optimizer.sh stats     # 显示统计"
            echo "  token-optimizer.sh suggest  # 获取优化建议"
            echo "  token-optimizer.sh reset    # 重置统计"
            echo ""
            echo "环境变量:"
            echo "  TOKEN_THRESHOLD            # 建议压缩的阈值（默认: 50000）"
            echo "  TOKEN_WARNING_THRESHOLD    # 警告阈值（默认: 80000）"
            ;;
    esac
}

main "$@"
