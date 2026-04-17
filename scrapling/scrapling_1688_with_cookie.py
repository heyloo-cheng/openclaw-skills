#!/usr/bin/env python3
"""
1688 商品爬取脚本（使用 Cookie 认证）

使用方法：
    python scrapling_1688_with_cookie.py "蓝牙耳机"
"""

import sys
import json
import re
from typing import List, Dict
from scrapling.fetchers import StealthyFetcher

# 1688 Cookie（从浏览器复制）
COOKIE = "leftMenuLastMode=COLLAPSE; mtop_partitioned_detect=1; _m_h5_tk=37baa87b0f8d29e04572bbf3a755dd2c_1776160435088; _m_h5_tk_enc=c26b596fa2d060b0da0ecb781f499166; xlly_s=1; leftMenuModeTip=shown; plugin_home_downLoad_cookie=%E4%B8%8B%E8%BD%BD%E6%8F%92%E4%BB%B6; t=87f1c4553d6a1cea12a9b990650392a2; _tb_token_=ee71376e6ef71; sg=%E8%AF%9A60; lid=yyc%E5%AE%87%E8%AF%9A; unb=2445313076; _nk_=yyc%5Cu5B87%5Cu8BDA; _csrf_token=1776150388241; __cn_logon__=true; __cn_logon_id__=yyc%E5%AE%87%E8%AF%9A; __last_loginid__=b2b-2445313076; __last_memberid__=b2b-2445313076; last_mid=b2b-2445313076; _user_vitals_session_data_={\"user_line_track\":true,\"ul_session_id\":\"026efffynrog\",\"last_page_id\":\"www.1688.com%2Fwc6ssb3mlyq\"}; yyc%E5%AE%87%E8%AF%9A_floatBotNotHit=1; isg=BLCw78JerW6BuHFqvaL5G49BgXgC-ZRDziUIgaoBfIveZVAPUglk0wbHv20Fbkwb; tfstk=gHKnIDqu71NXGtVZm7SIWDCX4IgOOMs5oQERwgCr715_9WEpUGzNd97yvMppsJtMiuEKO29zqgIrMjnxDpgCVglvJUNdRJ6Rn_yUwwSN7gBl5J-Imp9CVRay5puMd04TGsqFU_kGbTWVLg7U4lzN1TUFaQ5F75Wchg5yaQyZbt64TyWPT5kGF15P4gRyQAXR__SP4QJZsRZPi3-6bju73FPkS4-NKwf2L6Jpph50MsvFsurPt9bHWp5g4u-Mzor5Osmg_1pyhU7MqcE1VdLDZURZUu5k7tAcHBnaxg8wsnb2CjqCtFRBqMQjq8XModRHvdD8SQAwhEseYbZdOUJw41KEeuf2kKsGC3h_Y_YwzHQCVWlhIHvDqUjz9Pzqfjr5QYKaPz_FCOfYmOX5tN8QiiMiIrgC8O6KMADgP8bFCOqZIA4VLwW1dY1.."


def scrape_1688_with_cookie(keyword: str, max_pages: int = 1) -> List[Dict]:
    """使用 Cookie 爬取 1688"""
    base_url = "https://s.1688.com/selloffer/offer_search.htm"
    products = []
    
    for page in range(1, max_pages + 1):
        print(f"正在爬取第 {page} 页...")
        
        url = f"{base_url}?keywords={keyword}&beginPage={page}"
        
        try:
            # 使用 Cookie 爬取（直接在 headers 中传递）
            response = StealthyFetcher.fetch(
                url,
                headless=True,
                timeout=60000,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                    'Referer': 'https://www.1688.com/',
                    'Cookie': COOKIE,
                }
            )
            
            print(f"  状态码: {response.status}")
            print(f"  页面标题: {response.css('title::text').get()}")
            
            # 尝试多种选择器
            items = response.css('[class*="search-offer"]')
            if not items:
                items = response.css('[class*="offer-item"]')
            if not items:
                items = response.css('[data-spm]')
            
            if not items:
                print(f"  未找到商品")
                # 保存 HTML 用于调试
                with open(f'/tmp/1688_page_{page}.html', 'w', encoding='utf-8') as f:
                    f.write(str(response))
                print(f"  HTML 已保存到: /tmp/1688_page_{page}.html")
                break
            
            print(f"  找到 {len(items)} 个元素")
            
            for item in items[:20]:  # 只处理前 20 个
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
            print(f"  爬取失败: {e}")
            break
    
    return products


def main():
    if len(sys.argv) < 2:
        print("用法: python scrapling_1688_with_cookie.py <关键词>")
        sys.exit(1)
    
    keyword = sys.argv[1]
    
    print(f"🔍 搜索关键词: {keyword}")
    print(f"🔐 使用 Cookie 认证")
    print()
    
    products = scrape_1688_with_cookie(keyword, max_pages=1)
    
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
