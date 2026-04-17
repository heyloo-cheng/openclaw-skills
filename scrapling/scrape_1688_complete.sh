#!/bin/bash
"""
1688 完整爬取方案（agent-browser + 会话持久化）

步骤：
1. 首次运行：手动登录并保存会话
2. 后续运行：自动使用保存的会话

使用方法：
    # 首次登录（需要手动操作）
    bash scrape_1688_complete.sh login
    
    # 搜索商品（使用保存的会话）
    bash scrape_1688_complete.sh search "迷你加湿器"
"""

ACTION="$1"
KEYWORD="$2"
SESSION_NAME="1688-session"

case "$ACTION" in
    login)
        echo "🔐 首次登录 1688"
        echo "=" | tr '=' '=' | head -c 60; echo
        echo
        echo "步骤："
        echo "  1. 浏览器将打开 1688 登录页"
        echo "  2. 请手动登录"
        echo "  3. 登录成功后，会话将自动保存"
        echo "  4. 按 Ctrl+C 关闭浏览器"
        echo
        read -p "按 Enter 继续..."
        
        # 使用 --headed 显示浏览器窗口
        # 使用 --session-name 自动保存会话
        agent-browser --headed --session-name "$SESSION_NAME" open "https://www.1688.com"
        
        echo
        echo "✅ 会话已保存！"
        echo "现在可以使用: bash scrape_1688_complete.sh search \"关键词\""
        ;;
        
    search)
        if [ -z "$KEYWORD" ]; then
            echo "用法: bash scrape_1688_complete.sh search <关键词>"
            exit 1
        fi
        
        echo "🚀 使用 agent-browser 爬取 1688"
        echo "=" | tr '=' '=' | head -c 60; echo
        echo "关键词: $KEYWORD"
        echo "会话: $SESSION_NAME"
        echo
        
        # URL 编码
        ENCODED_KEYWORD=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$KEYWORD'))")
        SEARCH_URL="https://s.1688.com/selloffer/offer_search.htm?keywords=$ENCODED_KEYWORD"
        
        echo "🌐 打开搜索页面（使用保存的会话）..."
        agent-browser --session-name "$SESSION_NAME" open "$SEARCH_URL"
        
        echo "⏳ 等待页面加载..."
        agent-browser wait --load networkidle
        
        echo "📸 截图..."
        agent-browser screenshot --full /tmp/1688_search.png
        echo "💾 截图: /tmp/1688_search.png"
        
        echo
        echo "📋 获取页面快照..."
        agent-browser snapshot -i > /tmp/1688_snapshot.txt
        
        echo
        echo "🔍 提取商品信息..."
        agent-browser eval "
        Array.from(document.querySelectorAll('.offer-item, .search-offer, [class*=\"offer\"]')).slice(0, 10).map(item => {
          const titleEl = item.querySelector('.title, .offer-title, [class*=\"title\"]');
          const priceEl = item.querySelector('.price, .offer-price, [class*=\"price\"]');
          const companyEl = item.querySelector('.company, .supplier-name, [class*=\"company\"]');
          const linkEl = item.querySelector('a');
          
          return {
            title: titleEl?.textContent?.trim(),
            price: priceEl?.textContent?.trim(),
            supplier: companyEl?.textContent?.trim(),
            url: linkEl?.href
          };
        }).filter(item => item.title && item.price)
        " > /tmp/1688_products.json
        
        echo
        echo "📊 解析结果..."
        python3 << 'EOF'
import json
import sys

try:
    with open('/tmp/1688_products.json', 'r', encoding='utf-8') as f:
        content = f.read().strip()
    
    # 检查是否为空
    if not content or content == 'null':
        print("❌ 未找到商品")
        print("\n💡 可能原因:")
        print("  1. 会话已过期，需要重新登录")
        print("  2. 选择器不正确")
        print("  3. 页面结构已变更")
        print("\n建议:")
        print("  - 查看截图: /tmp/1688_search.png")
        print("  - 查看快照: /tmp/1688_snapshot.txt")
        print("  - 重新登录: bash scrape_1688_complete.sh login")
        sys.exit(1)
    
    products = json.loads(content)
    
    if not products or len(products) == 0:
        print("❌ 未找到商品")
        print("\n💡 可能原因:")
        print("  1. 会话已过期，需要重新登录")
        print("  2. 选择器不正确")
        print("\n建议:")
        print("  - 查看截图: /tmp/1688_search.png")
        print("  - 重新登录: bash scrape_1688_complete.sh login")
        sys.exit(1)
    
    print(f"✅ 找到 {len(products)} 个商品")
    print("=" * 60)
    
    # 提取价格
    prices = []
    for p in products:
        price_text = p.get('price', '')
        import re
        matches = re.findall(r'(\d+\.?\d*)', price_text)
        if matches:
            prices.append(float(matches[0]))
    
    if prices:
        print(f"💰 价格范围: ¥{min(prices):.2f} - ¥{max(prices):.2f}")
        print(f"📊 平均价格: ¥{sum(prices)/len(prices):.2f}")
    
    print("\n前 5 个商品:")
    for i, p in enumerate(products[:5], 1):
        print(f"\n{i}. {p.get('title', 'N/A')[:50]}")
        print(f"   价格: {p.get('price', 'N/A')}")
        if p.get('supplier'):
            print(f"   供应商: {p.get('supplier')[:30]}")
    
    # 保存完整数据
    with open('/tmp/1688_products_full.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print(f"\n💾 完整数据: /tmp/1688_products_full.json")

except Exception as e:
    print(f"❌ 解析失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF
        
        echo
        echo "🔧 关闭浏览器..."
        agent-browser close
        
        echo
        echo "✅ 完成!"
        ;;
        
    *)
        echo "用法:"
        echo "  bash scrape_1688_complete.sh login              # 首次登录"
        echo "  bash scrape_1688_complete.sh search <关键词>    # 搜索商品"
        exit 1
        ;;
esac
