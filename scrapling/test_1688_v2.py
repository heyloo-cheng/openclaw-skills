#!/usr/bin/env python3
"""测试 1688 页面结构 v2"""

from scrapling.fetchers import StealthyFetcher

url = "https://s.1688.com/selloffer/offer_search.htm?keywords=蓝牙耳机&beginPage=1"

print("正在爬取...")
response = StealthyFetcher.fetch(url, headless=True, timeout=60000)

# 找到包含 offer 的元素
items = response.css('[class*="offer"]')
print(f"找到 {len(items)} 个 offer 元素")

# 查看前 3 个元素的结构
for i, item in enumerate(items[:3], 1):
    print(f"\n=== 元素 {i} ===")
    print(f"Class: {item.attrib.get('class', 'N/A')}")
    
    # 尝试提取标题
    title = item.css('[class*="title"]::text').get()
    if not title:
        title = item.css('a::attr(title)').get()
    print(f"标题: {title}")
    
    # 尝试提取价格
    price = item.css('[class*="price"]::text').get()
    print(f"价格: {price}")
    
    # 查看所有文本
    all_text = item.css('::text').getall()
    print(f"所有文本: {[t.strip() for t in all_text if t.strip()][:5]}")
