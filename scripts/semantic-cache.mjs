#!/usr/bin/env node
/**
 * semantic-cache.mjs — 语义缓存管理
 * 用法:
 *   node semantic-cache.mjs store "question" "answer"
 *   node semantic-cache.mjs query "question"
 *   node semantic-cache.mjs stats
 *   node semantic-cache.mjs clean [days]
 */

import { createRequire } from "node:module";
import { homedir } from "node:os";
import { join } from "node:path";

const require = createRequire(import.meta.url);
const lancedb = require(join(homedir(), ".openclaw/workspace/plugins/memory-lancedb-pro/node_modules/@lancedb/lancedb"));

const JINA_API_KEY = "jina_263d8c05af5e425d9749551249952212fC2xGAojK2RS8mNXZFCQ879d9EH_";
const JINA_MODEL = "jina-embeddings-v5-text-small";
const DB_PATH = join(homedir(), ".openclaw/memory/lancedb-pro");
const TABLE_NAME = "semantic_cache";
const DIMENSIONS = 1024;
const SIMILARITY_THRESHOLD = 0.35; // cosine distance < 0.35 = cache hit

async function embed(texts, task = "retrieval.query") {
  const resp = await fetch("https://api.jina.ai/v1/embeddings", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${JINA_API_KEY}`,
    },
    body: JSON.stringify({
      model: JINA_MODEL, input: texts, task, dimensions: DIMENSIONS, normalized: true,
    }),
  });
  if (!resp.ok) throw new Error(`Jina API error: ${resp.status}`);
  const data = await resp.json();
  return data.data.map(d => d.embedding);
}

async function getOrCreateTable(db) {
  try {
    return await db.openTable(TABLE_NAME);
  } catch {
    return null;
  }
}

async function store(question, answer) {
  const db = await lancedb.connect(DB_PATH);
  const [vec] = await embed([question], "retrieval.passage");
  
  const record = {
    id: `cache_${Date.now()}`,
    question,
    answer,
    vector: vec,
    hit_count: 0,
    created_at: Date.now(),
    last_hit: 0,
  };

  let table = await getOrCreateTable(db);
  if (!table) {
    table = await db.createTable(TABLE_NAME, [record]);
    console.log("Created semantic_cache table");
  } else {
    await table.add([record]);
  }
  console.log(`✅ Cached: "${question.slice(0, 50)}..."`);
}

async function query(question) {
  const db = await lancedb.connect(DB_PATH);
  const table = await getOrCreateTable(db);
  if (!table) {
    console.log("MISS — cache empty");
    return null;
  }

  const [vec] = await embed([question], "retrieval.query");
  const results = await table.search(vec).limit(1).toArray();

  if (results.length === 0) {
    console.log("MISS — no results");
    return null;
  }

  const best = results[0];
  const distance = best._distance ?? 1;

  if (distance < SIMILARITY_THRESHOLD) {
    console.log(`HIT (distance: ${distance.toFixed(4)})`);
    console.log(`Q: ${best.question}`);
    console.log(`A: ${best.answer.slice(0, 200)}...`);
    return best;
  } else {
    console.log(`MISS (distance: ${distance.toFixed(4)}, threshold: ${SIMILARITY_THRESHOLD})`);
    console.log(`Nearest: "${best.question}"`);
    return null;
  }
}

async function stats() {
  const db = await lancedb.connect(DB_PATH);
  const table = await getOrCreateTable(db);
  if (!table) {
    console.log("Cache empty");
    return;
  }
  const count = await table.countRows();
  console.log(`📊 Semantic Cache Stats`);
  console.log(`   Entries: ${count}`);
}

async function clean(days = 30) {
  const db = await lancedb.connect(DB_PATH);
  const table = await getOrCreateTable(db);
  if (!table) return;
  const cutoff = Date.now() - days * 86400000;
  await table.delete(`created_at < ${cutoff}`);
  console.log(`🧹 Cleaned entries older than ${days} days`);
}

const [,, action, ...args] = process.argv;
switch (action) {
  case "store": await store(args[0], args[1]); break;
  case "query": await query(args[0]); break;
  case "stats": await stats(); break;
  case "clean": await clean(parseInt(args[0]) || 30); break;
  default: console.log("Usage: semantic-cache.mjs <store|query|stats|clean> [args]");
}
