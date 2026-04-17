#!/usr/bin/env python3
"""
1688 爬取脚本（使用 proxy_pool + Cookie）

基于 GitHub 发现的最佳实践：
- jhao104/proxy_pool 提供代理
- Cookie 认证
- 自动代理轮换

使用方法：
    1. 启动 proxy_pool: python proxyPool.py server
    2. 配置 Cookie（从浏览器复制）
    3. 运行: python scrapling_1688_final.py "迷你加湿器"
"""

import sys
import json
import re
import time
import requests
from typing import List, Dict, Optional
from scrapling.fetchers import StealthyFetcher

# 配置
PROXY_POOL_URL = "http://127.0.0.1:5010"  # proxy_pool API 地址
COOKIE = ""  # 从浏览器复制的 Cookie（需要用户提供）


def get_proxy_from_pool() -> Optional[str]:
    """从代理池获取代理"""
    try:
        response = requests.get(f"{PROXY_POOL_URL}/get/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            proxy = data.get("proxy")
            if proxy:
                return f"http://{proxy}"
    except Exception as e:
        print(f"  ⚠️ 获取代理失败: {e}")
    return None


def delete_proxy_from_pool(proxy: str):
    """从代理池删除失效代理"""
    try:
        # 移除 http:// 前缀
        proxy = proxy.replace("http://", "").replace("https://", "")
        requests.get(f"{PROXY_POOL_URL}/delete/?proxy={proxy}", timeout=5)
        print(f"  🗑️ 已删除失效代理: {proxy}")
    except Exception:
        pass


def scrape_1688_final(keyword: str, max_pages: int = 1, use_cookie: bool = True) -> List[Dict]:
    """使用 proxy_pool + Cookie 爬取 1688"""
    base_url = "https://s.1688.com/selloffer/offer_search.htm"
    products = []
    
    # 检查代理池是否可用
    try:
        response = requests.get(f"{PROXY_POOL_URL}/count", timeout=5)
        if response.status_code == 200:
            count = response.json().get("count", 0)
            print(f"🌐 代理池可用代理数: {count}")
            if count == 0:
                print("⚠️ 代理池为空，请先启动 proxy_pool 并等待代理采集")
                return []
        else:
            print("❌ 代理池未启动，请先运行: python proxyPool.py server")
            return []
    except Exception as e:
        print(f"❌ 无法连接到代理池: {e}")
        print("提示: 请先启动 proxy_pool")
        return []
    
    for page_num in range(1, max_pages + 1):
        print(f"\n正在爬取第 {page_num} 页...")
        
        # 获取代理
        proxy = get_proxy_from_pool()
        if not proxy:
            print("  ❌ 无可用代理")
            break
        
        print(f"  🔗 使用代理: {proxy}")
        
        url = f"{base_url}?keywords={keyword}&beginPage={page_num}"
        
        # 构建请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Referer': 'https://www.1688.com/',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        
        # 如果提供了 Cookie，添加到请求头
        if use_cookie and COOKIE:
            headers['Cookie'] = COOKIE
            print(f"  🔐 使用 Cookie 认证")
        
        try:
            start_time = time.time()
            
            # 使用代理 + Cookie 爬取
            response = StealthyFetcher.fetch(
                url,
                headless=True,
                timeout=60000,
                proxy=proxy,
                headers=headers
            )
            
            latency = (time.time() - start_time) * 1000
            
            print(f"  ✅ 请求成功 (延迟: {latency:.0f}ms)")
            
            # 获取页面标题
            title = response.css('title::text').get()
            print(f"  页面标题: {title}")
            
            # 检查是否被重定向
            if 'login' in str(response.url).lower():
                print(f"  ❌ 被重定向到登录页")
                print(f"  提示: Cookie 可能已过期，请重新获取")
                delete_proxy_from_pool(proxy)
                break
            
            # 提取商品
            items = response.css('[class*="search-offer"]')
            if not items:
                items = response.css('[class*="offer-item"]')
            
            if not items:
                print(f"  未找到商品")
                # 保存 HTML 用于调试
                html = str(response)
                with open(f'/tmp/1688_final_{page_num}.html', 'w', encoding='utf-8') as f:
                    f.write(html)
                print(f"  HTML 已保存到: /tmp/1688_final_{page_num}.html")
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
            delete_proxy_from_pool(proxy)
            continue
    
    return products


def main():
    if len(sys.argv) < 2:
        print("用法: python scrapling_1688_final.py <关键词>")
        print("\n配置说明:")
        print("  1. 启动 proxy_pool:")
        print("     cd ~/.openclaw/workspace/proxy_pool")
        print("     python proxyPool.py server")
        print("\n  2. 配置 Cookie（可选，但强烈推荐）:")
        print("     编辑本文件，设置 COOKIE 变量")
        print("\n  3. 运行爬虫:")
        print("     python scrapling_1688_final.py '迷你加湿器'")
        sys.exit(1)
    
    keyword = sys.argv[1]
    
    print(f"🔍 搜索关键词: {keyword}")
    print(f"🌐 使用 proxy_pool + Cookie")
    print()
    
    # 检查 Cookie 配置
    if not COOKIE:
        print("⚠️ 未配置 Cookie，成功率可能较低")
        print("建议: 从浏览器复制 Cookie 并配置到脚本中")
        print()
    
    products = scrape_1688_final(keyword, max_pages=1, use_cookie=bool(COOKIE))
    
    if not products:
        print("\n❌ 未找到任何商品")
        print("\n💡 故障排查:")
        print("  1. 检查 proxy_pool 是否运行: curl http://127.0.0.1:5010/count")
        print("  2. 检查代理池是否有代理: curl http://127.0.0.1:5010/all")
        print("  3. 检查 Cookie 是否有效（从浏览器重新获取）")
        print("  4. 或继续使用 Deep Search 方案")
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
