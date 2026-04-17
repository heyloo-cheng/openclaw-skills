#!/usr/bin/env python3
"""
1688 API 爬取脚本（方案 3：Stealth-Requests + API）

基于 GitHub 最新发现：
- Stealth-Requests：现代化反检测（2024-2025）
- 1688-Decryptor：API 签名生成

使用方法：
    python scrapling_1688_api.py "迷你加湿器"
"""

import sys
import json
import time
import hashlib
from typing import List, Dict, Optional

try:
    import stealth_requests as requests
    print("✅ 使用 Stealth-Requests（反检测）")
except ImportError:
    import requests
    print("⚠️ 使用标准 requests（建议安装 stealth_requests）")


def generate_sign(m_h5_tk: str, timestamp: str, app_key: str, data: str) -> str:
    """生成 1688 API 签名"""
    # 提取 _m_h5_tk 的前半部分
    token = m_h5_tk.split('_')[0] if '_' in m_h5_tk else m_h5_tk
    
    # 拼接签名字符串
    pre_sign_str = f'{token}&{timestamp}&{app_key}&{data}'
    
    # MD5 加密
    sign = hashlib.md5(pre_sign_str.encode('utf-8')).hexdigest()
    
    return sign


def get_m_h5_tk() -> Optional[str]:
    """
    获取 _m_h5_tk
    
    方法 1：从 Cookie 中提取
    方法 2：调用 1688 API 生成
    """
    # TODO: 实现获取逻辑
    # 这里需要用户提供或通过 API 生成
    return None


def search_1688_api(keyword: str, page: int = 1) -> List[Dict]:
    """使用 1688 API 搜索商品"""
    
    # API 配置
    APP_KEY = '12574478'  # 固定值
    API_URL = 'https://h5api.m.1688.com/h5/mtop.alibaba.alisite.cbu.server.pc.ModuleAsyncService/1.0/'
    
    # 构建请求参数
    timestamp = str(int(time.time() * 1000))
    
    # 请求数据
    data = json.dumps({
        "componentKey": "wp_pc_search_offer_list",
        "params": json.dumps({
            "keywords": keyword,
            "beginPage": page
        })
    }, ensure_ascii=False)
    
    # 获取 _m_h5_tk（需要 Cookie）
    m_h5_tk = get_m_h5_tk()
    if not m_h5_tk:
        print("❌ 需要 _m_h5_tk（从 Cookie 获取）")
        print("\n获取方法：")
        print("  1. 打开浏览器访问 https://www.1688.com")
        print("  2. 登录账号")
        print("  3. 按 F12 打开开发者工具")
        print("  4. 在控制台运行: document.cookie")
        print("  5. 找到 _m_h5_tk 的值")
        return []
    
    # 生成签名
    sign = generate_sign(m_h5_tk, timestamp, APP_KEY, data)
    
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
    
    # 请求头（需要包含 Cookie）
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Referer': 'https://www.1688.com/',
        'Cookie': f'_m_h5_tk={m_h5_tk}; ...'  # 需要完整 Cookie
    }
    
    try:
        print(f"🔍 搜索: {keyword} (第 {page} 页)")
        print(f"📡 API: {API_URL}")
        
        # 使用 Stealth-Requests 发送请求
        response = requests.get(
            API_URL,
            params=params,
            headers=headers,
            retry=3,
            timeout=30
        )
        
        print(f"✅ 状态码: {response.status_code}")
        
        # 解析响应
        if response.status_code == 200:
            # 移除 JSONP 包装
            text = response.text
            if text.startswith('mtopjsonp2('):
                text = text[11:-1]  # 移除 mtopjsonp2( 和 )
            
            data = json.loads(text)
            
            # 提取商品列表
            if data.get('ret') == ['SUCCESS::调用成功']:
                products = data.get('data', {}).get('offerList', [])
                return products
            else:
                print(f"❌ API 返回错误: {data.get('ret')}")
        
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    return []


def test_stealth_requests():
    """测试 Stealth-Requests"""
    print("\n🧪 测试 Stealth-Requests")
    print("=" * 60)
    
    try:
        # 测试简单请求
        resp = requests.get('https://www.1688.com/', retry=2, timeout=10)
        
        print(f"✅ 请求成功")
        print(f"状态码: {resp.status_code}")
        print(f"页面标题: {resp.text[:100]}...")
        
        # 检查是否被重定向
        if 'login' in resp.url.lower():
            print("⚠️ 被重定向到登录页")
        else:
            print("✅ 未被重定向")
        
        return True
    
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def main():
    print("🚀 方案 3：Stealth-Requests + 1688 API")
    print("=" * 60)
    
    # 测试 Stealth-Requests
    if not test_stealth_requests():
        print("\n❌ Stealth-Requests 测试失败")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("📋 下一步：")
    print("  1. 获取 _m_h5_tk（从浏览器 Cookie）")
    print("  2. 配置完整 Cookie")
    print("  3. 调用 search_1688_api() 搜索商品")
    print("\n💡 提示：")
    print("  - 这个方案直接调用 1688 API")
    print("  - 绕过 HTML 反爬虫")
    print("  - 需要登录后的 Cookie")
    print("=" * 60)


if __name__ == '__main__':
    main()
