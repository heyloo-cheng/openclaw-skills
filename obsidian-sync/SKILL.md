# Obsidian Sync Skill

Bidirectional sync between Obsidian vault and OpenClaw memory system.

## Features

- **File Watcher**: Monitors Obsidian vault for changes
- **Markdown Parser**: Extracts frontmatter, content, and links
- **Bidirectional Links**: Parses `[[wikilinks]]` and backlinks
- **Auto Import**: New notes automatically imported to memory-lancedb-pro
- **Knowledge Graph**: Builds relationship graph from links

## Usage

### Start File Watcher

```bash
node ~/.openclaw/workspace/skills/obsidian-sync/index.mjs watch
```

### Import Existing Notes

```bash
node ~/.openclaw/workspace/skills/obsidian-sync/index.mjs import
```

### Parse Single Note

```bash
node ~/.openclaw/workspace/skills/obsidian-sync/index.mjs parse ~/Obsidian/MyKnowledge/Projects/example.md
```

## Configuration

Environment variables:

```bash
OBSIDIAN_VAULT_PATH=~/Obsidian/MyKnowledge
OBSIDIAN_SYNC_INTERVAL=5000  # ms
OBSIDIAN_AUTO_IMPORT=true
```

## Integration

Integrates with:
- `memory-lancedb-pro` - stores notes as memories
- `unified-search` - searches across notes
- `vestige` - important notes (importance >= 0.8) stored for FSRS-6

## File Structure

```
~/Obsidian/MyKnowledge/
├── Projects/       # Project notes
├── Learning/       # Learning notes
├── Ideas/          # Idea notes
└── Archive/        # Archived notes
```

## Frontmatter Format

```yaml
---
title: Note Title
tags: [tag1, tag2]
importance: 0.8
category: fact
created: 2026-03-03
---

Note content here...

[[Related Note]]
```

## API

### `watchVault(vaultPath)`
Start watching vault for changes.

### `importNote(filePath)`
Import single note to memory.

### `parseMarkdown(content)`
Parse markdown content and extract metadata.

### `extractLinks(content)`
Extract `[[wikilinks]]` from content.

### `buildKnowledgeGraph(vaultPath)`
Build relationship graph from all notes.

## Triggers

- File created/modified in vault → auto import
- Memory stored with high importance → create note
- Link created → update knowledge graph
