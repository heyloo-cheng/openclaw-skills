#!/usr/bin/env python3
"""
Catering Design - Direct Nano Banana API Image Generator
Directly generate images using nano banana API.

Usage:
    # Simple prompt
    python3 scripts/generate_image_api.py "delicious pizza promotional poster"
    
    # With poster data (dish name, price, member price)
    python3 scripts/generate_image_api.py "招牌牛排" 198 168 --logo logo.png
    
    # With dish image
    python3 scripts/generate_image_api.py "新品披萨" 88 68 --dish-image pizza.jpg
    
    # Specific size
    python3 scripts/generate_image_api.py "川菜火锅" 128 98 --size 1792x1024
    
    # Multiple variations
    python3 scripts/generate_image_api.py "甜品" 58 48 --variations 3

Run outside sandbox for best results:
    cd /Users/heyloo/Documents/skill-creator
    python3 skills/public/catering-design/scripts/generate_image_api.py "your prompt"
"""

import os
import sys
import json
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

# API Configuration
NANO_BANANA_API_URL = "https://api.nanobana.com/v1/images/generations"
NANO_BANANA_API_KEY = os.environ.get("NANO_BANANA_API_KEY", "sk-pXPWfyGsbemwJAA9n2AjwYczCCmK8")


def generate_prompt_from_data(dish_name: str, price: float, member_price: float = None, 
                              style: str = 'modern', promo_badge: str = None) -> str:
    """Generate optimized prompt for poster."""
    
    style_prompts = {
        'modern': 'Modern minimalist restaurant promotional poster, clean contemporary design with orange and gold accents',
        'elegant': 'Luxurious fine dining poster, sophisticated dark theme with gold and black elegant typography',
        'playful': 'Vibrant fun restaurant poster, energetic pink and coral colors, casual dining aesthetic',
        'vintage': 'Warm nostalgic restaurant poster, classic 1950s diner style with rich orange-red tones',
        'minimal': 'Ultra-modern minimalist poster design, clean white and gray with lots of negative space',
    }
    
    prompt = f"""{style_prompts.get(style, style_prompts['modern'])},
prominent text "{dish_name}" as main headline,
price display: Regular Price {price} Yuan,
{member_price and f"Member Price {member_price} Yuan" or ""},
professional commercial food photography,
appetizing presentation with dramatic lighting,
commercial quality, high resolution poster design,
print-ready layout with clear typography"""
    
    if promo_badge:
        badge_text = {'sale': 'SALE', 'new': 'NEW', 'hot': 'HOT', 'member': 'MEMBER', 'limited': 'LIMITED'}
        prompt += f", promotional '{badge_text.get(promo_badge, promo_badge.upper())}' badge visible"
    
    return prompt


def call_api_curl(prompt: str, size: str = "1024x1024", timeout: int = 120) -> dict:
    """Call nano banana API using curl."""
    
    payload = json.dumps({
        "model": "nano-banana",
        "prompt": prompt,
        "size": size,
        "quality": "standard",
        "style": "vivid"
    })
    
    # Build curl command
    cmd = [
        'curl', '-s', '-X', 'POST',
        NANO_BANANA_API_URL,
        '-H', f'Authorization: Bearer {NANO_BANANA_API_KEY}',
        '-H', 'Content-Type: application/json',
        '-d', payload,
        '--max-time', str(timeout)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 10)
        
        if result.returncode != 0:
            return {"success": False, "error": f"curl error: {result.stderr}"}
        
        # Parse response
        try:
            response = json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"success": False, "error": f"Invalid JSON response: {result.stdout[:500]}"}
        
        # Check for API errors
        if isinstance(response, dict):
            if "error" in response:
                return {"success": False, "error": response["error"]}
            if "data" in response or "url" in response:
                return {"success": True, "response": response}
        
        return {"success": True, "response": response}
        
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Request timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def download_image_curl(url: str, filepath: Path, timeout: int = 60) -> bool:
    """Download image using curl."""
    cmd = ['curl', '-s', '-L', '-o', str(filepath), '--max-time', str(timeout), url]
    
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=timeout + 10)
        return result.returncode == 0 and filepath.exists() and filepath.stat().st_size > 0
    except Exception:
        return False


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="🎨 Generate images using nano banana API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple prompt
  python3 scripts/generate_image_api.py "delicious pizza promotional poster"
  
  # With prices
  python3 scripts/generate_image_api.py "招牌牛排" 198 168
  
  # With logo and dish image
  python3 scripts/generate_image_api.py "新品披萨" 88 68 --logo logo.png --dish-image pizza.jpg
  
  # Large size for print
  python3 scripts/generate_image_api.py "海报设计" 128 98 --size 1792x1024
  
  # Multiple variations
  python3 scripts/generate_image_api.py "甜品" 58 48 --variations 3

Environment:
  Export your API key: export NANO_BANANA_API_KEY="sk-xxx"
  Or it will use the default key configured in the script.
        """
    )
    
    parser.add_argument("dish_name", nargs="?", help="Dish name or prompt")
    parser.add_argument("price", nargs="?", type=float, help="Regular price")
    parser.add_argument("member_price", nargs="?", type=float, help="Member price (optional)")
    
    parser.add_argument("--logo", "-l", help="Logo image file path (for reference)")
    parser.add_argument("--dish-image", "-d", help="Dish image file path (for reference)")
    parser.add_argument("--output", "-o", default="./api_images", help="Output directory")
    
    parser.add_argument("--style", choices=['modern', 'elegant', 'playful', 'vintage', 'minimal'],
                        default='modern', help="Design style")
    parser.add_argument("--promo-badge", choices=['sale', 'new', 'hot', 'member', 'limited'],
                        help="Promotion badge style")
    parser.add_argument("--size", default="1024x1024", 
                        help="Image size (default: 1024x1024, options: 512x512, 1024x1024, 1792x1024, 1024x1280)")
    parser.add_argument("--variations", type=int, default=1, help="Number of variations (1-4)")
    
    parser.add_argument("--no-download", action="store_true", 
                        help="Only generate prompt, don't call API")
    parser.add_argument("--open-url", action="store_true",
                        help="Open the generated image URL in browser")
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_arguments()
    
    if not args.dish_name:
        print(__doc__)
        print("\n请提供提示词或菜品信息：")
        print('  python3 scripts/generate_image_api.py "delicious pizza poster"')
        print('  python3 scripts/generate_image_api.py "招牌牛排" 198 168')
        return
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Build prompt
    if args.price:
        prompt = generate_prompt_from_data(
            args.dish_name,
            args.price,
            args.member_price,
            args.style,
            args.promo_badge
        )
    else:
        prompt = args.dish_name
    
    print(f"\n{'='*70}")
    print("🎨 Nano Banana API 图片生成器")
    print(f"{'='*70}")
    print(f"\n📝 提示词:")
    print(f"   {prompt[:150]}{'...' if len(prompt) > 150 else ''}")
    print(f"\n📐 尺寸: {args.size}")
    print(f"   风格: {args.style}")
    if args.promo_badge:
        print(f"   标签: {args.promo_badge.upper()}")
    print(f"   变体: {args.variations}")
    
    if args.no_download:
        print(f"\n💡 提示词已生成，使用 --no-download 跳过 API 调用")
        prompt_file = output_dir / f"prompt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        prompt_file.write_text(prompt)
        print(f"   保存到: {prompt_file}")
        return
    
    print(f"\n{'='*70}")
    print("🌐 正在调用 nano banana API...")
    print(f"{'='*70}\n")
    
    # Size mapping for nano banana
    size_map = {
        "512x512": "512x512",
        "1024x1024": "1024x1024",
        "1792x1024": "1792x1024",
        "1024x1280": "1024x1280",
    }
    api_size = size_map.get(args.size, "1024x1024")
    
    results = []
    
    for i in range(args.variations):
        print(f"  📤 生成第 {i+1}/{args.variations} 张...")
        
        # Call API
        result = call_api_curl(prompt, api_size)
        
        if not result["success"]:
            print(f"     ❌ API 调用失败: {result.get('error', 'Unknown error')}")
            results.append({"success": False, "error": result.get('error')})
            continue
        
        # Extract image URL
        response = result["response"]
        image_url = None
        
        if isinstance(response, dict):
            # Try different response formats
            image_url = response.get("data", {}).get("url") if isinstance(response.get("data"), dict) else None
            if not image_url:
                image_url = response.get("url")
            if not image_url:
                # Handle list response
                images = response.get("data", response.get("images", []))
                if isinstance(images, list) and len(images) > 0:
                    image_url = images[0].get("url") if isinstance(images[0], dict) else images[0]
        
        if not image_url:
            print(f"     ⚠️  成功但无法获取图片URL")
            print(f"        响应: {str(response)[:200]}")
            results.append({"success": True, "response": response})
            continue
        
        print(f"     ✅ 图片生成成功!")
        print(f"        URL: {image_url[:80]}...")
        
        # Download image
        filename = f"{args.dish_name[:20]}_{args.style}_{i+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = output_dir / filename
        
        if download_image_curl(image_url, filepath):
            print(f"     💾 保存到: {filepath.name}")
            results.append({"success": True, "url": image_url, "filepath": str(filepath)})
        else:
            print(f"     ⚠️  下载失败，保留URL")
            results.append({"success": True, "url": image_url})
        
        # Open in browser if requested
        if args.open_url and i == 0:
            try:
                import webbrowser
                webbrowser.open(image_url)
                print(f"     🌐 已在浏览器中打开")
            except:
                pass
        
        # Rate limiting
        if i < args.variations - 1:
            time.sleep(2)
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 生成结果汇总")
    print(f"{'='*70}")
    
    successful = sum(1 for r in results if r.get("success"))
    failed = len(results) - successful
    
    print(f"\n   总数: {len(results)}")
    print(f"   成功: {successful}")
    print(f"   失败: {failed}")
    
    if successful > 0:
        print(f"\n   📁 输出目录: {output_dir.absolute()}")
        
        # Save prompt for reference
        prompt_file = output_dir / f"prompt_{args.dish_name[:15]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        prompt_file.write_text(prompt)
        print(f"   📝 提示词: {prompt_file.name}")
        
        # List downloaded images
        images = list(output_dir.glob(f"{args.dish_name[:15]}*.png"))
        if images:
            print(f"\n   🖼️  下载的图片:")
            for img in images[-3:]:  # Show last 3
                size = img.stat().st_size / 1024
                print(f"      - {img.name} ({size:.1f} KB)")
    
    if failed > 0:
        print(f"\n   ⚠️  失败的请求:")
        for r in results:
            if not r.get("success"):
                print(f"      - {r.get('error', 'Unknown error')}")
    
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    main()
