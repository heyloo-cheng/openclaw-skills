---
name: doc-generator-router
description: Routes documentation generation based on code type — API docs, README, changelog, or inline comments. Use when you want to generate or update documentation.
triggers:
  - doc
  - 文档
  - readme
  - changelog
  - API文档
  - 注释
  - generate doc
  - 写文档
---

# Doc Generator Router

Selects the optimal documentation strategy based on what changed.

## When NOT to Use This Skill

- For prose editing (just edit directly)
- For commit messages (use commit-message-router)
- For non-code documentation (marketing copy, etc.)

## Step 1: Detect What Needs Docs

```bash
git --no-pager diff --name-only HEAD 2>/dev/null || echo "NO_CHANGES"
# Also check for undocumented exports
```

## Step 2: Route by Content Type

### → API Documentation
Trigger: Route/controller/endpoint files changed, OpenAPI/Swagger files exist

```bash
opencode run "Generate API documentation for the changed endpoints. Include: method, path, parameters, request/response examples, error codes. Follow OpenAPI style."
```

### → README Update
Trigger: New features added, project structure changed, dependencies updated

```bash
opencode run "Update the README.md to reflect current changes. Add/update: feature descriptions, usage examples, installation steps if changed."
```

### → Changelog Entry
Trigger: Multiple meaningful changes, version bump, release prep

```bash
git log --oneline HEAD~10..HEAD | claude -p "Generate a changelog entry from these commits. Group by: Added, Changed, Fixed, Removed. Use Keep a Changelog format."
```

### → Inline Comments / JSDoc / Docstrings
Trigger: New functions/classes without documentation, complex logic

```bash
opencode run "Add documentation comments to undocumented functions in the changed files. Use the project's existing doc style (JSDoc/docstring/XML doc). Focus on: purpose, parameters, return values, edge cases."
```

### → Architecture / Design Doc
Trigger: Major structural changes, new modules, system design

```bash
claude -p "Analyze the project structure and recent changes. Generate an architecture document covering: system overview, component relationships, data flow, key design decisions."
```

## Step 3: Output

```
## Documentation Generated

**Type:** [API/README/Changelog/Inline/Architecture]
**Tool:** [OpenCode/Claude Code]

---
[Generated documentation]
---

**Files to update:** [list]
```
