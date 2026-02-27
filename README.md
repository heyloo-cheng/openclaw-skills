# OpenClaw Skills

Intelligent agent skills for OpenClaw — smart routing, workflow recipes, and cross-agent collaboration.

## Skills

| Skill | Description |
|-------|-------------|
| code-review-router | Routes code reviews between OpenCode and Claude Code |
| commit-message-router | Generates commit messages based on change characteristics |
| test-generator-router | Routes test generation (unit/integration/E2E) |
| refactor-planner | Analyzes code smells and plans refactoring |
| deploy-reviewer | Reviews CI/CD and deployment configs |
| incident-router | Routes incident troubleshooting by error pattern |
| doc-generator-router | Routes documentation generation by content type |
| translation-router | Routes translation by content type |
| pr-reviewer-router | Comprehensive PR review |
| task-estimator | Estimates task complexity and time |
| team-tasks | Multi-agent task coordination |
| skill-router | Intent matching + context-aware skill discovery |
| skill-recipes | Workflow recipes chaining multiple skills |
| skill-sandbox | Validates and dry-run tests skills |
| skill-intelligence | Proactive recommendations + self-evolution + cross-agent collaboration |

## Installation

Copy skills to your OpenClaw workspace:
```bash
cp -r */ ~/.openclaw/workspace/skills/
python3 ~/.openclaw/workspace/scripts/skill-register.py
```

## License

MIT
