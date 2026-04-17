#!/usr/bin/env python3
"""
1688 商品爬取脚本（使用系统反爬虫工具）

使用 OpenClaw 内置的反检测工具：
- playwright-stealth
- Canvas/WebGL/AudioContext 指纹伪造
- 频率控制
- 行为模拟

使用方法：
    python scrapling_1688_advanced.py "迷你加湿器"
"""

import sys
import json
import re
import asyncio
from typing import List, Dict
from pathlib import Path

# 导入 OpenClaw 反爬虫工具
sys.path.insert(0, str(Path.home() / '.openclaw/extensions/shared'))
sys.path.insert(0, str(Path.home() / '.openclaw/extensions/ai-goofish-monitor/src'))

from shared_anti_detection import apply_stealth, get_anti_detection_script
from playwright.async_api import async_playwright


async def scrape_1688_advanced(keyword: str, max_pages: int = 1) -> List[Dict]:
    """使用高级反检测技术爬取 1688"""
    base_url = "https://s.1688.com/selloffer/offer_search.htm"
    products = []
    
    async with async_playwright() as p:
        # 启动浏览器（隐身模式）
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='zh-CN',
        )
        
        page = await context.new_page()
        
        # 应用反检测脚本
        print("🛡️ 应用反检测...")
        await apply_stealth(page)
        await page.add_init_script(get_anti_detection_script())
        
        for page_num in range(1, max_pages + 1):
            print(f"正在爬取第 {page_num} 页...")
            
            url = f"{base_url}?keywords={keyword}&beginPage={page_num}"
            
            try:
                # 访问页面
                await page.goto(url, wait_until='networkidle', timeout=60000)
                
                # 等待内容加载
                await asyncio.sleep(2)
                
                # 获取页面标题
                title = await page.title()
                print(f"  页面标题: {title}")
                
                # 检查是否被重定向到登录页
                current_url = page.url
                if 'login' in current_url.lower():
                    print(f"  ❌ 被重定向到登录页")
                    break
                
                # 提取商品
                items = await page.query_selector_all('[class*="search-offer"]')
                if not items:
                    items = await page.query_selector_all('[class*="offer-item"]')
                
                if not items:
                    print(f"  未找到商品")
                    # 保存 HTML 用于调试
                    html = await page.content()
                    with open(f'/tmp/1688_advanced_{page_num}.html', 'w', encoding='utf-8') as f:
                        f.write(html)
                    print(f"  HTML 已保存到: /tmp/1688_advanced_{page_num}.html")
                    break
                
                print(f"  找到 {len(items)} 个元素")
                
                for item in items[:20]:
                    try:
                        # 提取标题
                        title_elem = await item.query_selector('[class*="title"]')
                        title = await title_elem.inner_text() if title_elem else None
                        
                        if not title:
                            title_elem = await item.query_selector('a')
                            title = await title_elem.get_attribute('title') if title_elem else None
                        
                        # 提取价格
                        price_elem = await item.query_selector('[class*="price"]')
                        price_text = await price_elem.inner_text() if price_elem else None
                        
                        price = None
                        if price_text:
                            match = re.search(r'(\d+\.?\d*)', price_text)
                            if match:
                                price = float(match.group(1))
                        
                        # 提取供应商
                        supplier_elem = await item.query_selector('[class*="company"]')
                        supplier = await supplier_elem.inner_text() if supplier_elem else None
                        
                        # 提取链接
                        link_elem = await item.query_selector('a')
                        link = await link_elem.get_attribute('href') if link_elem else None
                        
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
                print(f"  爬取失败: {e}")
                break
        
        await browser.close()
    
    return products


def main():
    if len(sys.argv) < 2:
        print("用法: python scrapling_1688_advanced.py <关键词>")
        sys.exit(1)
    
    keyword = sys.argv[1]
    
    print(f"🔍 搜索关键词: {keyword}")
    print(f"🛡️ 使用 OpenClaw 反爬虫工具")
    print()
    
    products = asyncio.run(scrape_1688_advanced(keyword, max_pages=1))
    
    if not products:
        print("❌ 未找到任何商品")
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
