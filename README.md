# OpenClaw Skills Collection

A comprehensive collection of 177+ reusable AI agent skills for OpenClaw.

## 📚 What's Inside

This repository contains production-ready skills covering:

- **Development**: Frontend/Backend patterns, TDD, Code review, API design
- **AI/ML**: Agent orchestration, MCP builders, Prompt optimization
- **Content**: Writing, Translation, SEO, Social media
- **Research**: Market research, Deep search, Data analysis
- **Design**: UI/UX, Mobile design, Canvas design
- **DevOps**: Docker, Deployment, Database migrations
- **Business**: Investor materials, Pricing strategy, Marketing

## 🚀 Quick Start

### Installation

```bash
# Clone this repository
git clone https://github.com/heyloo-cheng/openclaw-skills.git

# Copy skills to your OpenClaw workspace
cp -r openclaw-skills/* ~/.openclaw/workspace/.agents/skills/
```

### Usage

Skills are automatically discovered by OpenClaw. To use a skill:

1. Check available skills: `openclaw skills list`
2. Skills are triggered automatically based on task context
3. Or explicitly call: Read the skill's `SKILL.md` for instructions

## 📖 Skill Categories

### Development & Engineering
- `frontend-patterns` - Modern frontend best practices
- `backend-patterns` - Scalable backend architecture
- `test-driven-development` - TDD workflow and patterns
- `systematic-debugging` - Structured debugging approach
- `api-design` - RESTful API design principles

### AI & Automation
- `agent-tools` - Agent orchestration utilities
- `mcp-builder` - Model Context Protocol server builder
- `prompt-optimizer` - Prompt engineering optimization
- `autonomous-loops` - Self-improving agent loops
- `subagent-driven-development` - Multi-agent collaboration

### Content & Writing
- `article-writing` - Long-form content creation
- `copywriting` - Marketing copy and messaging
- `copy-editing` - Editorial review and refinement
- `social-content` - Social media content strategy
- `content-strategy` - Content planning and execution

### Research & Analysis
- `market-research` - Market analysis and insights
- `deep-search` - Advanced search strategies
- `brave-search` - Web search integration
- `ios-market-research` - iOS app market analysis
- `seo-audit` - SEO analysis and optimization

### Design & UX
- `ui-ux-pro-max` - Professional UI/UX design
- `mobile-design` - Mobile-first design patterns
- `canvas-design` - Canvas-based design system
- `apple-hig` - Apple Human Interface Guidelines
- `frontend-slides` - Presentation design

### Business & Strategy
- `investor-materials` - Pitch decks and materials
- `pricing-strategy` - Pricing model optimization
- `marketing-ideas` - Marketing campaign ideation
- `product-marketing-context` - Product positioning
- `strategic-compact` - Strategic planning

## 🛠️ Skill Structure

Each skill follows a standard structure:

```
skill-name/
├── SKILL.md          # Main skill documentation
├── _meta.json        # Metadata (optional)
├── references/       # Reference materials
├── scripts/          # Automation scripts
└── templates/        # Reusable templates
```

## 📝 Creating Your Own Skills

Use the `skill-creator` skill to generate new skills:

```bash
# Read the skill creator documentation
cat ~/.openclaw/workspace/.agents/skills/skill-creator/SKILL.md
```

## 🔍 Finding Skills

Use the built-in search:

```bash
# Search by keyword
bash ~/.openclaw/workspace/scripts/skill-search.sh "frontend"

# List all skills
openclaw skills list
```

## 🤝 Contributing

Skills are continuously evolving. To contribute:

1. Fork this repository
2. Create a new skill following the standard structure
3. Test thoroughly with OpenClaw
4. Submit a pull request

## 📊 Statistics

- **Total Skills**: 177+
- **Total Size**: ~40MB
- **Categories**: 10+
- **Last Updated**: 2026-04-17

## 🔗 Related Projects

- [OpenClaw](https://github.com/openclaw/openclaw) - The main OpenClaw project
- [OpenClaw Docs](https://docs.openclaw.ai) - Official documentation
- [ClawHub](https://clawhub.ai) - Skill marketplace

## 📄 License

Individual skills may have their own licenses. Check each skill's directory for details.

## 🙏 Acknowledgments

These skills are built on the collective knowledge of the OpenClaw community and various open-source projects.

---

**Note**: This is a living collection. Skills are regularly updated and new ones are added. Star this repo to stay updated!
