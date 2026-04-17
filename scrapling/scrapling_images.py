#!/usr/bin/env python3
"""
批量下载图片脚本（基于 Scrapling）

使用方法：
    python scrapling_images.py "https://example.com" --output ./images
    python scrapling_images.py "https://example.com" --selector ".product img" --max 10
"""

import sys
import os
import requests
from pathlib import Path
from typing import List
from scrapling.fetchers import Fetcher
from urllib.parse import urljoin, urlparse


def download_images(url: str, selector: str = 'img', output_dir: str = './images', max_images: int = None) -> List[str]:
    """
    从网页下载图片
    
    Args:
        url: 网页 URL
        selector: CSS 选择器（默认所有 img 标签）
        output_dir: 输出目录
        max_images: 最大下载数量
        
    Returns:
        下载的图片路径列表
    """
    print(f"🔍 正在爬取: {url}")
    
    # 爬取网页
    try:
        page = Fetcher.get(url, timeout=30)
    except Exception as e:
        print(f"❌ 爬取失败: {e}")
        return []
    
    # 提取图片 URL
    images = page.css(f'{selector}::attr(src)').getall()
    
    if not images:
        print(f"❌ 未找到图片（选择器: {selector}）")
        return []
    
    print(f"✅ 找到 {len(images)} 个图片")
    
    # 限制数量
    if max_images:
        images = images[:max_images]
        print(f"📊 限制下载: {len(images)} 个")
    
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 下载图片
    downloaded = []
    for i, img_url in enumerate(images, 1):
        try:
            # 处理相对 URL
            if not img_url.startswith('http'):
                img_url = urljoin(url, img_url)
            
            # 获取文件扩展名
            parsed = urlparse(img_url)
            ext = os.path.splitext(parsed.path)[1]
            if not ext or ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                ext = '.jpg'
            
            # 下载
            print(f"  [{i}/{len(images)}] 下载: {img_url[:60]}...")
            response = requests.get(img_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            # 保存
            filename = f"image_{i:03d}{ext}"
            filepath = output_path / filename
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            downloaded.append(str(filepath))
            print(f"  ✅ 已保存: {filepath}")
        
        except Exception as e:
            print(f"  ❌ 下载失败: {e}")
            continue
    
    return downloaded


def main():
    if len(sys.argv) < 2:
        print("用法: python scrapling_images.py <URL> [--selector CSS] [--output DIR] [--max N]")
        sys.exit(1)
    
    url = sys.argv[1]
    selector = 'img'
    output_dir = './images'
    max_images = None
    
    # 解析参数
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--selector' and i + 1 < len(sys.argv):
            selector = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--output' and i + 1 < len(sys.argv):
            output_dir = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--max' and i + 1 < len(sys.argv):
            max_images = int(sys.argv[i + 1])
            i += 2
        else:
            i += 1
    
    print(f"🌐 URL: {url}")
    print(f"🎯 选择器: {selector}")
    print(f"📁 输出目录: {output_dir}")
    if max_images:
        print(f"🔢 最大数量: {max_images}")
    print()
    
    # 下载
    downloaded = download_images(url, selector, output_dir, max_images)
    
    print()
    print("=" * 60)
    print(f"✅ 成功下载 {len(downloaded)} 个图片")
    print(f"📁 保存位置: {output_dir}")
    print("=" * 60)


if __name__ == '__main__':
    main()
