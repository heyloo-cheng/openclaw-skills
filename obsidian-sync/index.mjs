#!/usr/bin/env node
/**
 * Obsidian Sync - Bidirectional sync between Obsidian and OpenClaw
 */

import chokidar from 'chokidar';
import matter from 'gray-matter';
import { readFile, readdir, writeFile } from 'fs/promises';
import { join, basename, extname } from 'path';
import { homedir } from 'os';

// Configuration
const VAULT_PATH = process.env.OBSIDIAN_VAULT_PATH || join(homedir(), 'Obsidian', 'MyKnowledge');
const SYNC_INTERVAL = parseInt(process.env.OBSIDIAN_SYNC_INTERVAL || '5000');
const AUTO_IMPORT = process.env.OBSIDIAN_AUTO_IMPORT !== 'false';

// State
const processedFiles = new Set();
const knowledgeGraph = new Map(); // file -> [linked files]

/**
 * Parse markdown file
 */
export async function parseMarkdown(filePath) {
  try {
    const content = await readFile(filePath, 'utf-8');
    const { data: frontmatter, content: body } = matter(content);

    // Extract wikilinks [[link]]
    const links = extractLinks(body);

    // Extract tags from frontmatter and content
    const tags = [
      ...(frontmatter.tags || []),
      ...extractHashtags(body)
    ];

    return {
      filePath,
      fileName: basename(filePath, '.md'),
      frontmatter,
      body,
      links,
      tags,
      importance: frontmatter.importance || 0.7,
      category: frontmatter.category || 'other',
      created: frontmatter.created || new Date().toISOString(),
    };
  } catch (error) {
    console.error(`Error parsing ${filePath}:`, error.message);
    return null;
  }
}

/**
 * Extract [[wikilinks]] from content
 */
export function extractLinks(content) {
  const linkRegex = /\[\[([^\]]+)\]\]/g;
  const links = [];
  let match;

  while ((match = linkRegex.exec(content)) !== null) {
    const link = match[1];
    // Handle [[link|alias]] format
    const [target] = link.split('|');
    links.push(target.trim());
  }

  return [...new Set(links)]; // deduplicate
}

/**
 * Extract #hashtags from content
 */
export function extractHashtags(content) {
  const tagRegex = /#([a-zA-Z0-9_-]+)/g;
  const tags = [];
  let match;

  while ((match = tagRegex.exec(content)) !== null) {
    tags.push(match[1]);
  }

  return [...new Set(tags)];
}

/**
 * Import note to memory-lancedb-pro
 */
export async function importNote(filePath) {
  const parsed = await parseMarkdown(filePath);
  if (!parsed) return null;

  const { fileName, body, frontmatter, links, tags, importance, category } = parsed;

  // Build memory text
  const text = `${fileName}: ${body.slice(0, 500)}${body.length > 500 ? '...' : ''}`;

  // Store to memory (would call memory_store tool in real integration)
  const memory = {
    text,
    importance,
    category,
    scope: 'obsidian',
    metadata: {
      filePath,
      fileName,
      links,
      tags,
      frontmatter,
    }
  };

  console.log(`📝 Imported: ${fileName} (importance: ${importance}, links: ${links.length})`);
  return memory;
}

/**
 * Watch vault for changes
 */
export function watchVault(vaultPath = VAULT_PATH) {
  console.log(`👀 Watching vault: ${vaultPath}`);

  const watcher = chokidar.watch('**/*.md', {
    cwd: vaultPath,
    persistent: true,
    ignoreInitial: false,
    awaitWriteFinish: {
      stabilityThreshold: 2000,
      pollInterval: 100
    }
  });

  watcher
    .on('add', async (path) => {
      const fullPath = join(vaultPath, path);
      if (processedFiles.has(fullPath)) return;
      
      console.log(`➕ New file: ${path}`);
      if (AUTO_IMPORT) {
        await importNote(fullPath);
        processedFiles.add(fullPath);
      }
    })
    .on('change', async (path) => {
      const fullPath = join(vaultPath, path);
      console.log(`✏️  Changed: ${path}`);
      if (AUTO_IMPORT) {
        await importNote(fullPath);
      }
    })
    .on('unlink', (path) => {
      const fullPath = join(vaultPath, path);
      console.log(`🗑️  Deleted: ${path}`);
      processedFiles.delete(fullPath);
      knowledgeGraph.delete(fullPath);
    })
    .on('error', (error) => {
      console.error('Watcher error:', error);
    });

  return watcher;
}

/**
 * Build knowledge graph from all notes
 */
export async function buildKnowledgeGraph(vaultPath = VAULT_PATH) {
  console.log(`🕸️  Building knowledge graph...`);
  
  const graph = new Map();
  
  async function scanDir(dir) {
    const entries = await readdir(dir, { withFileTypes: true });
    
    for (const entry of entries) {
      const fullPath = join(dir, entry.name);
      
      if (entry.isDirectory()) {
        await scanDir(fullPath);
      } else if (entry.isFile() && extname(entry.name) === '.md') {
        const parsed = await parseMarkdown(fullPath);
        if (parsed) {
          graph.set(fullPath, parsed.links);
        }
      }
    }
  }
  
  await scanDir(vaultPath);
  
  console.log(`✅ Knowledge graph built: ${graph.size} notes, ${[...graph.values()].flat().length} links`);
  return graph;
}

/**
 * Import all existing notes
 */
export async function importAllNotes(vaultPath = VAULT_PATH) {
  console.log(`📚 Importing all notes from ${vaultPath}...`);
  
  let count = 0;
  
  async function scanDir(dir) {
    const entries = await readdir(dir, { withFileTypes: true });
    
    for (const entry of entries) {
      const fullPath = join(dir, entry.name);
      
      if (entry.isDirectory()) {
        await scanDir(fullPath);
      } else if (entry.isFile() && extname(entry.name) === '.md') {
        await importNote(fullPath);
        count++;
      }
    }
  }
  
  await scanDir(vaultPath);
  
  console.log(`✅ Imported ${count} notes`);
  return count;
}

/**
 * CLI
 */
async function main() {
  const command = process.argv[2];
  const arg = process.argv[3];

  switch (command) {
    case 'watch':
      watchVault(arg || VAULT_PATH);
      console.log('Press Ctrl+C to stop watching');
      break;

    case 'import':
      await importAllNotes(arg || VAULT_PATH);
      break;

    case 'parse':
      if (!arg) {
        console.error('Usage: node index.mjs parse <file>');
        process.exit(1);
      }
      const parsed = await parseMarkdown(arg);
      console.log(JSON.stringify(parsed, null, 2));
      break;

    case 'graph':
      const graph = await buildKnowledgeGraph(arg || VAULT_PATH);
      console.log(JSON.stringify([...graph.entries()], null, 2));
      break;

    default:
      console.log(`
Obsidian Sync CLI

Usage:
  node index.mjs watch [vault-path]   - Watch vault for changes
  node index.mjs import [vault-path]  - Import all existing notes
  node index.mjs parse <file>         - Parse single note
  node index.mjs graph [vault-path]   - Build knowledge graph

Environment:
  OBSIDIAN_VAULT_PATH=${VAULT_PATH}
  OBSIDIAN_SYNC_INTERVAL=${SYNC_INTERVAL}
  OBSIDIAN_AUTO_IMPORT=${AUTO_IMPORT}
      `);
      break;
  }
}

// Run CLI if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}
