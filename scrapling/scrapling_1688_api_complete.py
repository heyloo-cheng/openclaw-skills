#!/usr/bin/env python3
"""
1688 API 完整实现（方案 3：Stealth-Requests + API）

使用方法：
    python scrapling_1688_api_complete.py "迷你加湿器"
"""

import sys
import json
import time
import hashlib
import re
from typing import List, Dict

try:
    import stealth_requests as requests
    print("✅ 使用 Stealth-Requests（反检测）")
except ImportError:
    import requests
    print("⚠️ 使用标准 requests（建议安装 stealth_requests）")


# 从用户提供的 Cookie 中提取
COOKIE = "leftMenuLastMode=COLLAPSE; mtop_partitioned_detect=1; _m_h5_tk=37baa87b0f8d29e04572bbf3a755dd2c_1776160435088; _m_h5_tk_enc=c26b596fa2d060b0da0ecb781f499166; xlly_s=1; leftMenuModeTip=shown; plugin_home_downLoad_cookie=%E4%B8%8B%E8%BD%BD%E6%8F%92%E4%BB%B6; t=87f1c4553d6a1cea12a9b990650392a2; _tb_token_=ee71376e6ef71; sg=%E8%AF%9A60; lid=yyc%E5%AE%87%E8%AF%9A; unb=2445313076; _nk_=yyc%5Cu5B87%5Cu8BDA; _csrf_token=1776150388241; __cn_logon__=true; __cn_logon_id__=yyc%E5%AE%87%E8%AF%9A; __last_loginid__=b2b-2445313076; __last_memberid__=b2b-2445313076; last_mid=b2b-2445313076; isg=BLCw78JerW6BuHFqvaL5G49BgXgC-ZRDziUIgaoBfIveZVAPUglk0wbHv20Fbkwb; tfstk=gtPiImODLDt7LExFZnl1p1n7gu6d1fGjEodxDjnVLDoBXhdTuXJE5Vk46fUTxFN3qIdOfOa2ijhV2gCRwP6sGjS8B-ttCFgxrI-wDAke8j3mdFP1ZPasGe94dPW35svpuHOZum7nTquyQjkwQpJEAqpZ0ooZLHuoPjo40o8FT4gybduqbH7nlDoqgjr48w0xYmlqgozEOOOqqSPQTgWXzJ-mSEpI7Amz7DAuRWuN40fSAIR0tV4n4PyWgIPnSAVhqCBfCjyaWkD8IgAiGPy7c4rwbG03szV0Uk5psj4UUScUTM8Kb8a3ifFNk1lUslVZKo8AD2w-rrD8pZJov-zQtvVGeEgQ6rPseb5WbmeLrS00Gi13qPrgUYPwjgoJLL5C4IgFkWJXhAuI-0do-qiiLRtoNwbHFOMZRVIR-wvXoAuI-B7h-LuZQ2g1l"

# 提取 _m_h5_tk
M_H5_TK = "37baa87b0f8d29e04572bbf3a755dd2c_1776160435088"


def generate_sign(m_h5_tk: str, timestamp: str, app_key: str, data: str) -> str:
    """生成 1688 API 签名"""
    # 提取 _m_h5_tk 的前半部分
    token = m_h5_tk.split('_')[0] if '_' in m_h5_tk else m_h5_tk
    
    # 拼接签名字符串
    pre_sign_str = f'{token}&{timestamp}&{app_key}&{data}'
    
    # MD5 加密
    sign = hashlib.md5(pre_sign_str.encode('utf-8')).hexdigest()
    
    return sign


def search_1688_api(keyword: str, page: int = 1) -> List[Dict]:
    """使用 1688 API 搜索商品"""
    
    # API 配置
    APP_KEY = '12574478'
    API_URL = 'https://h5api.m.1688.com/h5/mtop.alibaba.alisite.cbu.server.pc.ModuleAsyncService/1.0/'
    
    # 当前时间戳
    timestamp = str(int(time.time() * 1000))
    
    # 构建请求数据
    data_dict = {
        "componentKey": "wp_pc_search_offer_list",
        "params": json.dumps({
            "keywords": keyword,
            "beginPage": page
        }, ensure_ascii=False)
    }
    data = json.dumps(data_dict, ensure_ascii=False)
    
    # 生成签名
    sign = generate_sign(M_H5_TK, timestamp, APP_KEY, data)
    
    # 构建请求参数
    params = {
        'jsv': '2.7.0',
        'appKey': APP_KEY,
        't': timestamp,
        'sign': sign,
        'api': 'mtop.alibaba.alisite.cbu.server.pc.ModuleAsyncService',
        'v': '1.0',
        'type': 'jsonp',
        'valueType': 'string',
        'dataType': 'jsonp',
        'timeout': '10000',
        'callback': 'mtopjsonp2',
        'data': data
    }
    
    # 请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Referer': 'https://www.1688.com/',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cookie': COOKIE
    }
    
    try:
        print(f"\n🔍 搜索: {keyword} (第 {page} 页)")
        print(f"📡 API: {API_URL}")
        print(f"🔐 签名: {sign[:16]}...")
        
        # 使用 Stealth-Requests 发送请求
        response = requests.get(
            API_URL,
            params=params,
            headers=headers,
            retry=3,
            timeout=30
        )
        
        print(f"✅ 状态码: {response.status_code}")
        
        if response.status_code == 200:
            # 移除 JSONP 包装
            text = response.text
            if text.startswith('mtopjsonp2('):
                text = text[11:-1]
            
            # 解析 JSON
            result = json.loads(text)
            
            # 检查返回状态
            ret = result.get('ret', [])
            print(f"📋 返回状态: {ret}")
            
            if 'SUCCESS' in str(ret):
                # 提取商品列表
                data = result.get('data', {})
                
                # 保存完整响应用于调试
                with open('/tmp/1688_api_response.json', 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"💾 完整响应已保存: /tmp/1688_api_response.json")
                
                # 尝试提取商品
                if isinstance(data, dict):
                    offers = data.get('offerList', [])
                    if offers:
                        print(f"✅ 找到 {len(offers)} 个商品")
                        return offers
                    else:
                        print(f"⚠️ 未找到 offerList")
                        print(f"数据结构: {list(data.keys())}")
                else:
                    print(f"⚠️ data 不是字典: {type(data)}")
            else:
                print(f"❌ API 返回错误: {ret}")
        
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        import traceback
        traceback.print_exc()
    
    return []


def main():
    if len(sys.argv) < 2:
        print("用法: python scrapling_1688_api_complete.py <关键词>")
        sys.exit(1)
    
    keyword = sys.argv[1]
    
    print("🚀 方案 3：Stealth-Requests + 1688 API")
    print("=" * 60)
    
    # 搜索商品
    products = search_1688_api(keyword, page=1)
    
    if not products:
        print("\n❌ 未找到商品")
        print("\n💡 故障排查:")
        print("  1. 检查 /tmp/1688_api_response.json 查看完整响应")
        print("  2. Cookie 可能已过期，需要重新获取")
        print("  3. API 接口可能已变更")
        sys.exit(1)
    
    # 解析商品信息
    print("\n" + "=" * 60)
    print(f"✅ 找到 {len(products)} 个商品")
    print("=" * 60)
    
    # 显示前 5 个
    print("\n前 5 个商品:")
    for i, product in enumerate(products[:5], 1):
        print(f"\n{i}. {product.get('subject', 'N/A')[:50]}")
        print(f"   价格: ¥{product.get('price', 'N/A')}")
        print(f"   供应商: {product.get('companyName', 'N/A')[:30]}")
        print(f"   链接: {product.get('detailUrl', 'N/A')}")


if __name__ == '__main__':
    main()
