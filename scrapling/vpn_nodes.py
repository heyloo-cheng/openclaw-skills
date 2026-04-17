#!/usr/bin/env python3
"""
VPN 节点配置文件

从 https://106.55.228.246:36666/hxvip?token=e1ba6df33feb83a9e2f39ee971723a86 获取
"""

import base64
import json
from typing import List, Dict

# Base64 编码的 VPN 节点
VPN_NODES_BASE64 = """
c3M6Ly9ZV1Z6TFRJMU5pMW5ZMjA2T1RBNVkyRXpOelF0TlRBeFlTMDBZVE0wTFRoak1XVXRZVFZpWlROallXUmlaV0l5QDExMC4yNDIuNzQuMTAyOjEwMDAxIyVGMCU5RiU4NyVBRCVGMCU5RiU4NyVCMCUyMCVFOSVBNiU5OSVFNiVCOCVBRklFUEwNCnNzOi8vWVdWekxUSTFOaTFuWTIwNk9UQTVZMkV6TnpRdE5UQXhZUzAwWVRNMExUaGpNV1V0WVRWaVpUTmpZV1JpWldJeUAxMTAuMjQyLjc0LjEwMjoxMDAwMiMlRjAlOUYlODclQTglRjAlOUYlODclQjMlMjAlRTUlOEYlQjAlRTYlQjklQkVJRVBMDQpzczovL1lXVnpMVEkxTmkxblkyMDZPVEE1WTJFek56UXROVEF4WVMwMFlUTTBMVGhqTVdVdFlUVmlaVE5qWVdSaVpXSXlAMTEwLjI0Mi43NC4xMDI6MTAwMDMjJUYwJTlGJTg3JUFGJUYwJTlGJTg3JUI1JTIwJUU2JTk3JUE1JUU2JTlDJUFDSUVQTA0Kc3M6Ly9ZV1Z6TFRJMU5pMW5ZMjA2T1RBNVkyRXpOelF0TlRBeFlTMDBZVE0wTFRoak1XVXRZVFZpWlROallXUmlaV0l5QDExMC4yNDIuNzQuMTAyOjEwMDA0IyVGMCU5RiU4NyVCOCVGMCU5RiU4NyVBQyUyMCVFNiU5NiVCMCVFNSU4QSVBMCVFNSU5RCVBMUlFUEwNCnNzOi8vWVdWekxUSTFOaTFuWTIwNk9UQTVZMkV6TnpRdE5UQXhZUzAwWVRNMExUaGpNV1V0WVRWaVpUTmpZV1JpWldJeUAxMTAuMjQyLjc0LjEwMjoxMDAwNSMlRjAlOUYlODclQkElRjAlOUYlODclQjglMjAlRTclQkUlOEUlRTUlOUIlQkRJRVBM
"""

def parse_shadowsocks_url(ss_url: str) -> Dict:
    """解析 Shadowsocks URL"""
    try:
        # 移除 ss:// 前缀
        ss_url = ss_url.replace('ss://', '')
        
        # 分离节点信息和名称
        if '#' in ss_url:
            node_info, name = ss_url.split('#', 1)
        else:
            node_info = ss_url
            name = "Unknown"
        
        # Base64 解码
        decoded = base64.b64decode(node_info + '==').decode('utf-8')
        
        # 解析格式：method:password@server:port
        method_password, server_port = decoded.split('@')
        method, password = method_password.split(':', 1)
        server, port = server_port.split(':')
        
        return {
            'name': name,
            'server': server,
            'port': int(port),
            'method': method,
            'password': password,
            'type': 'shadowsocks'
        }
    except Exception as e:
        print(f"解析失败: {e}")
        return None


def get_vpn_nodes() -> List[Dict]:
    """获取所有 VPN 节点"""
    # 解码 Base64
    decoded = base64.b64decode(VPN_NODES_BASE64).decode('utf-8')
    
    # 分割每个节点
    lines = decoded.strip().split('\n')
    
    nodes = []
    for line in lines:
        line = line.strip()
        if line.startswith('ss://'):
            node = parse_shadowsocks_url(line)
            if node:
                nodes.append(node)
    
    return nodes


def get_proxy_url(node: Dict) -> str:
    """将节点转换为代理 URL"""
    if node['type'] == 'shadowsocks':
        # Shadowsocks 代理格式
        return f"socks5://{node['server']}:{node['port']}"
    return None


# 可用节点列表
AVAILABLE_NODES = [
    {
        'name': '🇭🇰 香港IEPL',
        'server': '110.242.74.102',
        'port': 10001,
        'method': 'aes-256-gcm',
        'password': '909ca374-501a-4a34-8c1e-a5be3cadbeb2',
        'type': 'shadowsocks',
        'country': 'hk'
    },
    {
        'name': '🇨🇳 台湾IEPL',
        'server': '110.242.74.102',
        'port': 10002,
        'method': 'aes-256-gcm',
        'password': '909ca374-501a-4a34-8c1e-a5be3cadbeb2',
        'type': 'shadowsocks',
        'country': 'tw'
    },
    {
        'name': '🇯🇵 日本IEPL',
        'server': '110.242.74.102',
        'port': 10003,
        'method': 'aes-256-gcm',
        'password': '909ca374-501a-4a34-8c1e-a5be3cadbeb2',
        'type': 'shadowsocks',
        'country': 'jp'
    },
    {
        'name': '🇸🇬 新加坡IEPL',
        'server': '110.242.74.102',
        'port': 10004,
        'method': 'aes-256-gcm',
        'password': '909ca374-501a-4a34-8c1e-a5be3cadbeb2',
        'type': 'shadowsocks',
        'country': 'sg'
    },
    {
        'name': '🇺🇸 美国IEPL',
        'server': '110.242.74.102',
        'port': 10005,
        'method': 'aes-256-gcm',
        'password': '909ca374-501a-4a34-8c1e-a5be3cadbeb2',
        'type': 'shadowsocks',
        'country': 'us'
    }
]


def get_node_by_country(country: str = 'hk') -> Dict:
    """根据国家获取节点"""
    for node in AVAILABLE_NODES:
        if node['country'] == country:
            return node
    return AVAILABLE_NODES[0]  # 默认返回第一个


def get_all_nodes() -> List[Dict]:
    """获取所有节点"""
    return AVAILABLE_NODES


if __name__ == '__main__':
    print("可用 VPN 节点:")
    for i, node in enumerate(AVAILABLE_NODES, 1):
        print(f"{i}. {node['name']}")
        print(f"   服务器: {node['server']}:{node['port']}")
        print(f"   国家: {node['country']}")
        print()
