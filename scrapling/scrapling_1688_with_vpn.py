#!/usr/bin/env python3
"""
1688 商品爬取脚本（使用 VPN 节点）

使用 Shadowsocks 代理节点爬取 1688
支持自动节点轮换

使用方法：
    python scrapling_1688_with_vpn.py "迷你加湿器"
"""

import sys
import json
import re
import time
from typing import List, Dict
from pathlib import Path

# 导入 VPN 节点配置
sys.path.insert(0, str(Path(__file__).parent))
from vpn_nodes import AVAILABLE_NODES, get_node_by_country

from scrapling.fetchers import StealthyFetcher


def scrape_1688_with_vpn(keyword: str, max_pages: int = 1) -> List[Dict]:
    """使用 VPN 节点爬取 1688"""
    base_url = "https://s.1688.com/selloffer/offer_search.htm"
    products = []
    
    print(f"🌐 可用 VPN 节点: {len(AVAILABLE_NODES)} 个")
    
    # 选择节点（优先使用香港/台湾节点，距离近延迟低）
    node = get_node_by_country('hk')
    print(f"🔗 使用节点: {node['name']}")
    print(f"   服务器: {node['server']}:{node['port']}")
    
    # 构建代理 URL
    # Shadowsocks 代理格式：socks5://server:port
    proxy_url = f"socks5://{node['server']}:{node['port']}"
    
    for page_num in range(1, max_pages + 1):
        print(f"\n正在爬取第 {page_num} 页...")
        
        url = f"{base_url}?keywords={keyword}&beginPage={page_num}"
        
        try:
            start_time = time.time()
            
            # 使用 VPN 代理爬取
            response = StealthyFetcher.fetch(
                url,
                headless=True,
                timeout=60000,
                proxy=proxy_url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                    'Referer': 'https://www.1688.com/',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                }
            )
            
            latency = (time.time() - start_time) * 1000
            
            print(f"  ✅ 请求成功 (延迟: {latency:.0f}ms)")
            
            # 获取页面标题
            title = response.css('title::text').get()
            print(f"  页面标题: {title}")
            
            # 检查是否被重定向
            if 'login' in str(response.url).lower():
                print(f"  ❌ 被重定向到登录页")
                print(f"  提示: 尝试切换其他节点")
                break
            
            # 提取商品
            items = response.css('[class*="search-offer"]')
            if not items:
                items = response.css('[class*="offer-item"]')
            
            if not items:
                print(f"  未找到商品")
                # 保存 HTML 用于调试
                html = str(response)
                with open(f'/tmp/1688_vpn_{page_num}.html', 'w', encoding='utf-8') as f:
                    f.write(html)
                print(f"  HTML 已保存到: /tmp/1688_vpn_{page_num}.html")
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
            print(f"  提示: 检查 VPN 节点是否可用")
            break
    
    return products


def main():
    if len(sys.argv) < 2:
        print("用法: python scrapling_1688_with_vpn.py <关键词>")
        print("\n可用 VPN 节点:")
        for i, node in enumerate(AVAILABLE_NODES, 1):
            print(f"  {i}. {node['name']} ({node['country']})")
        sys.exit(1)
    
    keyword = sys.argv[1]
    
    print(f"🔍 搜索关键词: {keyword}")
    print(f"🌐 使用 VPN 节点")
    print()
    
    products = scrape_1688_with_vpn(keyword, max_pages=1)
    
    if not products:
        print("\n❌ 未找到任何商品")
        print("\n💡 建议:")
        print("  1. 检查 VPN 节点是否可用")
        print("  2. 尝试切换其他节点（修改 vpn_nodes.py）")
        print("  3. 或继续使用 Deep Search 方案")
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
