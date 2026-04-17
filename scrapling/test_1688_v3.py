#!/usr/bin/env python3
"""测试 1688 页面结构 v3 - 精确定位商品"""

from scrapling.fetchers import StealthyFetcher

url = "https://s.1688.com/selloffer/offer_search.htm?keywords=蓝牙耳机&beginPage=1"

print("正在爬取...")
response = StealthyFetcher.fetch(url, headless=True, timeout=60000)

# 尝试更精确的选择器
selectors = [
    '.search-offer-item',
    '.major-offer',
    '[class*="search-offer"]',
]

for sel in selectors:
    items = response.css(sel)
    print(f"\n选择器: {sel}")
    print(f"找到: {len(items)} 个")
    
    if items and len(items) > 0:
        item = items[0]
        print(f"  Class: {item.attrib.get('class', 'N/A')[:80]}")
        
        # 查看内部结构
        links = item.css('a')
        print(f"  链接数: {len(links)}")
        
        if links:
            link = links[0]
            print(f"  第一个链接 title: {link.attrib.get('title', 'N/A')[:50]}")
            print(f"  第一个链接 href: {link.attrib.get('href', 'N/A')[:80]}")
        
        # 查找价格相关元素
        price_elements = item.css('[class*="price"]')
        print(f"  价格元素数: {len(price_elements)}")
        if price_elements:
            for pe in price_elements[:2]:
                print(f"    价格文本: {pe.css('::text').getall()}")
