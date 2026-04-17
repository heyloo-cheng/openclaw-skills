#!/bin/bash
"""
1688 爬取脚本（使用 agent-browser）

方案 4：使用 OpenClaw agent-browser 控制真实浏览器

优势：
- 真实浏览器环境
- 完整的 JavaScript 支持
- 可以处理登录验证
- 可以截图调试

使用方法：
    bash scrape_1688_browser.sh "迷你加湿器"
"""

KEYWORD="$1"

if [ -z "$KEYWORD" ]; then
    echo "用法: bash scrape_1688_browser.sh <关键词>"
    exit 1
fi

echo "🚀 方案 4：使用 agent-browser 爬取 1688"
echo "=" | tr '=' '=' | head -c 60; echo
echo "关键词: $KEYWORD"
echo

# URL 编码关键词
ENCODED_KEYWORD=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$KEYWORD'))")
SEARCH_URL="https://s.1688.com/selloffer/offer_search.htm?keywords=$ENCODED_KEYWORD"

echo "🌐 打开搜索页面..."
agent-browser open "$SEARCH_URL"

echo "⏳ 等待页面加载..."
agent-browser wait --load networkidle

echo "📸 截图保存..."
agent-browser screenshot --full /tmp/1688_search.png
echo "💾 截图已保存: /tmp/1688_search.png"

echo
echo "📋 获取页面快照..."
agent-browser snapshot -i > /tmp/1688_snapshot.txt
echo "💾 快照已保存: /tmp/1688_snapshot.txt"

echo
echo "🔍 提取商品信息..."
# 使用 agent-browser 提取数据
agent-browser eval "
Array.from(document.querySelectorAll('.offer-item, .search-offer')).slice(0, 10).map(item => ({
  title: item.querySelector('.title, .offer-title')?.textContent?.trim(),
  price: item.querySelector('.price, .offer-price')?.textContent?.trim(),
  supplier: item.querySelector('.company, .supplier-name')?.textContent?.trim(),
  url: item.querySelector('a')?.href
})).filter(item => item.title && item.price)
" > /tmp/1688_products.json

echo "💾 商品数据已保存: /tmp/1688_products.json"

echo
echo "📊 解析结果..."
python3 << 'EOF'
import json
import sys

try:
    with open('/tmp/1688_products.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    if not products:
        print("❌ 未找到商品")
        print("\n💡 可能原因:")
        print("  1. 页面需要登录")
        print("  2. 选择器不正确")
        print("  3. 页面结构已变更")
        print("\n建议:")
        print("  - 查看截图: /tmp/1688_search.png")
        print("  - 查看快照: /tmp/1688_snapshot.txt")
        sys.exit(1)
    
    print(f"✅ 找到 {len(products)} 个商品")
    print("=" * 60)
    
    # 提取价格
    prices = []
    for p in products:
        price_text = p.get('price', '')
        # 提取数字
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

except Exception as e:
    print(f"❌ 解析失败: {e}")
    print("\n💡 建议:")
    print("  - 查看截图: /tmp/1688_search.png")
    print("  - 查看快照: /tmp/1688_snapshot.txt")
    print("  - 查看原始数据: /tmp/1688_products.json")
    sys.exit(1)
EOF

echo
echo "🔧 关闭浏览器..."
agent-browser close

echo
echo "✅ 完成!"
