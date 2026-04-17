#!/usr/bin/env python3
"""
Catering Design - Restaurant Poster Generator with Logo & Images
Combines dish name, price, member price, images and logo to create promotional posters.

Usage:
    # Interactive mode (recommended for first use)
    python3 scripts/generate_poster.py --interactive
    
    # Command line mode with all details
    python3 scripts/generter.py "麻辣火锅" 128 98 --logo logo.png --dish-image food.jpg
    
    # Use saved design template
    python3 scripts/generate_poster.py --template my_design.json --dish-image new_dish.jpg
    
    # Generate variations
    python3 scripts/generate_poster.py "新品披萨" 88 68 --logo logo.png --output ./posters --variations 3

For best results, run outside sandbox:
    cd /Users/heyloo/Documents/skill-creator
    python3 skills/public/catering-design/scripts/generate_poster.py
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from urllib.parse import quote
import webbrowser

# Nano Banana API Configuration
NANO_BANANA_API_URL = "https://api.nanobana.com/v1/images/generations"
NANO_BANANA_API_KEY = os.environ.get("NANO_BANANA_API_KEY", "sk-pXPWfyGsbemwJAA9n2AjwYczCCmK8")

# Design Templates
TEMPLATES = {
    'modern': {
        'name': '现代简约',
        'description': 'Clean minimalist design with focus on food',
        'layout': 'food_center',
        'colors': ['#E85D04', '#F48C06', '#FAA307', '#FFBA08'],
        'font_heading': 'Montserrat',
        'font_body': 'Open Sans',
    },
    'elegant': {
        'name': '高端优雅',
        'description': 'Sophisticated design for fine dining',
        'layout': 'food_top',
        'colors': ['#000000', '#1C1917', '#C0A062', '#FEF3C7'],
        'font_heading': 'Playfair Display',
        'font_body': 'Lato',
    },
    'playful': {
        'name': '活泼有趣',
        'description': 'Fun and energetic for casual dining',
        'layout': 'food_left',
        'colors': ['#EC4899', '#F472B6', '#F9A8D4', '#FDF2F8'],
        'font_heading': 'Quicksand',
        'font_body': 'Nunito',
    },
    'vintage': {
        'name': '复古经典',
        'description': 'Nostalgic warm design for traditional cuisine',
        'layout': 'food_center',
        'colors': ['#9D0208', '#DC2F02', '#E85D04', '#F48C06'],
        'font_heading': 'Playfair Display',
        'font_body': 'Merriweather',
    },
    'minimal': {
        'name': '极简主义',
        'description': 'Lots of white space, sophisticated simplicity',
        'layout': 'food_full',
        'colors': ['#334155', '#475569', '#94A3B8', '#E2E8F0'],
        'font_heading': 'Inter',
        'font_body': 'Inter',
    },
}

# Promotion Badge Styles
BADGE_STYLES = {
    'sale': {
        'text': 'SALE',
        'bg_color': '#EF4444',
        'text_color': '#FFFFFF',
    },
    'new': {
        'text': 'NEW',
        'bg_color': '#22C55E',
        'text_color': '#FFFFFF',
    },
    'hot': {
        'text': 'HOT',
        'bg_color': '#F97316',
        'text_color': '#FFFFFF',
    },
    'member': {
        'text': 'MEMBER',
        'bg_color': '#8B5CF6',
        'text_color': '#FFFFFF',
    },
    'limited': {
        'text': 'LIMITED',
        'bg_color': '#EC4899',
        'text_color': '#FFFFFF',
    },
}


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="🍽️ Generate restaurant promotional posters",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (recommended)
  python3 scripts/generate_poster.py --interactive
  
  # Quick poster generation
  python3 scripts/generate_poster.py "招牌牛排" 198 168 --logo restaurant.png
  
  # With dish image
  python3 scripts/generate_poster.py "新品披萨" 88 68 --logo logo.png --dish-image pizza.jpg
  
  # Generate all templates
  python3 scripts/generate_poster.py "麻辣香锅" 98 78 --logo logo.png --all-templates
  
  # Save design configuration
  python3 scripts/generate_poster.py "甜品套餐" 58 48 --logo logo.png --save-template my_design.json
        """
    )
    
    parser.add_argument("dish_name", nargs="?", help="Dish name (e.g., '招牌牛排')")
    parser.add_argument("price", nargs="?", type=float, help="Regular price (e.g., 198)")
    parser.add_argument("member_price", nargs="?", type=float, help="Member price (e.g., 168)")
    
    parser.add_argument("--logo", "-l", help="Path to restaurant logo file")
    parser.add_argument("--dish-image", "-d", help="Path to dish photo")
    parser.add_argument("--output", "-o", default="./poster_output", help="Output directory")
    parser.add_argument("--template", "-t", help="Use saved template JSON file")
    parser.add_argument("--save-template", help="Save configuration to JSON file")
    
    parser.add_argument("--style", choices=list(TEMPLATES.keys()), default='modern',
                        help="Design template style")
    parser.add_argument("--all-templates", action="store_true", 
                        help="Generate posters using all template styles")
    parser.add_argument("--variations", type=int, default=1,
                        help="Number of variations to generate")
    
    parser.add_argument("--promo-badge", choices=list(BADGE_STYLES.keys()),
                        help="Promotion badge style")
    parser.add_argument("--promo-text", help="Custom promotion text (e.g., '限时优惠')")
    
    parser.add_argument("--currency", default="¥", help="Currency symbol (default: ¥)")
    parser.add_argument("--description", help="Dish description or features")
    
    parser.add_argument("--interactive", "-i", action="store_true",
                        help="Interactive mode with guided prompts")
    parser.add_argument("--open-nano", action="store_true",
                        help="Open nano banana website with prompt")
    
    return parser.parse_args()


def interactive_mode():
    """Interactive mode for poster generation."""
    print("\n" + "="*60)
    print("🍽️  餐饮海报生成器 - 交互模式")
    print("="*60)
    
    # Collect dish information
    print("\n📝 请输入菜品信息：")
    dish_name = input("  菜品名称: ").strip()
    if not dish_name:
        print("  ❌ 菜品名称不能为空")
        return
    
    try:
        price = float(input("  原价 (¥): ").strip())
        member_price = input("  会员价 (¥, 可留空): ").strip()
        member_price = float(member_price) if member_price else None
    except ValueError:
        print("  ❌ 价格请输入数字")
        return
    
    description = input("  菜品描述 (可选): ").strip()
    
    # Logo
    print("\n🖼️  图片文件：")
    logo_path = input("  Logo 文件路径 (可选，直接回车跳过): ").strip()
    dish_image = input("  菜品图片路径 (可选，直接回车跳过): ").strip()
    
    # Template style
    print("\n🎨 选择设计风格：")
    for i, (key, tpl) in enumerate(TEMPLATES.items(), 1):
        print(f"  {i}. {tpl['name']} - {tpl['description']}")
    
    try:
        choice = int(input(f"\n  请选择 (1-{len(TEMPLATES)}, 默认 1): ").strip() or "1")
        style = list(TEMPLATES.keys())[choice - 1] if 1 <= choice <= len(TEMPLATES) else 'modern'
    except ValueError:
        style = 'modern'
    
    # Promotion badge
    print("\n🏷️  促销标签：")
    print("  0. 无标签")
    for i, (key, badge) in enumerate(BADGE_STYLES.items(), 1):
        print(f"  {i}. {badge['text']}")
    
    try:
        badge_choice = int(input(f"\n  请选择 (0-{len(BADGE_STYLES)}, 默认 0): ").strip() or "0")
        promo_badge = list(BADGE_STYLES.keys())[badge_choice - 1] if 1 <= badge_choice <= len(BADGE_STYLES) else None
    except ValueError:
        promo_badge = None
    
    # Generate
    print("\n" + "="*60)
    print("🎨 正在生成海报...")
    print("="*60 + "\n")
    
    return {
        'dish_name': dish_name,
        'price': price,
        'member_price': member_price,
        'description': description,
        'logo_path': logo_path if logo_path else None,
        'dish_image': dish_image if dish_image else None,
        'style': style,
        'promo_badge': promo_badge,
    }


def generate_prompt(data: dict) -> str:
    """Generate optimized prompt for poster generation."""
    dish = data['dish_name']
    price = data['price']
    member_price = data['member_price']
    style = data['style']
    promo_badge = data.get('promo_badge')
    description = data.get('description', '')
    
    template = TEMPLATES[style]
    colors = template['colors']
    
    # Style descriptions
    style_desc = {
        'modern': 'Clean contemporary restaurant poster design, minimalist aesthetic',
        'elegant': 'Sophisticated fine dining promotional poster, elegant atmosphere',
        'playful': 'Fun and energetic restaurant poster, vibrant casual dining style',
        'vintage': 'Warm nostalgic restaurant poster, classic timeless design',
        'minimal': 'Ultra-modern minimalist poster design, lots of white space',
    }.get(style, 'Professional restaurant poster design')
    
    # Promotion text
    promo_text = ""
    if promo_badge:
        badge = BADGE_STYLES[promo_badge]
        promo_text = f"with '{badge['text']}' promotional badge in {badge['bg_color']}"
    
    # Price display
    price_text = f"Price: {price}"
    if member_price:
        price_text += f", Member Price: {member_price}"
    
    prompt = f"""{style_desc},
{colors[0]} and {colors[1]} color scheme with {colors[2]} accent,
prominent text "{dish}" as main headline,
{price_text},
{dish} appetizing food photography,
professional commercial food photography,
{promo_text},
commercial quality, high resolution poster design,
print-ready, clean layout"""
    
    if description:
        prompt += f", featuring: {description}"
    
    return prompt


def generate_html_poster(data: dict, output_path: Path):
    """Generate HTML poster template that can be used for editing or printing."""
    dish = data['dish_name']
    price = data['price']
    member_price = data['member_price']
    style = data['style']
    promo_badge = data.get('promo_badge')
    description = data.get('description', '')
    logo_path = data.get('logo_path')
    dish_image = data.get('dish_image')
    
    template = TEMPLATES[style]
    colors = template['colors']
    fonts = f"'{template['font_heading']}', '{template['font_body']}'"
    
    # Discount calculation
    discount = ""
    if member_price and member_price < price:
        saving = price - member_price
        discount_pct = int((saving / price) * 100)
        discount = f"""
        <div class="discount-badge">
            <span class="save-text">SAVE</span>
            <span class="save-amount">¥{saving}</span>
        </div>
        """
    
    # Badge
    badge_html = ""
    if promo_badge:
        badge = BADGE_STYLES[promo_badge]
        badge_html = f"""
        <div class="promo-badge" style="background-color: {badge['bg_color']}; color: {badge['text_color']};">
            {badge['text']}
        </div>
        """
    
    # Logo
    logo_html = ""
    if logo_path and os.path.exists(logo_path):
        logo_html = f'<img src="file://{os.path.abspath(logo_path)}" alt="Logo" class="logo">'
    
    # Dish image
    dish_html = ""
    if dish_image and os.path.exists(dish_image):
        dish_html = f'<img src="file://{os.path.abspath(dish_image)}" alt="{dish}" class="dish-image">'
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{dish} - 促销海报</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family={template['font_heading'].replace(' ', '+')}&family={template['font_body'].replace(' ', '+')}&family=Noto+Sans+SC:wght@400;700&display=swap');
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: '{template['font_body']}', 'Noto Sans SC', sans-serif;
            background: #f0f0f0;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }}
        
        .poster {{
            width: 600px;
            height: 850px;
            background: linear-gradient(135deg, {colors[0]} 0%, {colors[1]} 100%);
            position: relative;
            overflow: hidden;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}
        
        .poster::before {{
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle, {colors[2]}33 0%, transparent 70%);
        }}
        
        .content {{
            position: relative;
            z-index: 1;
            padding: 40px;
            height: 100%;
            display: flex;
            flex-direction: column;
        }}
        
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 30px;
        }}
        
        .logo {{
            max-width: 100px;
            max-height: 50px;
        }}
        
        .promo-badge {{
            padding: 8px 20px;
            border-radius: 20px;
            font-family: '{template['font_heading']}', serif;
            font-weight: bold;
            font-size: 14px;
        }}
        
        .main {{
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
        }}
        
        .dish-name {{
            font-family: '{template['font_heading']}', serif;
            font-size: 48px;
            font-weight: bold;
            color: #FFFFFF;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            margin-bottom: 20px;
            line-height: 1.2;
        }}
        
        .dish-image {{
            max-width: 350px;
            max-height: 300px;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            margin-bottom: 20px;
        }}
        
        .description {{
            font-size: 16px;
            color: rgba(255,255,255,0.9);
            margin-bottom: 30px;
        }}
        
        .prices {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-bottom: 30px;
        }}
        
        .price-box {{
            text-align: center;
        }}
        
        .price-label {{
            font-size: 14px;
            color: rgba(255,255,255,0.8);
            margin-bottom: 5px;
        }}
        
        .price-value {{
            font-family: '{template['font_heading']}', serif;
            font-size: 36px;
            font-weight: bold;
            color: #FFFFFF;
        }}
        
        .member-price .price-value {{
            color: {colors[2]};
        }}
        
        .discount-badge {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: #FFFFFF;
            color: {colors[0]};
            padding: 10px 15px;
            border-radius: 10px;
        }}
        
        .save-text {{
            font-size: 12px;
            font-weight: bold;
        }}
        
        .save-amount {{
            font-size: 20px;
            font-weight: bold;
        }}
        
        .footer {{
            text-align: center;
            color: rgba(255,255,255,0.7);
            font-size: 12px;
            margin-top: auto;
        }}
        
        @media print {{
            body {{
                background: none;
                padding: 0;
            }}
            .poster {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="poster">
        <div class="content">
            <div class="header">
                {logo_html}
                {badge_html}
            </div>
            
            <div class="main">
                <h1 class="dish-name">{dish}</h1>
                {dish_html}
                {f'<p class="description">{description}</p>' if description else ''}
                
                <div class="prices">
                    <div class="price-box">
                        <div class="price-label">原价</div>
                        <div class="price-value">{data['currency']}{price:.0f}</div>
                    </div>
                    {f'<div class="price-box member-price"><div class="price-label">会员价</div><div class="price-value">{data["currency"]}{member_price:.0f}</div></div>' if member_price else ''}
                    {discount}
                </div>
            </div>
            
            <div class="footer">
                <p>更多优惠请关注我们的公众号</p>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html)
    return output_path


def generate_nano_prompt(data: dict) -> str:
    """Generate prompt specifically for nano banana image generation."""
    dish = data['dish_name']
    price = data['price']
    style = data['style']
    promo_badge = data.get('promo_badge')
    
    template = TEMPLATES[style]
    colors = template['colors']
    
    style_prompts = {
        'modern': 'Modern minimalist restaurant promotional poster, clean white and orange design',
        'elegant': 'Luxurious dark restaurant poster with gold and black accents, elegant fine dining',
        'playful': 'Vibrant pink restaurant poster, fun casual dining aesthetic',
        'vintage': 'Warm orange-red vintage restaurant poster, nostalgic 1950s diner style',
        'minimal': 'Clean white and gray minimalist poster design, contemporary restaurant',
    }
    
    prompt = f"""{style_prompts.get(style, 'Professional restaurant poster')},
prominent text "{dish}" displaying price {data['currency']}{price},
appetizing food photography of {dish},
commercial food photography quality,
professional poster layout with clear typography,
{dish} appetizing presentation,
high resolution, print-ready design"""
    
    if promo_badge:
        badge = BADGE_STYLES[promo_badge]
        prompt += f", '{badge['text']}' promotional badge visible"
    
    return prompt


def open_nano_banana(prompt: str):
    """Open nano banana website with the generated prompt."""
    encoded_prompt = quote(prompt, safe='')
    # Nano banana's image generation page
    url = f"https://nanobana.com/generate?prompt={encoded_prompt}"
    
    print(f"\n🌐 正在打开 nano banana...")
    webbrowser.open(url)


def save_config(data: dict, output_path: Path):
    """Save poster configuration to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 配置已保存到: {output_path}")


def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Interactive mode
    if args.interactive:
        data = interactive_mode()
        if not data:
            return
    elif not args.dish_name:
        print(__doc__)
        print("\n请使用交互模式：")
        print("  python3 scripts/generate_poster.py --interactive")
        print("\n或提供完整参数：")
        print('  python3 scripts/generate_poster.py "招牌牛排" 198 168 --logo logo.png')
        return
    else:
        # Command line mode
        data = {
            'dish_name': args.dish_name,
            'price': args.price,
            'member_price': args.member_price,
            'description': args.description,
            'logo_path': args.logo,
            'dish_image': args.dish_image,
            'style': args.style,
            'promo_badge': args.promo_badge,
            'currency': args.currency,
        }
    
    # Use template if provided
    if args.template and os.path.exists(args.template):
        with open(args.template, 'r', encoding='utf-8') as f:
            template_data = json.load(f)
        data.update(template_data)
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine templates to use
    templates_to_use = [data['style']]
    if args.all_templates:
        templates_to_use = list(TEMPLATES.keys())
    
    # Generate posters
    print(f"\n🍽️  餐饮海报生成器")
    print(f"{'='*60}")
    print(f"\n📋 菜品: {data['dish_name']}")
    print(f"   原价: {data['currency']}{data['price']}")
    if data['member_price']:
        print(f"   会员价: {data['currency']}{data['member_price']}")
    print(f"   风格: {TEMPLATES[data['style']]['name']}")
    if data.get('promo_badge'):
        print(f"   标签: {BADGE_STYLES[data['promo_badge']]['text']}")
    
    # Generate for each template
    for style in templates_to_use:
        data['style'] = style
        template = TEMPLATES[style]
        
        print(f"\n{'='*60}")
        print(f"🎨 正在生成: {template['name']}")
        print(f"{'='*60}")
        
        # Generate HTML poster
        html_file = output_dir / f"poster_{data['dish_name']}_{style}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        html_path = generate_html_poster(data, html_file)
        print(f"✅ HTML 海报: {html_path}")
        
        # Generate nano banana prompt
        prompt = generate_nano_prompt(data)
        print(f"\n📝 Nano Banana 提示词:")
        print(f"   {prompt[:100]}...")
        
        # Save prompt
        prompt_file = output_dir / f"prompt_{data['dish_name']}_{style}.txt"
        prompt_file.write_text(prompt)
        print(f"   已保存: {prompt_file}")
        
        # Open nano banana if requested
        if args.open_nano:
            open_nano_banana(prompt)
    
    # Save template
    if args.save_template:
        save_config(data, Path(args.save_template))
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 生成完成")
    print(f"{'='*60}")
    print(f"   输出目录: {output_dir.absolute()}")
    print(f"   生成数量: {len(templates_to_use)}")
    
    if not args.open_nano:
        print(f"\n💡 提示:")
        print(f"   1. 打开生成的 HTML 文件查看/打印海报")
        print(f"   2. 复制提示词到 nano banana 生成图片")
        print(f"   3. 使用 --open-nano 直接打开 nano banana")
    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
