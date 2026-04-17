---
name: mobile-design
description: Create distinctive, production-grade mobile interfaces with high design quality. Use this skill when the user asks to build mobile apps, mini programs, responsive layouts, or mobile-specific UI components (examples include iOS/Android apps, WeChat mini programs, mobile landing pages, touch interactions, and mobile-first designs). Generates creative, polished code that avoids generic AI aesthetics and is optimized for mobile experiences. Also includes Web UI/UX support with multiple frameworks.
license: Apache License 2.0
---

This skill guides creation of distinctive, production-grade mobile interfaces that avoid generic "AI slop" aesthetics. Implement real working code with exceptional attention to mobile-specific design details and creative choices.

**NEW: Web UI/UX Support Added!**
This skill now includes comprehensive Web UI/UX capabilities including design system generation, 50+ design styles, 97 color palettes, 57 font pairings, and support for React, Vue, Next.js, Tailwind CSS, and more!

The user provides mobile design requirements: a component, page, application, or interface to build for mobile platforms. They may include context about the target platform (iOS, Android, mini programs), device types, or technical constraints.

## Mobile Design Thinking

Before coding mobile interfaces, understand the mobile context and commit to a BOLD aesthetic direction:
- **Platform**: Which platform(s) - iOS, Android, WeChat mini program, or cross-platform (React Native, Flutter, uni-app)?
- **Use Context**: How do users hold the device? Thumb zone, one-handed vs two-handed use?
- **Tone**: Pick an extreme: glassmorphism, neumorphism, brutalist, retro mobile, futuristic HUD, organic/natural, luxury/refined, playful/toy-like, editorial/magazine. Commit fully to one direction.
- **Constraints**: Screen sizes, performance requirements, platform guidelines (Human Interface Guidelines, Material Design).
- **Differentiation**: What makes this UNFORGETTABLE on a mobile screen? What's the one interaction or visual that someone will remember?

**CRITICAL**: Mobile design requires understanding of touch ergonomics, gesture patterns, and platform conventions. Choose a clear conceptual direction and execute it with precision. Bold maximalism and refined minimalism both work - the key is intentionality and purposeful design for mobile contexts.

Then implement working code (React Native, Flutter, Vue/uni-app, SwiftUI, etc.) that is:
- Production-grade and functional on mobile devices
- Visually striking and memorable in mobile contexts
- Optimized for touch interactions and gesture controls
- Cohesive with platform conventions while maintaining unique aesthetic point-of-view
- Meticulously refined for small screens and finger-based navigation

## Mobile Aesthetics Guidelines

Mobile interfaces have unique constraints and opportunities. Focus on:

### Touch & Ergonomics

- **Thumb Zone Optimization**: Design for comfortable thumb reach. Primary actions should be in the bottom or center of the screen. Secondary actions can extend upward.
- **Touch Targets**: Minimum 44x44 points (iOS) or 48x48 dp (Android) for interactive elements. Larger is better for frequently used actions.
- **Gesture Awareness**: Support standard gestures (swipe, pinch, long-press, double-tap) but add custom gestures that surprise and delight.
- **Scroll & Bounce**: Embrace the natural scroll behavior. Use pull-to-refresh, infinite scroll, and snap-to-item patterns thoughtfully.
- **Haptic Feedback**: Integrate haptics for meaningful moments (successful actions, important notifications, boundary feedback).

### Typography for Mobile

- **Font Selection**: Choose fonts that are readable at small sizes but have distinctive character. Avoid generic system fonts.
- **Dynamic Type**: Support text scaling for accessibility. Use semantic type scales that adapt gracefully.
- **Hierarchy**: Clear visual hierarchy is crucial on small screens. Use size, weight, and color to establish content priority.
- **Line Length**: Optimal line length for mobile is 30-40 characters. Avoid full-width text blocks.

### Color & Theme

- **Dark Mode Native**: Design for both light and dark themes from the start. Dark mode saves battery on OLED screens and reduces eye strain.
- **Platform Color Conventions**: Respect platform-specific color meanings (green for success, red for error/danger across most platforms).
- **Contrast Ratios**: WCAG 2.1 AA minimum (4.5:1 for normal text, 3:1 for large text). Higher is better for outdoor visibility.
- **Adaptive Colors**: Colors that work across different ambient light conditions and screen technologies.

### Motion for Mobile

- **Platform Animation Standards**: iOS uses spring animations. Android uses material motion. Match the platform's feel while adding your unique touches.
- **Gesture-Driven Animation**: Animations that respond to finger movement create tactile connection.
- **Performance Priority**: 60fps is the target. Use GPU-accelerated properties (transform, opacity) over layout-triggering changes.
- **Loading States**: Creative loading indicators that match your aesthetic - not generic spinners.
- **Transition Patterns**: Smooth page transitions, modal presentations, and navigation flows that feel natural.

### Spatial Composition

- **Safe Areas**: Respect notches, home indicators, and corner radii. Use CSS safe-area-insets or platform equivalents.
- **Vertical Rhythm**: Consistent spacing system (4px, 8px, 16px, 24px, 32px, 40px, 48px) creates visual harmony.
- **Card-Based Layouts**: Cards are the dominant mobile pattern - use them meaningfully, not as containers for everything.
- **Full-Width Components**: Mobile benefits from edge-to-edge design patterns.
- **Negative Space**: Use generous spacing to reduce cognitive load on small screens.

### Platform-Specific Patterns

#### iOS (SwiftUI)
- NavigationSplitView, TabView, List, ScrollView
- Sheet presentations, context menus, pull-to-refresh
- SF Symbols integration, dynamic type support
- Safe area handling, gesture modifiers

#### Android (Compose)
- Scaffold, LazyColumn/LazyRow, Card, FloatingActionButton
- Material 3 theming, ripple effects, elevation
- Navigation component, gesture navigation support
- ConstraintLayout for complex layouts

#### WeChat Mini Programs
- rpx responsive units (750rpx = design width)
- WX components (view, scroll-view, swiper)
- WeChat login, payment integration
- Tab bar, navigation bar customization

#### Cross-Platform (React Native, Flutter, uni-app)
- Platform-aware components that adapt to each OS
- Platform-specific code paths when needed
- Consistent experience across platforms
- Platform-native performance

## Web UI/UX Support

**NEW!** This skill now includes comprehensive Web UI/UX capabilities. Use this when building websites, web applications, dashboards, landing pages, or any web-based interfaces.

### When to Use Web UI/UX Features

Reference these guidelines when:
- Building websites, landing pages, or web applications
- Creating dashboards, admin panels, or SaaS interfaces
- Designing e-commerce platforms or portfolios
- Implementing responsive web layouts
- Working with React, Vue, Next.js, or Tailwind CSS

### Rule Categories by Priority

| Priority | Category | Impact | Domain |
|----------|----------|--------|--------|
| 1 | Accessibility | CRITICAL | `ux` |
| 2 | Touch & Interaction | CRITICAL | `ux` |
| 3 | Performance | HIGH | `ux` |
| 4 | Layout & Responsive | HIGH | `ux` |
| 5 | Typography & Color | MEDIUM | `typography`, `color` |
| 6 | Animation | MEDIUM | `ux` |
| 7 | Style Selection | MEDIUM | `style`, `product` |
| 8 | Charts & Data | LOW | `chart` |

### Quick Reference

#### 1. Accessibility (CRITICAL)

- `color-contrast` - Minimum 4.5:1 ratio for normal text
- `focus-states` - Visible focus rings on interactive elements
- `alt-text` - Descriptive alt text for meaningful images
- `aria-labels` - aria-label for icon-only buttons
- `keyboard-nav` - Tab order matches visual order
- `form-labels` - Use label with for attribute

#### 2. Touch & Interaction (CRITICAL)

- `touch-target-size` - Minimum 44x44px touch targets
- `hover-vs-tap` - Use click/tap for primary interactions
- `loading-buttons` - Disable button during async operations
- `error-feedback` - Clear error messages near problem
- `cursor-pointer` - Add cursor-pointer to clickable elements

#### 3. Performance (HIGH)

- `image-optimization` - Use WebP, srcset, lazy loading
- `reduced-motion` - Check prefers-reduced-motion
- `content-jumping` - Reserve space for async content

#### 4. Layout & Responsive (HIGH)

- `viewport-meta` - width=device-width initial-scale=1
- `readable-font-size` - Minimum 16px body text on mobile
- `horizontal-scroll` - Ensure content fits viewport width
- `z-index-management` - Define z-index scale (10, 20, 30, 50)

#### 5. Typography & Color (MEDIUM)

- `line-height` - Use 1.5-1.75 for body text
- `line-length` - Limit to 65-75 characters per line
- `font-pairing` - Match heading/body font personalities

#### 6. Animation (MEDIUM)

- `duration-timing` - Use 150-300ms for micro-interactions
- `transform-performance` - Use transform/opacity, not width/height
- `loading-states` - Skeleton screens or spinners

#### 7. Style Selection (MEDIUM)

- `style-match` - Match style to product type
- `consistency` - Use same style across all pages
- `no-emoji-icons` - Use SVG icons, not emojis

#### 8. Charts & Data (LOW)

- `chart-type` - Match chart type to data type
- `color-guidance` - Use accessible color palettes
- `data-table` - Provide table alternative for accessibility

### Design System Generation

Generate complete design systems for any project:

```bash
# Generate design system (run via Claude Code)
/generate-design-system "<product_type> <industry> <keywords>"
```

**Example:**
```
/generate-design-system "beauty spa wellness elegant"
```

**Output includes:**
- Pattern recommendation (Service-First, Content-Heavy, etc.)
- Style selection (Minimalist, Glassmorphism, etc.)
- Color palette (5-7 colors with roles)
- Typography pairing (heading + body fonts)
- Effects (shadows, gradients, borders)
- Anti-patterns to avoid

### Design Styles (50+ Available)

| Style | Characteristics | Best For |
|-------|----------------|----------|
| Glassmorphism | Translucent backgrounds, blur effects | Tech, Modern, Premium |
| Claymorphism | 3D soft shapes, rounded corners | Playful, Kids, Toys |
| Minimalism | Lots of whitespace, simple shapes | Luxury, Fashion, Editorial |
| Brutalism | Raw, bold, sometimes chaotic | Art, Experimental, Youth |
| Neumorphism | Soft extruded shapes, subtle shadows | Tools, Dashboards, Utilities |
| Bento Grid | Grid-based, modular layouts | Portfolios, Dashboards |
| Dark Mode | Dark backgrounds, light text | Gaming, Media, Night Use |
| Skeuomorphism | Realistic textures, shadows | Games, Vintage, Retro |
| Flat Design | Simple, no shadows or gradients | Corporate, SaaS, Business |
| Retro/Vintage | Warm colors, textured backgrounds | Food, Hospitality, Lifestyle |
| Futuristic/HUD | Neon, dark backgrounds, tech feel | Gaming, Tech, AI |
| Organic/Natural | Soft curves, earth tones | Health, Wellness, Nature |
| Luxury/Refined | Black/white, serif fonts | High-end, Fashion, Jewelry |
| Playful/Toy-like | Bright colors, rounded everything | Kids, Entertainment, Games |
| Editorial/Magazine | Typography-focused, layouts | Blogs, Publications, Media |
| Cyberpunk | Neon pink/blue, grid lines | Gaming, Tech, Sci-fi |
| Swiss Style | Grid-based, bold typography | Corporate, Architecture |
| Bauhaus | Geometric, primary colors | Art, Design, Creative |
| Art Deco | Gold, black, geometric patterns | Luxury, Fashion, Hospitality |
| Scandinavian | White, wood, cozy | Furniture, Lifestyle, Home |

### Color Palettes (97 Available)

| Category | Count | Examples |
|----------|-------|----------|
| SaaS | 15 | Blue Professional, Tech Gradient |
| E-commerce | 12 | Fashion Forward, Bold Accent |
| Healthcare | 10 | Medical Blue, Trust Green |
| Beauty/Spa | 8 | Soft Pink, Natural Green |
| Fintech | 12 | Secure Purple, Wealth Gold |
| Gaming | 8 | Neon Colors, Dark Theme |
| Portfolio | 10 | Minimal Black, Creative Colors |
| Blog | 10 | Reading Friendly, Comfort |
| Service | 12 | Professional Gray, Warm Beige |

### Font Pairings (57 Available)

| Style | Heading Font | Body Font | Vibe |
|-------|--------------|-----------|------|
| Elegant | Playfair Display | Lato | Luxury, Editorial |
| Modern | Montserrat | Open Sans | Tech, Corporate |
| Bold | Oswald | Roboto | Strong, Industrial |
| Traditional | Merriweather | Source Sans Pro | Editorial, News |
| Geometric | Poppins | Inter | Tech, Startup |
| Friendly | Quicksand | Nunito | Playful, Kids |
| Minimal | Space Grotesk | DM Sans | Design, Creative |
| Classic | Crimson Text | Lora | Books, Literature |
| Tech | Exo 2 | Roboto | Gaming, Sci-fi |
| Warm | Bitter | Open Sans | Food, Hospitality |

### Framework Support

| Framework | Best For | Key Features |
|-----------|----------|--------------|
| **React** | Dynamic web apps | Components, Hooks, State |
| **Vue** | Progressive web apps | Composition API, Pinia |
| **Next.js** | Full-stack React | SSR, Routing, Images |
| **Tailwind CSS** | Utility-first styling | Responsive, Dark Mode |
| **HTML/CSS** | Static sites | Semantics, Layouts |
| **shadcn/ui** | Modern React apps | Components, Theme, Forms |

---

## Component Design Patterns

### Mobile Navigation

- **Bottom Tab Bar**: Primary navigation pattern. 3-5 tabs maximum. Use distinct icons and concise labels.
- **Hamburger Menu**: Secondary navigation. Works for complex apps with many sections.
- **Stack Navigation**: Drill-down content. Maintain clear hierarchy.
- **Drawer/Sidebar**: Alternative to tabs for apps with complex information architecture.
- **Floating Action Button**: Prominent primary action. Not for navigation.

### Mobile Lists & Feeds

- **Plain Lists**: Simple, readable content. Good for settings, contacts, directories.
- **Grouped Lists**: Related content sections with headers.
- **Cards**: Rich content with images, actions, and metadata.
- **Swipe Actions**: Reveal actions on swipe (edit, delete, archive).
- **Pull-to-Refresh**: Standard refresh pattern. Customize the indicator.
- **Infinite Scroll**: Loading more content as users scroll. Add visual loading states.

### Mobile Forms & Input

- **Floating Label**: Text field with label that moves when focused. Clean and space-efficient.
- **Auto-complete/Auto-correct**: Helpful but not intrusive.
- **Date/Time Pickers**: Platform-native pickers for date, time, and ranges.
- **Password Fields**: Show/hide toggle, strength indicator.
- **Validation**: Inline validation as users type. Clear error messages.

### Mobile Cards & Content

- **Hero Cards**: Full-width featured content at top of screens.
- **Content Cards**: Standard card with image, title, subtitle, actions.
- **Swipe Cards**: Tinder-style horizontal swipe for content discovery.
- **Expandable Cards**: Tap to reveal more detail. Accordion patterns.
- **Image Cards**: Photo-focused cards with minimal text.

### Mobile Actions & Feedback

- **Buttons**: Primary, secondary, tertiary, destructive. Clear hierarchy.
- **Chips/Tags**: Small, tappable elements for categories, filters, selections.
- **Progress Indicators**: Linear, circular, or creative animations.
- **Toast/Snackbar**: Non-blocking notifications. Use sparingly.
- **Dialogs**: Alert, confirmation, and action sheets. Modal by default.

### Mobile Overlays & Modals

- **Bottom Sheets**: Slide up from bottom. Good for additional options, forms.
- **Full-Screen Modals**: For focused tasks, onboarding, content immersion.
- **Popovers/Menus**: Quick actions that don't navigate away.
- **Loading Overlays**: Full-screen or partial blocking states.

## Web Component Patterns

### Web Navigation

- **Navbar**: Horizontal navigation with logo, links, and actions.
- **Sidebar**: Vertical navigation for dashboards and admin panels.
- **Breadcrumb**: Hierarchical navigation indicator.
- **Pagination**: Page navigation for long lists.
- **Mega Menu**: Large dropdown menu with categories.

### Web Layouts

- **Hero Section**: Full-width intro with CTA.
- **Feature Grid**: Product/service highlights.
- **Content Sections**: Text + image alternating layout.
- **Card Grid**: Responsive card layout.
- **Footer**: Links, contact, social, legal.

### Web Forms

- **Input Fields**: With labels, validation, error states.
- **Select/Dropdown**: Single and multi-select.
- **Checkboxes/Radios**: Option selection.
- **File Upload**: Drag & drop or click to upload.
- **Form Layouts**: Single column, two column, wizard.

### Web Cards

- **Product Card**: Image, title, price, add to cart.
- **Profile Card**: Avatar, name, bio, actions.
- **Stats Card**: Number, label, trend indicator.
- **Testimonial Card**: Quote, author, avatar.
- **Blog Card**: Image, title, excerpt, read more.

### Web Tables

- **Data Table**: Sortable, filterable data display.
- **Pricing Table**: Feature comparison.
- **Comparison Table**: Side-by-side feature list.

---

## Screen Types

### Mobile Landing Pages

- **Hero Section**: Bold statement with clear value proposition.
- **Feature Highlights**: Concise benefit statements with icons/images.
- **Social Proof**: Testimonials, user counts, ratings.
- **CTA Sections**: Clear call-to-action buttons.
- **Footer**: Secondary links, contact info, social links.

### Mobile Dashboards

- **Summary Cards**: Key metrics at a glance.
- **Quick Actions**: Frequently used functions accessible.
- **Activity Feeds**: Recent actions, notifications, updates.
- **Charts/Graphs**: Simplified visualizations for mobile.
- **Date Pickers**: Quick time period selection.

### Mobile Commerce

- **Product Cards**: Image, title, price, rating, quick add.
- **Category Grids**: Visual product categories.
- **Shopping Cart**: Line items with quantity, price, total.
- **Checkout Flow**: Multi-step, progress indicator.
- **Order Tracking**: Visual timeline of order status.

### Mobile Profile/Settings

- **Header**: Avatar, name, bio, edit button.
- **Stats Row**: Followers, posts, likes.
- **Content Tabs**: Grid/list toggle for user content.
- **Settings List**: Grouped preferences with icons.
- **Actions**: Log out, delete account (destructive).

### Mobile Chat/Communication

- **Message Bubbles**: Distinct styles for sent/received.
- **Input Area**: Text field, attachment, send button.
- **Media Gallery**: Photos, videos, shared content.
- **Timestamp**: Readable time format.
- **Status Indicators**: Online, typing, read receipts.

### Web Landing Pages

- **Hero**: Bold headline, subheadline, CTA.
- **Social Proof**: Logos, testimonials, ratings.
- **Features**: Grid of benefits with icons.
- **How It Works**: Step-by-step guide.
- **Pricing**: Tiered pricing cards.
- **FAQ**: Accordion-style questions.
- **CTA**: Final call-to-action.
- **Footer**: Links, contact, legal.

### Web Dashboards

- **Sidebar Navigation**: Collapsible sections.
- **Header**: User profile, notifications, search.
- **Summary Widgets**: Key metrics at a glance.
- **Data Tables**: Sortable, filterable lists.
- **Charts**: Visual data representation.
- **Activity Feed**: Recent events stream.
- **Quick Actions**: Frequently used buttons.

### Web E-commerce

- **Product Grid**: Responsive card layout.
- **Filters**: Sidebar or horizontal filters.
- **Product Detail**: Images, description, reviews.
- **Cart**: Line items, totals, checkout button.
- **Checkout**: Multi-step form with progress.
- **Account**: Orders, wishlist, settings.

---

## Performance Optimization

### Mobile Rendering

- **Virtual Lists**: Only render visible items. Critical for long lists.
- **Image Optimization**: Proper sizing, compression, lazy loading.
- **Code Splitting**: Load components on demand.
- **Memoization**: Cache expensive computations.

### Mobile Network

- **Request Batching**: Combine multiple API calls.
- **Caching Strategy**: Local storage, ETag,304 Not Modified.
- **Offline-First**: Graceful degradation when offline.
- **Payload Size**: Minimize request/response sizes.

### Mobile Storage

- **Local Persistence**: Efficient use of AsyncStorage/SQLite/Realm.
- **Image Cache**: Proper caching headers and local cache.
- **Data Compression**: Binary formats over JSON when appropriate.
- **Cache Invalidation**: Smart cache clearing strategies.

### Web Performance

- **Lazy Loading**: Images, components, routes.
- **Code Splitting**: Dynamic imports.
- **CDN**: Static assets on CDN.
- **Minification**: CSS, JavaScript.
- **Compression**: Gzip/Brotli.
- **Caching**: Service workers, HTTP cache.
- **Image Optimization**: WebP, AVIF, srcset.
- **Critical CSS**: Inline critical styles.

---

## Accessibility

### Mobile Accessibility

- **Screen Reader**: Semantic markup, ARIA labels, content descriptions.
- **Color Independence**: Don't use color as the only conveyor of meaning.
- **Focus Management**: Logical focus order, visible focus indicators.
- **Text Scaling**: Respect system text size settings.
- **Contrast**: Meet WCAG 2.1 AA minimums.

### Web Accessibility

- **Semantic HTML**: Use proper HTML5 elements.
- **ARIA Labels**: For icons, buttons, inputs.
- **Keyboard Navigation**: Focus order, skip links.
- **Color Contrast**: 4.5:1 minimum ratio.
- **Alt Text**: Descriptive alt for all images.
- **Forms**: Labels, error messages, hints.
- **Reduced Motion**: Respect prefers-reduced-motion.

---

## Common Rules for Professional UI

### Icons & Visual Elements

| Rule | Do | Don't |
|------|-----|-------|
| **No emoji icons** | Use SVG icons (Heroicons, Lucide, Simple Icons) | Use emojis like 🎨 🚀 ⚙️ as UI icons |
| **Stable hover states** | Use color/opacity transitions on hover | Use scale transforms that shift layout |
| **Correct brand logos** | Research official SVG from Simple Icons | Guess or use incorrect logo paths |
| **Consistent icon sizing** | Use fixed viewBox (24x24) with w-6 h-6 | Mix different icon sizes randomly |

### Interaction & Cursor

| Rule | Do | Don't |
|------|-----|-------|
| **Cursor pointer** | Add `cursor-pointer` to all clickable/hoverable cards | Leave default cursor on interactive elements |
| **Hover feedback** | Provide visual feedback (color, shadow, border) | No indication element is interactive |
| **Smooth transitions** | Use `transition-colors duration-200` | Instant state changes or too slow (>500ms) |

### Light/Dark Mode Contrast

| Rule | Do | Don't |
|------|-----|-------|
| **Glass card light mode** | Use `bg-white/80` or higher opacity | Use `bg-white/10` (too transparent) |
| **Text contrast light** | Use `#0F172A` (slate-900) for text | Use `#94A3B8` (slate-400) for body text |
| **Muted text light** | Use `#475569` (slate-600) minimum | Use gray-400 or lighter |
| **Border visibility** | Use `border-gray-200` in light mode | Use `border-white/10` (invisible) |

### Layout & Spacing

| Rule | Do | Don't |
|------|-----|-------|
| **Floating navbar** | Add `top-4 left-4 right-4` spacing | Stick navbar to `top-0 left-0 right-0` |
| **Content padding** | Account for fixed navbar height | Let content hide behind fixed elements |
| **Consistent max-width** | Use same `max-w-6xl` or `max-w-7xl` | Mix different container widths |

---

## Pre-Delivery Checklist

Before delivering UI code, verify these items:

### Visual Quality
- [ ] No emojis used as icons (use SVG instead)
- [ ] All icons from consistent icon set (Heroicons/Lucide)
- [ ] Brand logos are correct (verified from Simple Icons)
- [ ] Hover states don't cause layout shift
- [ ] Use theme colors directly (bg-primary) not var() wrapper

### Interaction
- [ ] All clickable elements have `cursor-pointer`
- [ ] Hover states provide clear visual feedback
- [ ] Transitions are smooth (150-300ms)
- [ ] Focus states visible for keyboard navigation

### Light/Dark Mode
- [ ] Light mode text has sufficient contrast (4.5:1 minimum)
- [ ] Glass/transparent elements visible in light mode
- [ ] Borders visible in both modes
- [ ] Test both modes before delivery

### Layout
- [ ] Floating elements have proper spacing from edges
- [ ] No content hidden behind fixed navbars
- [ ] Responsive at 375px, 768px, 1024px, 1440px
- [ ] No horizontal scroll on mobile

### Accessibility
- [ ] All images have alt text
- [ ] Form inputs have labels
- [ ] Color is not the only indicator
- [ ] `prefers-reduced-motion` respected

### Performance
- [ ] Images are optimized (WebP, lazy loaded)
- [ ] Code is split where appropriate
- [ ] Animations are GPU-accelerated
- [ ] No layout-triggering animations

### Mobile-Specific
- [ ] Touch targets are at least 44x44px
- [ ] Thumb zone optimization applied
- [ ] Platform conventions respected (iOS HIG / Material Design)
- [ ] Safe areas handled (notch, home indicator)

---

## Code Examples

### React Native Component

```jsx
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';

const MobileCard = ({ title, subtitle, onPress, style }) => {
  return (
    <TouchableOpacity 
      style={[styles.card, style]}
      onPress={onPress}
      activeOpacity={0.8}
      accessibilityLabel={title}
      accessibilityRole="button"
    >
      <View style={styles.header}>
        <Text style={styles.title}>{title}</Text>
        <Text style={styles.subtitle}>{subtitle}</Text>
      </View>
      <View style={styles.chevron}>›</View>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    marginHorizontal: 16,
    marginVertical: 8,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    // Neumorphic shadow
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  header: {
    flex: 1,
  },
  title: {
    fontSize: 17,
    fontWeight: '600',
    color: '#1D1D1F',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 14,
    color: '#86868B',
  },
  chevron: {
    fontSize: 20,
    color: '#C7C7CC',
    marginLeft: 12,
  },
});

export default MobileCard;
```

### SwiftUI Component

```swift
import SwiftUI

struct MobileCard: View {
    let title: String
    let subtitle: String
    let onTap: () -> Void
    
    var body: some View {
        Button(action: onTap) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(title)
                        .font(.system(size: 17, weight: .semibold))
                        .foregroundColor(.primary)
                    
                    Text(subtitle)
                        .font(.system(size: 14))
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.secondary)
            }
            .padding(16)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color(.systemBackground))
                    .shadow(color: .black.opacity(0.08), radius: 8, y: 2)
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
}

#Preview {
    MobileCard(
        title: "Design Principles",
        subtitle: "Learn about mobile aesthetics",
        onTap: {}
    )
    .padding()
}
```

### Flutter Component

```dart
import 'package:flutter/material.dart';

class MobileCard extends StatelessWidget {
  final String title;
  final String subtitle;
  final VoidCallback onTap;
  
  const MobileCard({
    super.key,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });
  
  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.surface,
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.08),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: Theme.of(context).colorScheme.onSurfaceVariant,
                    ),
                  ),
                ],
              ),
            ),
            Icon(
              Icons.chevron_right,
              color: Theme.of(context).colorScheme.onSurfaceVariant,
            ),
          ],
        ),
      ),
    );
  }
}
```

### uni-app Component

```vue
<template>
  <view class="mobile-card" @click="handleClick">
    <view class="card-header">
      <text class="card-title">{{ title }}</text>
      <text class="card-subtitle">{{ subtitle }}</text>
    </view>
    <view class="card-arrow">
      <text class="arrow-icon">›</text>
    </view>
  </view>
</template>

<script>
export default {
  name: 'MobileCard',
  props: {
    title: {
      type: String,
      required: true
    },
    subtitle: {
      type: String,
      default: ''
    }
  },
  methods: {
    handleClick() {
      this.$emit('click');
    }
  }
};
</script>

<style lang="scss" scoped>
.mobile-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 32rpx;
  margin: 0 32rpx 16rpx;
  background-color: #fff;
  border-radius: 24rpx;
  
  // Glassmorphism effect
  backdrop-filter: blur(20rpx);
  box-shadow: 
    0 8rpx 32rpx rgba(0, 0, 0, 0.08),
    inset 0 1rpx 0 rgba(255, 255, 255, 0.8);
  
  .card-header {
    flex: 1;
    
    .card-title {
      display: block;
      font-size: 34rpx;
      font-weight: 600;
      color: #1d1d1f;
      margin-bottom: 8rpx;
    }
    
    .card-subtitle {
      font-size: 28rpx;
      color: #86868b;
    }
  }
  
  .card-arrow {
    margin-left: 24rpx;
    
    .arrow-icon {
      font-size: 40rpx;
      color: #c7c7cc;
    }
  }
}
</style>
```

### React Web Component

```jsx
import React from 'react';

const Button = ({ children, variant = 'primary', onClick, disabled }) => {
  const baseStyles = `
    px-6 py-3 rounded-lg font-semibold transition-all duration-200
    focus:outline-none focus:ring-2 focus:ring-offset-2
    disabled:opacity-50 disabled:cursor-not-allowed
  `;
  
  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
    secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200 focus:ring-gray-500',
    outline: 'border-2 border-gray-300 text-gray-700 hover:bg-gray-50 focus:ring-gray-500',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
  };
  
  return (
    <button
      className={`${baseStyles} ${variants[variant]}`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
};

export default Button;
```

### Vue Web Component

```vue
<template>
  <button 
    :class="buttonClass"
    :disabled="disabled"
    @click="handleClick"
  >
    <slot></slot>
  </button>
</template>

<script>
export default {
  name: 'BaseButton',
  props: {
    variant: {
      type: String,
      default: 'primary',
      validator: (value) => ['primary', 'secondary', 'outline', 'danger'].includes(value)
    },
    size: {
      type: String,
      default: 'md',
      validator: (value) => ['sm', 'md', 'lg'].includes(value)
    },
    disabled: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    buttonClass() {
      const base = 'font-semibold rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';
      const sizeClasses = {
        sm: 'px-3 py-1.5 text-sm',
        md: 'px-4 py-2 text-base',
        lg: 'px-6 py-3 text-lg'
      };
      const variantClasses = {
        primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
        secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200 focus:ring-gray-500',
        outline: 'border-2 border-gray-300 text-gray-700 hover:bg-gray-50 focus:ring-gray-500',
        danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500'
      };
      
      return `${base} ${sizeClasses[this.size]} ${variantClasses[this.variant]}`;
    }
  },
  methods: {
    handleClick() {
      this.$emit('click');
    }
  }
};
</script>
```

---

## Anti-Patterns to Avoid

NEVER use generic AI-generated mobile aesthetics:
- Overused gradient buttons that look identical across apps
- Generic avatar circles with the same shadow
- "Skeleton loader" screens that feel lifeless
- Bottom tab bars with identical styling in every app
- Card designs with the exact same padding, radius, and shadow values
- Loading spinners that are copied from bootstrap or generic libraries
- Empty states with generic illustrations

Every mobile design should feel purpose-built for:
- The specific content it displays
- The platform conventions it follows
- The users who will interact with it
- The context in which it will be used

Vary between different aesthetics:
- Different color palettes (pastel, neon, monochrome, vibrant)
- Different icon styles (outline, filled, illustrated, 3D)
- Different layout patterns (cards, lists, masonry, full-bleed)
- Different animation styles (subtle, playful, dramatic)

**IMPORTANT**: Match implementation complexity to the mobile vision. Feature-rich apps need thoughtful navigation and state management. Simple apps need elegant restraint and attention to micro-interactions. Excellence comes from executing the mobile vision with understanding of platform conventions and user expectations.

Remember: Claude is capable of extraordinary mobile design work. Don't settle for generic, template-like designs. Show what can truly be created when thinking deeply about mobile contexts and committing fully to distinctive, platform-aware design directions.

---

## Resources

### Mobile Platform Guidelines
- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Material Design 3](https://m3.material.io/)
- [WeChat Mini Program Design](https://developers.weixin.qq.com/miniprogram/design/)

### Web Design Guidelines
- [WebAIM Accessibility](https://webaim.org/)
- [A11Y Project](https://www.a11yproject.com/)
- [MDN Web Docs](https://developer.mozilla.org/)

### Design Tools
- Figma, Sketch, Adobe XD
- Principle, Framer for mobile prototyping
- After Effects for motion design

### Development Resources
- React Native documentation
- SwiftUI documentation
- Flutter documentation
- uni-app documentation
- React documentation
- Vue documentation
- Next.js documentation
- Tailwind CSS documentation