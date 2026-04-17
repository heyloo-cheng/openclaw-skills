#!/usr/bin/env python3
"""
Catering Design - AI Image Prompt Generator
Generate optimized prompts for nano banana and other AI image generators.

Usage:
    python3 scripts/generate_prompts.py "poster italian restaurant new dish"
    python3 scripts/generate_prompts.py "menu cafe drinks" --style vintage --platform wechat
    python3 scripts/generate_prompts.py "social media bubble tea" --style playful --output prompts.txt
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Color palettes
COLOR_PALETTES = {
    'warm': {
        'Sunset Bistro': '#E85D04, #F48C06, #FAA307, #FFBA08',
        'Rustic Tuscan': '#9D0208, #DC2F02, #E85D04, #F48C06',
        'Golden Harvest': '#B45309, #D97706, #F59E0B, #FBBF24',
        'Spice Market': '#B91C1C, #DC2626, #EF4444, #F87171',
    },
    'fresh': {
        'Garden Fresh': '#15803D, #166534, #16A34A, #22C55E',
        'Ocean Mist': '#0369A1, #0EA5E9, #22D3EE, #A5F3FC',
        'Lemon Zest': '#EAB308, #FDE047, #FEF08A, #FFF7ED',
        'Matcha Tea': '#3F6212, #65A30D, #84CC16, #ECFCCB',
    },
    'elegant': {
        'Midnight Gold': '#000000, #1C1917, #C0A062, #FEF3C7',
        'Burgundy Classic': '#7F1D1D, #991B1B, #B91C1C, #FECACA',
        'Charcoal Copper': '#1F2937, #374151, #B45309, #D97706',
        'Slate Elegance': '#334155, #475569, #94A3B8, #E2E8F0',
    },
    'playful': {
        'Candy Shop': '#EC4899, #F472B6, #F9A8D4, #FDF2F8',
        'Retro Diner': '#EF4444, #F59E0B, #22C55E, #3B82F6',
        'Popsicle Summer': '#F97316, #FB923C, #FDBA74, #FED7AA',
        'Rainbow Fruit': '#EF4444, #EAB308, #22C55E, #3B82F6',
    },
    'cafe': {
        'Barista Brown': '#5D4037, #795548, #8D6E63, #D7CCC8',
        'Latte Art': '#A1887F, #BCAAA4, #D7CCC8, #EFEBE9',
        'Espresso Dark': '#212121, #424242, #616161, #BDBDBD',
        'Mocha Match': '#4E342E, #6D4C41, #8D6E63, #A1887F',
    }
}

# Typography pairings
FONT_PAIRINGS = {
    'vintage': {'heading': 'Playfair Display', 'body': 'Lato'},
    'modern': {'heading': 'Montserrat', 'body': 'Open Sans'},
    'asian': {'heading': 'Noto Serif SC', 'body': 'Noto Sans SC'},
    'casual': {'heading': 'Quicksand', 'body': 'Nunito'},
    'bold': {'heading': 'Oswald', 'body': 'Roboto'},
    'luxury': {'heading': 'Bodoni Moda', 'body': 'DM Sans'},
    'handwritten': {'heading': 'Pacifico', 'body': 'Quicksand'},
    'cafe': {'heading': 'Bitter', 'body': 'Open Sans'},
    'industrial': {'heading': 'Barlow Condensed', 'body': 'Barlow'},
}

# Design styles
DESIGN_STYLES = {
    'vintage': 'Vintage 1950s diner aesthetic, warm nostalgic feel',
    'modern': 'Clean contemporary design, minimalist approach',
    'minimal': 'Modern minimalist, lots of white space',
    'rustic': 'Rustic farm-to-table, earthy textures',
    'industrial': 'Urban industrial, raw materials',
    'elegant': 'Sophisticated fine dining, elegant atmosphere',
    'playful': 'Fun and energetic, cartoon illustration style',
    'asian': 'Asian fusion, traditional elements with modern twist',
    'mediterranean': 'Mediterranean breeze, coastal colors',
    'french': 'French bistro classic, timeless elegance',
    'luxury': 'Premium and exclusive, gold accents',
    'scandinavian': 'Nordic clean, functional design',
}

# Platform specifications
PLATFORM_SPECS = {
    'wechat': {'ratio': '4:5', 'size': '1080×1350', 'name': 'WeChat Moments'},
    'xiaohongshu': {'ratio': '1:1 or 9:16', 'size': '1080×1080 or 1080×1920', 'name': 'Xiaohongshu'},
    'instagram': {'ratio': '1:1', 'size': '1080×1080', 'name': 'Instagram Post'},
    'instagram_story': {'ratio': '9:16', 'size': '1080×1920', 'name': 'Instagram Story'},
    'douyin': {'ratio': '9:16', 'size': '1080×1920', 'name': 'Douyin'},
    'a4': {'ratio': '1:1.414', 'size': '2480×3508', 'name': 'A4 Print'},
    'a3': {'ratio': '1:1.414', 'size': '3508×4961', 'name': 'A3 Print'},
    'menu': {'ratio': '8.5:11', 'size': '2550×3300', 'name': 'Letter Menu'},
    'business_card': {'ratio': '1.75:1', 'size': '1050×600', 'name': 'Business Card'},
}

# Material types
MATERIAL_TYPES = {
    'poster': {
        'description': 'promotional poster',
        'elements': ['strong headline', 'hero food image', 'call-to-action', 'brand elements'],
        'sizes': ['A4', 'A3', 'Square'],
    },
    'flyer': {
        'description': 'distribution flyer',
        'elements': ['promotional text', 'special offer', 'contact info', 'logo'],
        'sizes': ['A5', 'A4'],
    },
    'menu': {
        'description': 'restaurant menu',
        'elements': ['categories', 'item names', 'prices', 'descriptions', 'dietary icons'],
        'sizes': ['Single Page', 'Fold-out', 'Book'],
    },
    'social': {
        'description': 'social media post',
        'elements': ['visual focus', 'text overlay', 'brand colors', 'engagement element'],
        'sizes': ['1:1', '9:16', '4:5'],
    },
    'business_card': {
        'description': 'business card',
        'elements': ['logo', 'name', 'title', 'contact info'],
        'sizes': ['Standard 3.5×2'],
    },
    'sticker': {
        'description': 'decal/sticker',
        'elements': ['fun graphic', 'logo', 'catchphrase'],
        'sizes': ['Round', 'Square', 'Die-cut'],
    },
}


def parse_request(request: str) -> dict:
    """Parse user request into structured data."""
    request_lower = request.lower()
    
    # Detect cuisine/food type
    cuisines = {
        'chinese': ['chinese', '中餐', '川菜', '粤菜', '东北菜'],
        'japanese': ['japanese', '日本料理', '寿司', '拉面'],
        'italian': ['italian', '意大利', '披萨', '意面'],
        'french': ['french', '法餐', '法国菜'],
        'american': ['american', '美式', '汉堡', '快餐'],
        'korean': ['korean', '韩国', '烤肉'],
        'mexican': ['mexican', '墨西哥', '塔可'],
        'thai': ['thai', '泰国', '泰餐'],
        'mediterranean': ['mediterranean', '地中海'],
        'cafe': ['cafe', '咖啡', '咖啡厅', '咖啡店'],
        'bakery': ['bakery', '面包', '烘焙', '甜品'],
        'bar': ['bar', '酒吧', '酒', '精酿'],
    }
    
    detected_cuisine = 'modern fusion'  # default
    for cuisine, keywords in cuisines.items():
        if any(kw in request_lower for kw in keywords):
            detected_cuisine = cuisine
            break
    
    # Detect material type
    materials = {
        'poster': ['poster', '海报', '宣传画'],
        'flyer': ['flyer', '传单', '宣传单'],
        'menu': ['menu', '菜单', '价目表'],
        'social': ['social', '社交媒体', '小红书', '朋友圈'],
        'business_card': ['business card', '名片'],
        'sticker': ['sticker', '贴纸', '标签'],
    }
    
    detected_material = 'poster'  # default
    for material, keywords in materials.items():
        if any(kw in request_lower for kw in keywords):
            detected_material = material
            break
    
    # Detect style
    styles = {
        'vintage': ['vintage', '复古', '怀旧'],
        'modern': ['modern', '现代', '摩登'],
        'minimal': ['minimal', '极简', '简约'],
        'rustic': ['rustic', '乡村', '田园'],
        'elegant': ['elegant', '优雅', '精致'],
        'playful': ['playful', '有趣', '活泼', '卡通'],
        'luxury': ['luxury', '高端', '奢华'],
        'industrial': ['industrial', '工业'],
    }
    
    detected_style = 'modern'  # default
    for style, keywords in styles.items():
        if any(kw in request_lower for kw in keywords):
            detected_style = style
            break
    
    # Detect platform
    platforms = {
        'wechat': ['wechat', '微信', '朋友圈'],
        'xiaohongshu': ['xiaohongshu', '小红书', 'RED'],
        'instagram': ['instagram', 'INS'],
        'instagram_story': ['story', '快拍'],
        'douyin': ['douyin', '抖音', 'TikTok'],
        'print': ['print', '打印', '印刷', 'A4', 'A3'],
    }
    
    detected_platform = 'a4'  # default
    for platform, keywords in platforms.items():
        if any(kw in request_lower for kw in keywords):
            detected_platform = platform
            break
    
    # Extract specific dishes/items if mentioned
    import re
    dish_pattern = r'(?:dish|special|menu|item|food|产品|菜品|菜品|套餐)'
    dishes = re.findall(dish_pattern, request_lower)
    
    return {
        'cuisine': detected_cuisine,
        'material': detected_material,
        'style': detected_style,
        'platform': detected_platform,
        'original_request': request,
        'dishes': dishes,
    }


def select_color_palette(cuisine: str, style: str) -> str:
    """Select appropriate color palette."""
    style_map = {
        'vintage': 'warm',
        'rustic': 'warm',
        'modern': 'elegant',
        'minimal': 'elegant',
        'elegant': 'elegant',
        'luxury': 'elegant',
        'playful': 'playful',
        'cafe': 'cafe',
        'industrial': 'elegant',
    }
    
    palette_category = style_map.get(style, 'elegant')
    palettes = COLOR_PALETTES.get(palette_category, COLOR_PALETTES['elegant'])
    
    # Select first palette in category
    palette_name = list(palettes.keys())[0]
    return palettes[palette_name]


def select_font_pairing(style: str) -> dict:
    """Select font pairing based on style."""
    return FONT_PAIRINGS.get(style, FONT_PAIRINGS['modern'])


def generate_poster_prompt(data: dict) -> str:
    """Generate poster prompt."""
    cuisine = data['cuisine']
    style = data['style']
    colors = select_color_palette(cuisine, style)
    fonts = select_font_pairing(style)
    
    style_desc = DESIGN_STYLES.get(style, DESIGN_STYLES['modern'])
    
    prompt = f"""{style_desc} restaurant poster design,
{colors} color scheme,
{fonts['heading']} typography for headlines,
{fonts['body']} for body text,
appetizing food photography of {cuisine} cuisine dishes,
professional commercial quality,
dramatic lighting,
clear call-to-action text space,
high resolution 300 DPI,
A4 poster format"""
    
    return prompt


def generate_menu_prompt(data: dict) -> str:
    """Generate menu design prompt."""
    cuisine = data['cuisine']
    style = data['style']
    colors = select_color_palette(cuisine, style)
    fonts = select_font_pairing(style)
    
    prompt = f"""{cuisine.title()} restaurant menu design,
{style} aesthetic,
{colors} color palette,
{fonts['heading']} for section headers,
{fonts['body']} for item descriptions,
elegant layout with categories,
prices clearly displayed,
dietary icons included,
professional menu design,
high resolution,
single page format"""
    
    return prompt


def generate_social_prompt(data: dict) -> str:
    """Generate social media post prompt."""
    cuisine = data['cuisine']
    style = data['style']
    platform = data['platform']
    colors = select_color_palette(cuisine, style)
    
    specs = PLATFORM_SPECS.get(platform, PLATFORM_SPECS['wechat'])
    
    prompt = f"""{specs['name']} social media post,
{style} {cuisine} restaurant content,
{colors} color scheme,
vertical {specs['ratio']} aspect ratio ({specs['size']}),
appetizing food photography,
bold text overlay space,
contemporary social media aesthetic,
engaging visual,
high resolution,
mobile-optimized design"""
    
    return prompt


def generate_material_prompt(data: dict) -> str:
    """Generate appropriate prompt based on material type."""
    material = data['material']
    
    prompts = {
        'poster': generate_poster_prompt(data),
        'flyer': generate_poster_prompt(data),
        'menu': generate_menu_prompt(data),
        'social': generate_social_prompt(data),
    }
    
    return prompts.get(material, generate_poster_prompt(data))


def generate_all_platforms_prompts(data: dict) -> dict:
    """Generate prompts for multiple platforms."""
    cuisine = data['cuisine']
    style = data['style']
    colors = select_color_palette(cuisine, style)
    
    prompts = {}
    
    # Social platforms
    for platform in ['wechat', 'xiaohongshu', 'instagram', 'douyin']:
        specs = PLATFORM_SPECS[platform]
        prompts[f"social_{platform}"] = f"""{specs['name']} post,
{style} {cuisine} content,
{colors},
vertical {specs['ratio']} format,
engaging food visual,
text overlay area,
social media optimized,
high resolution"""
    
    # Print materials
    for platform in ['a4', 'a3']:
        specs = PLATFORM_SPECS[platform]
        prompts[f"print_{platform}"] = f"""{specs['name']} poster,
{style} {cuisine} design,
{colors},
professional print quality,
{300 if platform == 'a3' else 300} DPI,
high resolution"""
    
    return prompts


def generate_design_system(data: dict) -> dict:
    """Generate complete design system."""
    cuisine = data['cuisine']
    style = data['style']
    
    colors = select_color_palette(cuisine, style)
    fonts = select_font_pairing(style)
    
    return {
        'cuisine': cuisine,
        'style': style,
        'color_palette': colors,
        'fonts': fonts,
        'design_style': DESIGN_STYLES.get(style),
    }


def generate_markdown_report(data: dict, prompts: dict, design_system: dict) -> str:
    """Generate markdown report."""
    lines = []
    
    lines.append(f"# {data['cuisine'].title()} {data['material'].title()} Design System")
    lines.append(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Style**: {data['style']}")
    lines.append(f"**Platform**: {data['platform']}")
    
    lines.append("\n## Design System")
    lines.append(f"\n**Color Palette**: {design_system['color_palette']}")
    lines.append(f"\n**Typography**:")
    lines.append(f"- Heading: {design_system['fonts']['heading']}")
    lines.append(f"- Body: {design_system['fonts']['body']}")
    
    lines.append("\n## AI Image Prompts")
    
    for name, prompt in prompts.items():
        lines.append(f"\n### {name.replace('_', ' ').title()}")
        lines.append("```")
        lines.append(prompt)
        lines.append("```")
    
    return "\n".join(lines)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nExamples:")
        print('  python3 scripts/generate_prompts.py "poster italian restaurant new pasta"')
        print('  python3 scripts/generate_prompts.py "menu cafe drinks" --style vintage --platform wechat')
        print('  python3 scripts/generate_prompts.py "social bubble tea" --all-platforms --output prompts.md')
        sys.exit(1)
    
    # Parse arguments
    request = sys.argv[1]
    all_platforms = False
    output_file = None
    
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--all-platforms':
            all_platforms = True
            i += 1
        elif sys.argv[i] == '--output' and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--style' and i + 1 < len(sys.argv):
            # Override style
            sys.argv[1] = f"{request} {sys.argv[i+1]}"
            i += 2
        elif sys.argv[i] == '--platform' and i + 1 < len(sys.argv):
            # Override platform
            sys.argv[1] = f"{request} {sys.argv[i+1]}"
            i += 2
        else:
            i += 1
    
    # Parse request
    data = parse_request(request)
    
    # Generate prompts
    if all_platforms:
        prompts = generate_all_platforms_prompts(data)
    else:
        prompts = {'main': generate_material_prompt(data)}
    
    # Generate design system
    design_system = generate_design_system(data)
    
    # Generate report
    report = generate_markdown_report(data, prompts, design_system)
    
    # Output
    if output_file:
        Path(output_file).write_text(report)
        print(f"Prompts saved to: {output_file}")
    else:
        print(report)


if __name__ == '__main__':
    main()
