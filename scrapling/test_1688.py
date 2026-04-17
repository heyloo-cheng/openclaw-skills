#!/usr/bin/env python3
"""测试 1688 页面结构"""

from scrapling.fetchers import StealthyFetcher

url = "https://s.1688.com/selloffer/offer_search.htm?keywords=蓝牙耳机&beginPage=1"

print("正在爬取...")
response = StealthyFetcher.fetch(url, headless=True, timeout=60000)

print(f"状态码: {response.status}")
print(f"页面标题: {response.css('title::text').get()}")
print()

# 尝试不同的选择器
selectors = [
    '.offer-item',
    '.sw-offer-item',
    '[class*="offer"]',
    '[class*="item"]',
    '.card',
    '[data-spm]',
]

for sel in selectors:
    items = response.css(sel)
    if items:
        print(f"✅ 找到 {len(items)} 个元素: {sel}")
    else:
        print(f"❌ 未找到: {sel}")

# 保存 HTML 用于调试
with open('/tmp/1688_debug.html', 'w', encoding='utf-8') as f:
    f.write(response.html)
print("\n💾 HTML 已保存到: /tmp/1688_debug.html")
