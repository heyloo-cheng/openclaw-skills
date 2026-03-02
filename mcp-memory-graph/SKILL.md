# MCP Memory Graph Skill

Knowledge graph integration using MCP memory server.

## Features

- **Entity Management**: Create and manage entities
- **Relationship Tracking**: Define relationships between entities
- **Graph Queries**: Search and traverse knowledge graph
- **Fast Retrieval**: 5ms average query time
- **Cross-Agent Sharing**: Shared knowledge across agents

## Usage

### Add Entity

```bash
node index.mjs add-entity "OpenClaw" "AI assistant framework" --type "software"
```

### Add Relation

```bash
node index.mjs add-relation "OpenClaw" "uses" "Claude" --type "dependency"
```

### Search

```bash
node index.mjs search "OpenClaw"
```

### Query Graph

```bash
node index.mjs query "What does OpenClaw use?"
```

## Integration

Integrates with:
- `memory-lancedb-pro` - stores entities as memories
- `unified-search` - searches across graph
- `obsidian-sync` - syncs entities to Obsidian

## MCP Server

Uses `@modelcontextprotocol/server-memory` for knowledge graph storage.

Server path: `~/.openclaw/workspace/mcp-servers/src/memory/dist/index.js`

## API

### `addEntity(name, description, type)`
Create new entity in graph.

### `addRelation(from, relation, to, type)`
Create relationship between entities.

### `search(query)`
Search entities by name or description.

### `query(naturalLanguage)`
Query graph using natural language.

### `getGraph()`
Get entire knowledge graph.

## Triggers

- Entity mentioned in conversation → auto-create
- Relationship detected → auto-link
- Query about entities → search graph
