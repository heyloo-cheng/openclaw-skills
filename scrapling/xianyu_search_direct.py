#!/usr/bin/env python3
"""
直接调用闲鱼搜索（不通过 openclaw run）
"""

import sys
import json
import os

# 添加路径
sys.path.insert(0, os.path.expanduser('~/.openclaw/extensions/xianyu'))

try:
    # 使用全局函数而不是类
    from utils.item_search import search_xianyu_items
    import asyncio
    
    if __name__ == '__main__':
        keyword = sys.argv[1] if len(sys.argv) > 1 else '蓝牙耳机'
        
        # 运行搜索
        results = asyncio.run(search_xianyu_items(keyword, page=1, page_size=20))
        
        # 提取价格
        prices = []
        for item in results.get('items', []):
            try:
                price = float(item.get('price', 0))
                if price > 0 and price < 10000:
                    prices.append(price)
            except:
                pass
        
        if prices:
            output = {
                'success': True,
                'min': min(prices),
                'max': max(prices),
                'avg': sum(prices) / len(prices),
                'count': len(prices)
            }
        else:
            output = {
                'success': False,
                'error': '未找到价格数据'
            }
        
        print(json.dumps(output, ensure_ascii=False))
        
except Exception as e:
    print(json.dumps({
        'success': False,
        'error': str(e)
    }, ensure_ascii=False))
