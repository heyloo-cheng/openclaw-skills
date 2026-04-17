#!/usr/bin/env python3
"""
闲鱼商品爬取脚本（基于 Scrapling）

使用方法：
    python scrapling_xianyu.py "手机支架"
    python scrapling_xianyu.py "手机支架" --max-pages 3 --output xianyu.json
"""

import sys
import json
import re
from typing import List, Dict, Optional
from scrapling.fetchers import StealthyFetcher


def scrape_xianyu(keyword: str, max_pages: int = 1) -> List[Dict]:
    """
    爬取闲鱼商品价格
    
    Args:
        keyword: 搜索关键词
        max_pages: 最大页数
        
    Returns:
        商品列表，每个商品包含 title, price, location, url
    """
    base_url = "https://s.2.taobao.com/list/list.htm"
    products = []
    
    for page in range(1, max_pages + 1):
        print(f"正在爬取第 {page} 页...")
        
        # 闲鱼搜索 URL
        url = f"{base_url}?q={keyword}&app=idle&page={page}"
        
        try:
            # 使用隐身模式爬取
            response = StealthyFetcher.fetch(
                url,
                headless=True,
                timeout=30,
                solve_cloudflare=True,  # 可能遇到验证码
                auto_match=True
            )
            
            # 提取商品列表（闲鱼的 DOM 结构可能变化）
            items = response.css('.item, .Card--doubleCardWrapper--', adaptive=True)
            
            if not items:
                # 尝试其他选择器
                items = response.css('[class*="item"], [class*="card"]')
            
            if not items:
                print(f"  未找到商品（可能被反爬虫拦截或需要登录）")
                break
            
            print(f"  找到 {len(items)} 个商品")
            
            for item in items:
                try:
                    # 提取标题
                    title = item.css('.title, .Card--title--::text').get()
                    if not title:
                        title = item.css('[class*="title"]::text').get()
                    
                    # 提取价格
                    price_text = item.css('.price, .Card--price--::text').get()
                    if not price_text:
                        price_text = item.css('[class*="price"]::text').get()
                    
                    # 解析价格
                    price = None
                    if price_text:
                        # 移除 ¥ 符号
                        price_text = price_text.replace('¥', '').replace('元', '').strip()
                        match = re.search(r'(\d+\.?\d*)', price_text)
                        if match:
                            price = float(match.group(1))
                    
                    # 提取地区
                    location = item.css('.location, .Card--location--::text').get()
                    if not location:
                        location = item.css('[class*="location"]::text').get()
                    
                    # 提取链接
                    link = item.css('a::attr(href)').get()
                    
                    if title and price:
                        products.append({
                            'title': title.strip(),
                            'price': price,
                            'location': location.strip() if location else None,
                            'url': link if link and link.startswith('http') else None
                        })
                
                except Exception as e:
                    print(f"  解析商品失败: {e}")
                    continue
        
        except Exception as e:
            print(f"  爬取失败: {e}")
            break
    
    return products


def calculate_stats(products: List[Dict]) -> Dict:
    """计算价格统计"""
    if not products:
        return {}
    
    prices = [p['price'] for p in products]
    prices.sort()
    
    return {
        'count': len(products),
        'min': min(prices),
        'max': max(prices),
        'avg': sum(prices) / len(prices),
        'median': prices[len(prices) // 2],
        'prices': prices
    }


def main():
    if len(sys.argv) < 2:
        print("用法: python scrapling_xianyu.py <关键词> [--max-pages N] [--output FILE]")
        sys.exit(1)
    
    keyword = sys.argv[1]
    max_pages = 1
    output_file = None
    
    # 解析参数
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--max-pages' and i + 1 < len(sys.argv):
            max_pages = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--output' and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    
    print(f"🔍 搜索关键词: {keyword}")
    print(f"📄 最大页数: {max_pages}")
    print()
    
    # 爬取
    products = scrape_xianyu(keyword, max_pages)
    
    if not products:
        print("❌ 未找到任何商品")
        print("💡 提示: 闲鱼可能需要登录或遇到验证码")
        sys.exit(1)
    
    # 统计
    stats = calculate_stats(products)
    
    print()
    print("=" * 60)
    print(f"✅ 找到 {stats['count']} 个商品")
    print(f"💰 价格范围: ¥{stats['min']:.2f} - ¥{stats['max']:.2f}")
    print(f"📊 平均价格: ¥{stats['avg']:.2f}")
    print(f"📈 中位数: ¥{stats['median']:.2f}")
    print("=" * 60)
    
    # 显示前 5 个商品
    print("\n前 5 个商品:")
    for i, p in enumerate(products[:5], 1):
        print(f"{i}. {p['title'][:50]}")
        print(f"   价格: ¥{p['price']:.2f}")
        if p['location']:
            print(f"   地区: {p['location']}")
        print()
    
    # 保存结果
    if output_file:
        result = {
            'keyword': keyword,
            'stats': stats,
            'products': products
        }
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"💾 结果已保存到: {output_file}")
    
    # 返回中位数价格（供其他脚本调用）
    return stats['median']


if __name__ == '__main__':
    main()
