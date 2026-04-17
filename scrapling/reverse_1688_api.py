#!/usr/bin/env python3
"""
1688 API 逆向分析工具

使用 Stealth-Requests 访问 1688 搜索页面，
分析网络请求，找到真实的 API 接口

使用方法：
    python reverse_1688_api.py "迷你加湿器"
"""

import sys
import json
import time
import hashlib
from urllib.parse import urlencode, quote

try:
    import stealth_requests as requests
    print("✅ 使用 Stealth-Requests")
except ImportError:
    import requests
    print("⚠️ 使用标准 requests")


# 用户提供的 Cookie
COOKIE = "leftMenuLastMode=COLLAPSE; mtop_partitioned_detect=1; _m_h5_tk=37baa87b0f8d29e04572bbf3a755dd2c_1776160435088; _m_h5_tk_enc=c26b596fa2d060b0da0ecb781f499166; xlly_s=1; leftMenuModeTip=shown; plugin_home_downLoad_cookie=%E4%B8%8B%E8%BD%BD%E6%8F%92%E4%BB%B6; t=87f1c4553d6a1cea12a9b990650392a2; _tb_token_=ee71376e6ef71; sg=%E8%AF%9A60; lid=yyc%E5%AE%87%E8%AF%9A; unb=2445313076; _nk_=yyc%5Cu5B87%5Cu8BDA; _csrf_token=1776150388241; __cn_logon__=true; __cn_logon_id__=yyc%E5%AE%87%E8%AF%9A; __last_loginid__=b2b-2445313076; __last_memberid__=b2b-2445313076; last_mid=b2b-2445313076; isg=BLCw78JerW6BuHFqvaL5G49BgXgC-ZRDziUIgaoBfIveZVAPUglk0wbHv20Fbkwb; tfstk=gtPiImODLDt7LExFZnl1p1n7gu6d1fGjEodxDjnVLDoBXhdTuXJE5Vk46fUTxFN3qIdOfOa2ijhV2gCRwP6sGjS8B-ttCFgxrI-wDAke8j3mdFP1ZPasGe94dPW35svpuHOZum7nTquyQjkwQpJEAqpZ0ooZLHuoPjo40o8FT4gybduqbH7nlDoqgjr48w0xYmlqgozEOOOqqSPQTgWXzJ-mSEpI7Amz7DAuRWuN40fSAIR0tV4n4PyWgIPnSAVhqCBfCjyaWkD8IgAiGPy7c4rwbG03szV0Uk5psj4UUScUTM8Kb8a3ifFNk1lUslVZKo8AD2w-rrD8pZJov-zQtvVGeEgQ6rPseb5WbmeLrS00Gi13qPrgUYPwjgoJLL5C4IgFkWJXhAuI-0do-qiiLRtoNwbHFOMZRVIR-wvXoAuI-B7h-LuZQ2g1l"

M_H5_TK = "37baa87b0f8d29e04572bbf3a755dd2c_1776160435088"


def test_search_page(keyword: str):
    """测试访问搜索页面"""
    print(f"\n🔍 测试 1：访问搜索页面")
    print("=" * 60)
    
    # 搜索 URL
    search_url = f"https://s.1688.com/selloffer/offer_search.htm?keywords={quote(keyword)}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cookie': COOKIE
    }
    
    try:
        print(f"URL: {search_url}")
        resp = requests.get(search_url, headers=headers, timeout=30)
        
        print(f"✅ 状态码: {resp.status_code}")
        print(f"最终 URL: {resp.url}")
        
        # 检查是否被重定向
        if 'login' in resp.url.lower():
            print("❌ 被重定向到登录页")
            return False
        
        # 保存 HTML
        with open('/tmp/1688_search_page.html', 'w', encoding='utf-8') as f:
            f.write(resp.text)
        print(f"💾 HTML 已保存: /tmp/1688_search_page.html")
        
        # 查找 API 调用
        if 'mtop.alibaba' in resp.text:
            print("✅ 发现 mtop API 调用")
            
            # 提取 API 相关代码
            import re
            api_matches = re.findall(r'mtop\.alibaba\.[a-zA-Z.]+', resp.text)
            if api_matches:
                print(f"发现的 API:")
                for api in set(api_matches[:10]):
                    print(f"  - {api}")
        
        return True
        
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False


def test_api_variations(keyword: str):
    """测试不同的 API 变体"""
    print(f"\n🔍 测试 2：尝试不同的 API 接口")
    print("=" * 60)
    
    APP_KEY = '12574478'
    
    # 可能的 component keys
    component_keys = [
        'wp_pc_search_offer_list',
        'pc_search_offer_list',
        'search_offer_list',
        'offer_search',
        'pc_offer_search',
        'wp_offer_search',
    ]
    
    for component_key in component_keys:
        print(f"\n尝试: {component_key}")
        
        timestamp = str(int(time.time() * 1000))
        
        # 构建请求数据
        data_dict = {
            "componentKey": component_key,
            "params": json.dumps({
                "keywords": keyword,
                "beginPage": 1
            }, ensure_ascii=False)
        }
        data = json.dumps(data_dict, ensure_ascii=False)
        
        # 生成签名
        token = M_H5_TK.split('_')[0]
        pre_sign_str = f'{token}&{timestamp}&{APP_KEY}&{data}'
        sign = hashlib.md5(pre_sign_str.encode('utf-8')).hexdigest()
        
        # 构建请求参数
        params = {
            'jsv': '2.7.0',
            'appKey': APP_KEY,
            't': timestamp,
            'sign': sign,
            'api': 'mtop.alibaba.alisite.cbu.server.pc.ModuleAsyncService',
            'v': '1.0',
            'type': 'jsonp',
            'dataType': 'jsonp',
            'callback': 'mtopjsonp2',
            'data': data
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Referer': 'https://www.1688.com/',
            'Cookie': COOKIE
        }
        
        try:
            api_url = 'https://h5api.m.1688.com/h5/mtop.alibaba.alisite.cbu.server.pc.ModuleAsyncService/1.0/'
            resp = requests.get(api_url, params=params, headers=headers, timeout=10)
            
            if resp.status_code == 200:
                # 移除 JSONP 包装
                text = resp.text
                if text.startswith('mtopjsonp2('):
                    text = text[11:-1]
                
                result = json.loads(text)
                ret = result.get('ret', [])
                
                if 'SUCCESS' in str(ret):
                    print(f"  ✅ 成功! {ret}")
                    
                    # 保存响应
                    with open(f'/tmp/1688_api_{component_key}.json', 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    print(f"  💾 响应已保存: /tmp/1688_api_{component_key}.json")
                    
                    return component_key
                else:
                    print(f"  ❌ 失败: {ret}")
        
        except Exception as e:
            print(f"  ❌ 错误: {e}")
    
    return None


def main():
    if len(sys.argv) < 2:
        print("用法: python reverse_1688_api.py <关键词>")
        sys.exit(1)
    
    keyword = sys.argv[1]
    
    print("🚀 1688 API 逆向分析")
    print("=" * 60)
    print(f"关键词: {keyword}")
    print()
    
    # 测试 1：访问搜索页面
    if test_search_page(keyword):
        print("\n✅ 搜索页面访问成功")
    else:
        print("\n❌ 搜索页面访问失败")
    
    # 测试 2：尝试不同的 API
    success_key = test_api_variations(keyword)
    
    if success_key:
        print(f"\n🎉 找到可用的 API!")
        print(f"Component Key: {success_key}")
    else:
        print(f"\n❌ 未找到可用的 API")
        print("\n💡 建议:")
        print("  1. 检查 /tmp/1688_search_page.html 查找 API 调用")
        print("  2. 使用浏览器开发者工具查看网络请求")
        print("  3. 或继续使用 Deep Search 方案")


if __name__ == '__main__':
    main()
