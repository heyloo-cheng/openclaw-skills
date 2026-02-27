---
name: translation-router
description: Routes translation tasks based on content type — technical docs, marketing copy, or UI text. Use when translating content between languages.
triggers:
  - translate
  - 翻译
  - translation
  - 中译英
  - 英译中
  - 本地化
  - localize
---

# Translation Router

Selects translation strategy based on content type for optimal quality.

## When NOT to Use This Skill

- For single word/phrase lookups
- For language learning exercises
- For already-translated content review

## Step 1: Detect Content Type

Analyze the input text or file:

| Pattern | Type | Strategy |
|---------|------|----------|
| Code comments, API docs, README | Technical | Preserve terminology, keep code blocks |
| Marketing copy, landing pages, ads | Marketing | Adapt tone, localize idioms |
| UI strings, button labels, menus | UI/UX | Concise, consistent, context-aware |
| Legal, compliance, terms | Legal | Precise, formal, no ambiguity |
| Blog posts, articles | Editorial | Natural flow, cultural adaptation |

## Step 2: Detect Languages

- Source language: Auto-detect from content
- Target language: User-specified or infer from context

## Step 3: Route by Type

### Technical Documentation
```bash
opencode run "Translate the following technical documentation from [source] to [target]. Rules: 1) Keep code blocks, variable names, and CLI commands unchanged, 2) Preserve markdown formatting, 3) Keep technical terms in English with Chinese/target explanation on first use, 4) Maintain heading structure. Content: <text>"
```

### Marketing / Editorial
```bash
claude -p "Translate this marketing content from [source] to [target]. Rules: 1) Adapt tone and idioms for target culture, 2) Maintain persuasive impact, 3) Localize examples and references, 4) Keep brand names unchanged. Content: <text>"
```

### UI Strings
```bash
opencode run "Translate these UI strings from [source] to [target]. Rules: 1) Keep translations concise (similar character count), 2) Maintain consistent terminology across strings, 3) Consider context (button/label/message/error), 4) Output as key-value pairs. Strings: <text>"
```

### Legal / Formal
```bash
claude -p "Translate this legal/formal text from [source] to [target]. Rules: 1) Precise meaning preservation, 2) Formal register, 3) No ambiguity, 4) Flag terms with no direct equivalent. Content: <text>"
```

## Step 4: Output

```
## Translation Results

**Type:** [Technical/Marketing/UI/Legal]
**Direction:** [source] → [target]
**Tool:** [OpenCode/Claude Code]

---
[Translated content]
---

**Notes:** [terminology decisions, flagged items]
```
