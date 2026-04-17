#!/usr/bin/env python3
"""
Mobile Design System Generator
Generate complete design systems for mobile and web projects.

Usage:
    python3 scripts/generate_design_system.py "<product_type> <industry> <keywords>"
    python3 scripts/generate_design_system.py "beauty spa wellness elegant" --format markdown
    python3 scripts/generate_design_system.py "beauty spa" --persist --output design-system/
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
try:
    from data.design_data import (
        DESIGN_STYLES, COLOR_PALETTES, FONT_PAIRINGS, 
        CHART_TYPES, ANTI_PATTERNS
    )
except ImportError:
    # Fallback inline data if import fails
    from .design_data_inline import (
        DESIGN_STYLES, COLOR_PALETTES, FONT_PAIRINGS,
        CHART_TYPES, ANTI_PATTERNS
    )


def analyze_request(request: str) -> dict:
    """Extract key information from user request."""
    request_lower = request.lower()
    
    # Detect product type
    product_types = {
        'saas': ['saas', 'software', 'dashboard', 'admin', 'tool'],
        'ecommerce': ['shop', 'store', 'commerce', 'buy', 'sell', 'product'],
        'portfolio': ['portfolio', 'showcase', 'personal', 'gallery'],
        'blog': ['blog', 'article', 'news', 'publish', 'content'],
        'landing': ['landing', 'landing page', 'promotion', 'campaign'],
        'mobile_app': ['app', 'mobile', 'ios', 'android', 'react native'],
        'dashboard': ['dashboard', 'analytics', 'stats', 'metrics'],
        'social': ['social', 'community', 'network', 'chat', 'messaging'],
        'food': ['food', 'restaurant', 'delivery', 'menu', 'dining'],
        'fitness': ['fitness', 'health', 'workout', 'exercise', 'gym'],
        'travel': ['travel', 'hotel', 'booking', 'trip', 'vacation'],
        'education': ['education', 'course', 'learning', 'tutorial', 'school'],
        'finance': ['finance', 'banking', 'payment', 'crypto', 'wallet'],
        'entertainment': ['entertainment', 'video', 'music', 'game', 'streaming'],
        'beauty': ['beauty', 'spa', 'wellness', 'makeup', 'skincare', 'salon'],
        'real_estate': ['real estate', 'property', 'housing', 'apartment', 'rent'],
    }
    
    detected_product = 'saas'  # default
    for product, keywords in product_types.items():
        if any(kw in request_lower for kw in keywords):
            detected_product = product
            break
    
    # Detect industry
    industries = {
        'technology': ['tech', 'software', 'ai', 'developer', 'coding'],
        'healthcare': ['health', 'medical', 'doctor', 'hospital', 'wellness'],
        'finance': ['finance', 'bank', 'crypto', 'investment', 'trading'],
        'education': ['education', 'learning', 'course', 'tutoring'],
        'entertainment': ['entertainment', 'movie', 'music', 'game', 'streaming'],
        'retail': ['retail', 'shop', 'store', 'fashion', 'clothing'],
        'food': ['food', 'restaurant', 'delivery', 'catering'],
        'travel': ['travel', 'hotel', 'booking', 'tourism'],
        'real_estate': ['real estate', 'property', 'housing', 'apartment'],
        'beauty': ['beauty', 'spa', 'salon', 'makeup', 'skincare'],
        'sports': ['sports', 'fitness', 'workout', 'gym', 'athlete'],
        'news': ['news', 'journalism', 'media', 'publishing'],
    }
    
    detected_industry = 'technology'  # default
    for industry, keywords in industries.items():
        if any(kw in request_lower for kw in keywords):
            detected_industry = industry
            break
    
    # Detect tone/keywords
    tones = []
    tone_keywords = {
        'professional': ['professional', 'business', 'corporate', 'enterprise'],
        'playful': ['playful', 'fun', 'cute', 'kids', 'toy'],
        'luxury': ['luxury', 'premium', 'elegant', 'high-end', 'refined'],
        'modern': ['modern', 'contemporary', 'sleek', 'clean'],
        'minimal': ['minimal', 'minimalist', 'simple', 'minimalism'],
        'bold': ['bold', 'strong', 'powerful', 'impactful'],
        'warm': ['warm', 'cozy', 'friendly', 'inviting'],
        'tech': ['tech', 'futuristic', 'innovative', 'cutting-edge'],
        'natural': ['natural', 'organic', 'earth', 'eco', 'green'],
        'retro': ['retro', 'vintage', 'classic', 'nostalgic'],
    }
    
    for tone, keywords in tone_keywords.items():
        if any(kw in request_lower for kw in keywords):
            tones.append(tone)
    
    if not tones:
        tones = ['modern', 'professional']
    
    return {
        'product_type': detected_product,
        'industry': detected_industry,
        'tones': tones,
        'original_request': request
    }


def recommend_pattern(product_type: str) -> str:
    """Recommend a design pattern based on product type."""
    patterns = {
        'saas': 'Dashboard-First',
        'ecommerce': 'Product-First',
        'portfolio': 'Content-Heavy',
        'blog': 'Content-Heavy',
        'landing': 'Marketing-First',
        'mobile_app': 'Task-Focused',
        'dashboard': 'Dashboard-First',
        'social': 'Feed-First',
        'food': 'Visual-First',
        'fitness': 'Action-First',
        'travel': 'Visual-First',
        'education': 'Content-Heavy',
        'finance': 'Trust-First',
        'entertainment': 'Visual-First',
        'beauty': 'Visual-First',
        'real_estate': 'Visual-First',
    }
    return patterns.get(product_type, 'Service-First')


def select_style(tones: list, industry: str) -> str:
    """Select the best design style based on tones and industry."""
    style_scores = {}
    
    for style, data in DESIGN_STYLES.items():
        score = 0
        # Score based on tone matches
        for tone in tones:
            if tone in data.get('tones', []):
                score += 3
        # Industry bonus
        if industry in data.get('industries', []):
            score += 2
        
        style_scores[style] = score
    
    # Return highest scoring style
    best_style = max(style_scores, key=style_scores.get)
    return best_style


def select_color_palette(industry: str, style: str) -> dict:
    """Select the best color palette based on industry and style."""
    industry_map = {
        'technology': 'SaaS',
        'healthcare': 'Healthcare',
        'finance': 'Fintech',
        'education': 'Service',
        'entertainment': 'Gaming',
        'retail': 'E-commerce',
        'food': 'Service',
        'travel': 'Service',
        'real_estate': 'Service',
        'beauty': 'Beauty/Spa',
        'sports': 'Gaming',
        'news': 'Blog',
    }
    
    category = industry_map.get(industry, 'SaaS')
    
    # Get palettes for this category
    palettes = COLOR_PALETTES.get(category, COLOR_PALETTES['SaaS'])
    
    # For certain styles, prefer specific palettes
    if style == 'Minimalism':
        # Prefer minimal palettes
        for palette in palettes:
            if 'Minimal' in palette.get('name', ''):
                return palette
    
    return palettes[0] if palettes else None


def select_font_pairing(tones: list, style: str) -> dict:
    """Select the best font pairing based on tones and style."""
    tone_to_style = {
        'luxury': 'Elegant',
        'modern': 'Geometric',
        'professional': 'Modern',
        'playful': 'Friendly',
        'tech': 'Tech',
        'minimal': 'Minimal',
        'warm': 'Warm',
        'bold': 'Bold',
    }
    
    # Map tone to font style
    font_style = 'Modern'  # default
    for tone in tones:
        if tone in tone_to_style:
            font_style = tone_to_style[tone]
            break
    
    # Get fonts for this style
    fonts = FONT_PAIRINGS.get(font_style, FONT_PAIRINGS['Modern'])
    
    return fonts[0] if fonts else None


def select_effects(style: str) -> dict:
    """Select appropriate effects based on design style."""
    style_effects = {
        'Glassmorphism': {
            'shadows': ['0 8rpx 32rpx rgba(0, 0, 0, 0.08)'],
            'borders': ['inset 0 1rpx 0 rgba(255, 255, 255, 0.8)'],
            'backdrop': 'blur(20rpx)',
            'radius': '16rpx',
            'gradient': 'linear-gradient(135deg, rgba(255,255,255,0.4) 0%, rgba(255,255,255,0) 100%)'
        },
        'Neumorphism': {
            'shadows': ['0 8rpx 32rpx rgba(0, 0, 0, 0.1)', 'inset 0 2rpx 4rpx rgba(255, 255, 255, 0.5)'],
            'borders': ['none'],
            'backdrop': 'none',
            'radius': '24rpx',
            'gradient': 'none'
        },
        'Minimalism': {
            'shadows': ['0 2rpx 8rpx rgba(0, 0, 0, 0.04)'],
            'borders': ['1rpx solid #E5E7EB'],
            'backdrop': 'none',
            'radius': '8rpx',
            'gradient': 'none'
        },
        'Default': {
            'shadows': ['0 4rpx 16rpx rgba(0, 0, 0, 0.08)'],
            'borders': ['none'],
            'backdrop': 'none',
            'radius': '12rpx',
            'gradient': 'none'
        }
    }
    
    return style_effects.get(style, style_effects['Default'])


def generate_design_system(request: str, format: str = 'markdown', persist: bool = False, output_dir: str = None):
    """Generate a complete design system based on user request."""
    analysis = analyze_request(request)
    
    # Select components
    pattern = recommend_pattern(analysis['product_type'])
    style = select_style(analysis['tones'], analysis['industry'])
    palette = select_color_palette(analysis['industry'], style)
    fonts = select_font_pairing(analysis['tones'], style)
    effects = select_effects(style)
    
    # Get anti-patterns for this style
    style_anti_patterns = ANTI_PATTERNS.get(style, ANTI_PATTERNS.get('General', []))
    
    # Build the design system
    design_system = {
        'name': analysis['original_request'].title(),
        'pattern': pattern,
        'style': style,
        'industry': analysis['industry'],
        'product_type': analysis['product_type'],
        'tones': analysis['tones'],
        'generated_at': datetime.now().isoformat(),
        'color_palette': palette,
        'font_pairing': fonts,
        'effects': effects,
        'anti_patterns': style_anti_patterns
    }
    
    # Generate output
    if format == 'markdown':
        output = generate_markdown(design_system)
    elif format == 'json':
        import json
        output = json.dumps(design_system, indent=2)
    else:
        output = generate_markdown(design_system)
    
    # Persist if requested
    if persist:
        persist_design_system(design_system, output_dir or 'design-system')
        output += f"\n\nDesign system has been persisted to: {output_dir or 'design-system'}"
    
    return output


def generate_markdown(ds: dict) -> str:
    """Generate markdown documentation for the design system."""
    lines = []
    
    lines.append(f"# {ds['name']} - Design System")
    lines.append("")
    lines.append(f"**Pattern**: {ds['pattern']}")
    lines.append(f"**Style**: {ds['style']}")
    lines.append(f"**Industry**: {ds['industry']}")
    lines.append(f"**Generated**: {ds['generated_at']}")
    lines.append("")
    
    # Color Palette
    lines.append("## Color Palette")
    lines.append("")
    if ds.get('color_palette'):
        palette = ds['color_palette']
        lines.append(f"**{palette.get('name', 'Default')}** ({palette.get('category', '')})")
        lines.append("")
        lines.append("| Role | Color | CSS Variable |")
        lines.append("|------|-------|--------------|")
        for color in palette.get('colors', []):
            lines.append(f"| {color.get('role', '')} | {color.get('hex', '')} | {color.get('var', '')} |")
    
    lines.append("")
    
    # Typography
    lines.append("## Typography")
    lines.append("")
    if ds.get('font_pairing'):
        fonts = ds['font_pairing']
        lines.append(f"**Heading**: {fonts.get('heading', '')}")
        lines.append(f"**Body**: {fonts.get('body', '')}")
        lines.append(f"**Vibe**: {fonts.get('vibe', '')}")
        lines.append("")
        lines.append("### Font Sizes (Mobile)")
        lines.append("| Element | Size | Weight |")
        lines.append("|---------|------|--------|")
        lines.append("| H1 | 32px | Bold |")
        lines.append("| H2 | 24px | Semi-Bold |")
        lines.append("| H3 | 20px | Medium |")
        lines.append("| Body | 16px | Regular |")
        lines.append("| Caption | 12px | Regular |")
    
    lines.append("")
    
    # Effects
    lines.append("## Effects")
    lines.append("")
    effects = ds.get('effects', {})
    lines.append(f"**Border Radius**: {effects.get('radius', '12rpx')}")
    lines.append(f"**Backdrop**: {effects.get('backdrop', 'none')}")
    lines.append(f"**Shadows**: {', '.join(effects.get('shadows', []))}")
    
    lines.append("")
    
    # Anti-Patterns
    lines.append("## Anti-Patterns to Avoid")
    lines.append("")
    for anti in ds.get('anti_patterns', []):
        lines.append(f"- {anti}")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Implementation Tips")
    lines.append("")
    lines.append("1. Use CSS custom properties for colors")
    lines.append("2. Implement dark mode support")
    lines.append("3. Test at all responsive breakpoints")
    lines.append("4. Follow accessibility guidelines")
    
    return "\n".join(lines)


def persist_design_system(ds: dict, output_dir: str):
    """Persist the design system to files."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create MASTER.md
    master_content = generate_master_md(ds)
    (output_path / "MASTER.md").write_text(master_content)
    
    # Create design-tokens.json
    import json
    tokens = {
        'colors': ds.get('color_palette', {}).get('colors', []),
        'fonts': {
            'heading': ds.get('font_pairing', {}).get('heading', ''),
            'body': ds.get('font_pairing', {}).get('body', '')
        },
        'effects': ds.get('effects', {})
    }
    (output_path / "design-tokens.json").write_text(json.dumps(tokens, indent=2))
    
    # Create README.md
    readme_content = f"""# {ds['name']}

This is a generated design system for **{ds['industry']}** projects.

## Quick Start

```css
/* Import design tokens */
@import './design-tokens.css';

/* Use in your components */
.custom-element {{
  background-color: var(--primary);
  color: var(--on-primary);
  border-radius: {ds.get('effects', {}).get('radius', '12rpx')};
}}
```

## Files

- `MASTER.md` - Complete design system documentation
- `design-tokens.json` - CSS custom properties and design tokens
"""
    (output_path / "README.md").write_text(readme_content)
    
    print(f"Design system persisted to: {output_path}")


def generate_master_md(ds: dict) -> str:
    """Generate the MASTER.md file."""
    lines = []
    
    lines.append(f"# {ds['name']} - Design System")
    lines.append("")
    lines.append("## Brand Identity")
    lines.append(f"- **Tone**: {', '.join(ds.get('tones', []))}")
    lines.append(f"- **Industry**: {ds.get('industry', '')}")
    lines.append(f"- **Product Type**: {ds.get('product_type', '')}")
    lines.append(f"- **Pattern**: {ds.get('pattern', '')}")
    lines.append("")
    
    lines.append("## Visual Style")
    lines.append(f"- **Style**: {ds.get('style', '')}")
    lines.append("")
    
    if ds.get('color_palette'):
        palette = ds['color_palette']
        lines.append("### Color Palette")
        lines.append(f"**{palette.get('name', '')}**")
        lines.append("")
        lines.append("```css")
        for color in palette.get('colors', []):
            lines.append(f"  {color.get('var', '')}: {color.get('hex', '')};")
        lines.append("```")
    
    lines.append("")
    lines.append("## Typography")
    if ds.get('font_pairing'):
        fonts = ds['font_pairing']
        lines.append(f"- **Heading**: {fonts.get('heading', '')}")
        lines.append(f"- **Body**: {fonts.get('body', '')}")
    
    lines.append("")
    lines.append("## Effects")
    effects = ds.get('effects', {})
    lines.append(f"- **Border Radius**: {effects.get('radius', '')}")
    lines.append(f"- **Shadow**: {effects.get('shadows', [''])[0]}")
    
    lines.append("")
    lines.append("## Anti-Patterns")
    for anti in ds.get('anti_patterns', []):
        lines.append(f"- {anti}")
    
    lines.append("")
    lines.append("---")
    lines.append("*Generated by Mobile-Design Skill*")
    
    return "\n".join(lines)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nExamples:")
        print('  python3 scripts/generate_design_system.py "beauty spa wellness elegant"')
        print('  python3 scripts/generate_design_system.py "saas dashboard admin" --format markdown')
        print('  python3 scripts/generate_design_system.py "blog tech" --persist --output my-design-system')
        sys.exit(1)
    
    # Parse arguments
    request = sys.argv[1]
    format_type = 'markdown'
    persist = False
    output_dir = 'design-system'
    
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--format' and i + 1 < len(sys.argv):
            format_type = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--persist':
            persist = True
            i += 1
        elif sys.argv[i] == '--output' and i + 1 < len(sys.argv):
            output_dir = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    
    # Generate design system
    result = generate_design_system(request, format_type, persist, output_dir)
    print(result)


if __name__ == '__main__':
    main()
