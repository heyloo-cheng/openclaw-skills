#!/usr/bin/env python3
"""
Catering Design - Nano Banana API Image Generator

This script generates optimized prompts and can call nano banana API 
to generate images directly.

Usage:
    # Just generate prompts (always works)
    python3 scripts/generate_images.py "italian restaurant poster new pasta"
    
    # Generate for specific platform
    python3 scripts/generate_images.py "川菜火锅海报" --platform xiaohongshu
    
    # Generate for all platforms
    python3 scripts/generate_images.py "bubble tea" --all-platforms
    
    # With API call (requires proper SSL settings)
    python3 scripts/generate_images.py "pizza promotion" --api

For best results, run outside sandbox:
    cd /Users/heyloo/Documents/skill-creator
    python3 skills/public/catering-design/scripts/generate_images.py "your prompt"
"""

import json
import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

# Try to import requests, fallback to subprocess
try:
    import requests
    HAS_REQUESTS = True
except (ImportError, PermissionError):
    HAS_REQUESTS = False

# API Configuration
NANO_BANANA_API_URL = "https://api.nanobana.com/v1/images/generations"
NANO_BANANA_API_KEY = os.environ.get("NANO_BANANA_API_KEY", "sk-pXPWfyGsbemwJAA9n2AjwYczCCmK8")

# Color palettes (simplified)
COLOR_PALETTES = {
    'warm': '#E85D04, #F48C06, #FAA307, #FFBA08',
    'fresh': '#15803D, #166534, #16A34A, #22C55E',
    'elegant': '#000000, #1C1917, #C0A062, #FEF3C7',
    'playful': '#EC4899, #F472B6, #F9A8D4, #FDF2F8',
    'cafe': '#5D4037, #795548, #8D6E63, #D7CCC8',
}

# Design styles
STYLES = {
    'vintage': 'Vintage 1950s diner aesthetic, warm nostalgic feel',
    'modern': 'Clean contemporary design, minimalist approach',
    'minimal': 'Modern minimalist, lots of white space',
    'rustic': 'Rustic farm-to-table, earthy textures',
    'elegant': 'Sophisticated fine dining, elegant atmosphere',
    'playful': 'Fun and energetic, vibrant colors',
    'luxury': 'Premium and exclusive, gold accents',
}

# Platform specifications
PLATFORMS = {
    'wechat': {'size': '1080x1350', 'note': 'WeChat Moments style, vertical 4:5 format'},
    'xiaohongshu': {'size': '1080x1080', 'note': 'Xiaohongshu aesthetic, square format'},
    'xiaohongshu_story': {'size': '1080x1920', 'note': 'Xiaohongshu Story, vertical 9:16'},
    'instagram': {'size': '1080x1080', 'note': 'Instagram Post, square format'},
    'instagram_story': {'size': '1080x1920', 'note': 'Instagram Story, vertical 9:16'},
    'douyin': {'size': '1080x1920', 'note': 'Douyin short video cover, vertical 9:16'},
    'a4': {'size': '2480x3508', 'note': 'A4 poster format, print-ready, 300 DPI'},
    'a3': {'size': '3508x4961', 'note': 'A3 poster format, print-ready, 300 DPI'},
}


def parse_request(request: str) -> dict:
    """Parse user request."""
    request_lower = request.lower()
    
    # Detect cuisine
    cuisines = {
        'chinese': ['chinese', '中餐', '川菜', '火锅', '麻辣', '粤菜', '东北菜'],
        'japanese': ['japanese', '日本料理', '寿司', '拉面', '日式'],
        'italian': ['italian', '意大利', '披萨', '意面', '披萨', '意式'],
        'french': ['french', '法餐', '法国菜'],
        'american': ['american', '美式', '汉堡', '快餐'],
        'korean': ['korean', '韩国', '烤肉', '韩式'],
        'mexican': ['mexican', '墨西哥', '塔可'],
        'thai': ['thai', '泰国', '泰餐'],
        'cafe': ['cafe', '咖啡', '奶茶', 'bubble tea', '咖啡厅'],
        'bakery': ['bakery', '面包', '烘焙', '甜品', '蛋糕'],
        'bar': ['bar', '酒吧', '酒', '精酿', '啤酒'],
    }
    
    cuisine = 'modern fusion'
    for k, v in cuisines.items():
        if any(kw in request_lower for kw in v):
            cuisine = k
            break
    
    # Detect material
    if any(w in request_lower for w in ['poster', '海报']):
        material = 'poster'
    elif any(w in request_lower for w in ['flyer', '传单']):
        material = 'flyer'
    elif any(w in request_lower for w in ['menu', '菜单', '价目表']):
        material = 'menu'
    elif any(w in request_lower for w in ['social', '小红书', '抖音', '朋友圈', 'instagram']):
        material = 'social'
    elif any(w in request_lower for w in ['business card', '名片']):
        material = 'business_card'
    elif any(w in request_lower for w in ['sticker', '贴纸', '贴']):
        material = 'sticker'
    else:
        material = 'poster'
    
    # Detect style
    if any(w in request_lower for w in ['vintage', '复古', '怀旧']):
        style = 'vintage'
    elif any(w in request_lower for w in ['elegant', '优雅', '高端', '精致']):
        style = 'elegant'
    elif any(w in request_lower for w in ['playful', '有趣', '活泼', '卡通', '可爱']):
        style = 'playful'
    elif any(w in request_lower for w in ['luxury', '奢华', ' premium']):
        style = 'luxury'
    elif any(w in request_lower for w in ['rustic', '乡村', '田园', '自然']):
        style = 'rustic'
    elif any(w in request_lower for w in ['minimal', '极简', '简约']):
        style = 'minimal'
    else:
        style = 'modern'
    
    return {'cuisine': cuisine, 'material': material, 'style': style, 'request': request}


def get_colors(cuisine: str, style: str) -> str:
    """Get color palette based on cuisine and style."""
    if style in ['vintage', 'rustic']:
        return COLOR_PALETTES['warm']
    elif style in ['elegant', 'luxury']:
        return COLOR_PALETTES['elegant']
    elif style == 'playful':
        return COLOR_PALETTES['playful']
    elif cuisine == 'cafe':
        return COLOR_PALETTES['cafe']
    elif cuisine in ['chinese', 'japanese', 'korean', 'thai']:
        return COLOR_PALETTES['warm']
    else:
        return COLOR_PALETTES['warm']


def generate_prompt(data: dict, platform: str = None) -> str:
    """Generate optimized image prompt."""
    cuisine = data['cuisine']
    style = data['style']
    material = data['material']
    colors = get_colors(cuisine, style)
    style_desc = STYLES.get(style, STYLES['modern'])
    
    # Cuisine descriptions
    food_desc = {
        'chinese': 'authentic Chinese hot pot and Sichuan cuisine dishes with rich spices',
        'japanese': 'fresh Japanese sushi and ramen with elegant presentation',
        'italian': 'authentic Italian pasta and pizza with rustic charm',
        'french': 'refined French gourmet cuisine with elegant plating',
        'american': 'comfortable American burgers and fries',
        'korean': 'Korean BBQ and bibimbap with vibrant colors',
        'mexican': 'vibrant Mexican tacos and nachos',
        'thai': 'aromatic Thai curry and noodle dishes',
        'cafe': 'artisanal coffee drinks with latte art',
        'bakery': 'freshly baked pastries and desserts',
        'bar': 'craft cocktails and drinks with stylish presentation',
    }.get(cuisine, 'appetizing gourmet dishes')
    
    # Material-specific
    material_focus = {
        'poster': 'stunning promotional poster design with bold headline',
        'flyer': 'eye-catching promotional flyer with special offer',
        'menu': 'elegant menu design with clear sections',
        'social': 'engaging social media post design',
        'business_card': 'professional business card layout',
        'sticker': 'fun sticker design for packaging',
    }.get(material, 'professional design')
    
    # Platform
    platform_note = ""
    if platform and platform in PLATFORMS:
        platform_note = f", {PLATFORMS[platform]['note']}"
    
    prompt = f"""{style_desc} restaurant {material_focus},
{colors} color scheme,
professional commercial food photography of {food_desc},
appetizing presentation with dramatic lighting,
commercial quality, high resolution{platform_note}"""
    
    return prompt


def call_nano_banana_api(prompt: str, size: str = "1024x1024") -> dict:
    """Call nano banana API to generate image."""
    if not HAS_REQUESTS:
        return {"error": "requests library not available", "prompt": prompt}
    
    headers = {
        "Authorization": f"Bearer {NANO_BANANA_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": "nano-banana",
        "prompt": prompt,
        "size": size,
        "quality": "standard",
        "style": "vivid"
    }
    
    try:
        response = requests.post(
            NANO_BANANA_API_URL,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error: {response.status_code}", "detail": response.text}
    except Exception as e:
        return {"error": str(e)}


def generate_prompts_file(data: dict, output_dir: Path) -> Path:
    """Generate a prompts markdown file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / f"prompts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    lines = []
    lines.append(f"# Catering Design Prompts - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"\n**Cuisine**: {data['cuisine']}")
    lines.append(f"**Material**: {data['material']}")
    lines.append(f"**Style**: {data['style']}")
    lines.append("")
    
    # All platforms
    all_platforms = list(PLATFORMS.keys())[:5]  # Top 5
    
    lines.append("## Prompts by Platform")
    lines.append("")
    
    for platform in all_platforms:
        prompt = generate_prompt(data, platform)
        size = PLATFORMS[platform]['size']
        lines.append(f"### {platform.title()} ({size})")
        lines.append("```")
        lines.append(prompt)
        lines.append("```")
        lines.append("")
    
    # Nano banana API call example
    main_prompt = generate_prompt(data, None)
    lines.append("## Nano Banana API Call")
    lines.append("")
    lines.append("```bash")
    lines.append(f'curl -X POST "https://api.nanobana.com/v1/images/generations" \\')
    lines.append(f'  -H "Authorization: Bearer $NANO_BANANA_API_KEY" \\')
    lines.append(f'  -H "Content-Type: application/json" \\')
    lines.append(f'  -d \'{{"model":"nano-banana","prompt":"{main_prompt[:100]}...","size":"1024x1024"}}\'')
    lines.append("```")
    
    filepath.write_text("\n".join(lines))
    return filepath


def main():
    parser = argparse.ArgumentParser(
        description="🍽️ Generate catering design prompts and images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic prompt generation
  python3 scripts/generate_images.py "italian restaurant poster new pasta"
  
  # Chinese prompt
  python3 scripts/generate_images.py "川菜火锅海报 辣"
  
  # Specific platform
  python3 scripts/generate_images.py "bubble tea" --platform xiaohongshu
  
  # All platforms
  python3 scripts/generate_images.py "cafe menu" --all-platforms
  
  # Save prompts to file
  python3 scripts/generate_images.py "pizza promotion" --save-prompts
  
  # Try API call (may need proper SSL)
  python3 scripts/generate_images.py "sushi" --api
        """
    )
    parser.add_argument("prompt", nargs="?", help="Design prompt (e.g., 'italian restaurant poster')")
    parser.add_argument("--all-platforms", action="store_true", help="Generate prompts for all platforms")
    parser.add_argument("--platform", help="Specific platform (wechat, xiaohongshu, douyin, a4, etc.)")
    parser.add_argument("--output", "-o", default="./catering_output", help="Output directory")
    parser.add_argument("--save-prompts", action="store_true", help="Save prompts to markdown file")
    parser.add_argument("--api", action="store_true", help="Try to call nano banana API")
    
    args = parser.parse_args()
    
    if not args.prompt:
        print(__doc__)
        sys.exit(1)
    
    # Parse request
    data = parse_request(args.prompt)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n🍽️  Catering Design Image Generator")
    print(f"{'='*60}")
    print(f"\n📋 Design Brief:")
    print(f"   🏷️  菜系: {data['cuisine']}")
    print(f"   📄 类型: {data['material']}")
    print(f"   🎨 风格: {data['style']}")
    print(f"   📝 原始: {args.prompt[:50]}...")
    
    # Generate prompts
    if args.all_platforms:
        platforms = list(PLATFORMS.keys())
    elif args.platform:
        platforms = [args.platform]
    else:
        platforms = [None]
    
    prompts = {p or 'main': generate_prompt(data, p) for p in platforms}
    
    print(f"\n📝 Generated Prompts:")
    print(f"{'='*60}")
    
    for name, prompt in prompts.items():
        platform_info = f" [{PLATFORMS.get(name, {}).get('size', '')}]" if name in PLATFORMS else ""
        print(f"\n[{name}{platform_info}]")
        print(f"{prompt}")
    
    # Save prompts
    if args.save_prompts:
        prompts_file = generate_prompts_file(data, output_dir)
        print(f"\n✅ Prompts saved to: {prompts_file}")
    
    # API call
    if args.api:
        print(f"\n{'='*60}")
        print("🎨 Calling Nano Banana API...")
        print(f"{'='*60}\n")
        
        for name, prompt in prompts.items():
            size = PLATFORMS.get(name, {}).get('size', '1024x1024') if name in PLATFORMS else '1024x1024'
            print(f"  🌐 Generating {name} ({size})...")
            
            result = call_nano_banana_api(prompt, size)
            
            if "error" in result:
                print(f"  ❌ Error: {result['error']}")
                if "prompt" in result:
                    print(f"  📝 Prompt (for manual use):")
                    print(f"     {result['prompt'][:150]}...")
            else:
                print(f"  ✅ Success! Image generated")
                # Save response
                resp_file = output_dir / f"response_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                resp_file.write_text(json.dumps(result, indent=2))
                print(f"  📁 Response saved: {resp_file}")
            
            time.sleep(1)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 Summary")
    print(f"{'='*60}")
    print(f"   输出目录: {output_dir.absolute()}")
    print(f"   生成数量: {len(prompts)}")
    
    if not args.api:
        print(f"\n💡 To generate images, use --api flag or copy prompts to nano banana")
        print(f"   或在 https://nanobana.com 使用生成的提示词")
    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
