#!/usr/bin/env python3
"""
1688 商品爬取脚本（使用智能代理池）

使用 OpenClaw 内置的智能代理池：
- 自动选择最佳代理
- 自动健康检查
- 自动黑名单管理
- 成本优化

使用方法：
    python scrapling_1688_with_proxy_pool.py "迷你加湿器"
"""

import sys
import json
import re
import asyncio
from typing import List, Dict
from pathlib import Path

# 导入 OpenClaw 智能代理池
sys.path.insert(0, str(Path.home() / '.openclaw/extensions/shared'))

from smart_proxy_pool import SmartProxyPool
from scrapling.fetchers import StealthyFetcher


async def scrape_1688_with_proxy_pool(keyword: str, max_pages: int = 1) -> List[Dict]:
    """使用智能代理池爬取 1688"""
    base_url = "https://s.1688.com/selloffer/offer_search.htm"
    products = []
    
    # 初始化代理池
    print("🚀 初始化智能代理池...")
    proxy_pool = SmartProxyPool(config={
        "providers": ["local"],  # 使用本地代理配置
        "countries": ["cn"],     # 中国代理
        "auto_refresh": False,   # 不自动刷新
    })
    
    await proxy_pool.initialize(countries=["cn"])
    
    if len(proxy_pool.proxies) == 0:
        print("❌ 代理池为空，请配置代理")
        return []
    
    print(f"✅ 代理池初始化完成: {len(proxy_pool.proxies)} 个代理")
    
    for page_num in range(1, max_pages + 1):
        print(f"\n正在爬取第 {page_num} 页...")
        
        # 选择最佳代理（针对 1688/淘宝/天猫）
        proxy_url = proxy_pool.select_proxy(platform="taobao", country="cn")
        
        if not proxy_url:
            print("  ❌ 无可用代理")
            break
        
        print(f"  🔗 使用代理: {proxy_url[:50]}...")
        
        url = f"{base_url}?keywords={keyword}&beginPage={page_num}"
        
        try:
            # 使用代理爬取
            start_time = asyncio.get_event_loop().time()
            
            response = StealthyFetcher.fetch(
                url,
                headless=True,
                timeout=60000,
                proxy=proxy_url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                    'Referer': 'https://www.1688.com/',
                }
            )
            
            latency = (asyncio.get_event_loop().time() - start_time) * 1000
            
            print(f"  ✅ 请求成功 (延迟: {latency:.0f}ms)")
            print(f"  页面标题: {response.css('title::text').get()}")
            
            # 检查是否被重定向
            if 'login' in str(response.url).lower():
                print(f"  ❌ 被重定向到登录页")
                proxy_pool.record_fail(proxy_url, platform="taobao")
                continue
            
            # 记录成功
            proxy_pool.record_success(proxy_url, latency, platform="taobao")
            
            # 提取商品
            items = response.css('[class*="search-offer"]')
            if not items:
                items = response.css('[class*="offer-item"]')
            
            if not items:
                print(f"  未找到商品")
                break
            
            print(f"  找到 {len(items)} 个元素")
            
            for item in items[:20]:
                try:
                    # 提取标题
                    title = item.css('[class*="title"]::text').get()
                    if not title:
                        title = item.css('a::attr(title)').get()
                    
                    # 提取价格
                    price_text = item.css('[class*="price"]::text').get()
                    price = None
                    if price_text:
                        match = re.search(r'(\d+\.?\d*)', price_text)
                        if match:
                            price = float(match.group(1))
                    
                    # 提取供应商
                    supplier = item.css('[class*="company"]::text').get()
                    
                    # 提取链接
                    link = item.css('a::attr(href)').get()
                    
                    if title and price:
                        products.append({
                            'title': title.strip(),
                            'price': price,
                            'supplier': supplier.strip() if supplier else None,
                            'url': link if link and link.startswith('http') else None
                        })
                
                except Exception as e:
                    continue
        
        except Exception as e:
            print(f"  ❌ 爬取失败: {e}")
            proxy_pool.record_fail(proxy_url, platform="taobao")
            continue
    
    # 显示代理池统计
    print("\n" + "=" * 60)
    print("📊 代理池统计:")
    print(f"  总请求: {proxy_pool.stats['total_requests']}")
    print(f"  成功: {proxy_pool.stats['successful_requests']}")
    print(f"  失败: {proxy_pool.stats['failed_requests']}")
    print("=" * 60)
    
    return products


def main():
    if len(sys.argv) < 2:
        print("用法: python scrapling_1688_with_proxy_pool.py <关键词>")
        sys.exit(1)
    
    keyword = sys.argv[1]
    
    print(f"🔍 搜索关键词: {keyword}")
    print(f"🛡️ 使用智能代理池")
    print()
    
    products = asyncio.run(scrape_1688_with_proxy_pool(keyword, max_pages=1))
    
    if not products:
        print("\n❌ 未找到任何商品")
        sys.exit(1)
    
    # 统计
    prices = [p['price'] for p in products]
    prices.sort()
    
    print()
    print("=" * 60)
    print(f"✅ 找到 {len(products)} 个商品")
    print(f"💰 价格范围: ¥{min(prices):.2f} - ¥{max(prices):.2f}")
    print(f"📊 平均价格: ¥{sum(prices)/len(prices):.2f}")
    print("=" * 60)
    
    # 显示前 5 个
    print("\n前 5 个商品:")
    for i, p in enumerate(products[:5], 1):
        print(f"{i}. {p['title'][:50]}")
        print(f"   价格: ¥{p['price']:.2f}")
        if p['supplier']:
            print(f"   供应商: {p['supplier'][:30]}")
        print()


if __name__ == '__main__':
    main()
