#!/usr/bin/env node
/**
 * skill-vectorize.mjs — 把 skill-registry.json 向量化存入 LanceDB skills 表
 * 复用 memory-lancedb-pro 的 LanceDB 实例和 Jina embedding
 */

import { createRequire } from "node:module";
import { readFile } from "node:fs/promises";
import { homedir } from "node:os";
import { join } from "node:path";

const require = createRequire(import.meta.url);

// 复用插件的 lancedb
const lancedb = require(join(homedir(), ".openclaw/workspace/plugins/memory-lancedb-pro/node_modules/@lancedb/lancedb"));

// Config
const JINA_API_KEY = "jina_263d8c05af5e425d9749551249952212fC2xGAojK2RS8mNXZFCQ879d9EH_";
const JINA_MODEL = "jina-embeddings-v5-text-small";
const DB_PATH = join(homedir(), ".openclaw/memory/lancedb-pro");
const REGISTRY_PATH = join(homedir(), ".openclaw/workspace/data/skill-registry.json");
const TABLE_NAME = "skills";
const DIMENSIONS = 1024;

// Jina embedding
async function embed(texts, task = "retrieval.passage") {
  const resp = await fetch("https://api.jina.ai/v1/embeddings", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${JINA_API_KEY}`,
    },
    body: JSON.stringify({
      model: JINA_MODEL,
      input: texts,
      task,
      dimensions: DIMENSIONS,
      normalized: true,
    }),
  });
  if (!resp.ok) throw new Error(`Jina API error: ${resp.status} ${await resp.text()}`);
  const data = await resp.json();
  return data.data.map(d => d.embedding);
}

// Build searchable text for each skill
function buildSkillText(skill) {
  const parts = [
    skill.name,
    skill.description,
    ...(skill.triggers || []),
    ...(skill.examples || []),
  ];
  return parts.filter(Boolean).join(" | ");
}

async function main() {
  console.log("📦 Loading registry...");
  const registry = JSON.parse(await readFile(REGISTRY_PATH, "utf-8"));
  console.log(`   ${registry.length} skills found`);

  // Build texts for embedding
  const texts = registry.map(buildSkillText);

  // Batch embed (Jina supports up to 2048 inputs)
  console.log("🧠 Generating embeddings...");
  const batchSize = 50;
  const allVectors = [];
  for (let i = 0; i < texts.length; i += batchSize) {
    const batch = texts.slice(i, i + batchSize);
    const vectors = await embed(batch);
    allVectors.push(...vectors);
    console.log(`   Embedded ${Math.min(i + batchSize, texts.length)}/${texts.length}`);
  }

  // Build records
  const records = registry.map((skill, idx) => ({
    id: skill.id,
    name: skill.name,
    description: skill.description || "",
    source: skill.source || "",
    category: skill.category || "general",
    triggers: JSON.stringify(skill.triggers || []),
    examples: JSON.stringify(skill.examples || []),
    cli_deps: JSON.stringify(skill.cli_deps || []),
    path: skill.path || "",
    search_text: texts[idx],
    vector: allVectors[idx],
    use_count: skill.use_count || 0,
    success_rate: skill.success_rate ?? -1,
    updated_at: Date.now(),
  }));

  // Connect to LanceDB
  console.log("💾 Writing to LanceDB...");
  const db = await lancedb.connect(DB_PATH);

  // Drop existing table if exists
  try {
    await db.dropTable(TABLE_NAME);
    console.log("   Dropped existing skills table");
  } catch (e) {
    // Table doesn't exist, that's fine
  }

  // Create table
  const table = await db.createTable(TABLE_NAME, records);
  console.log(`   Created '${TABLE_NAME}' table with ${records.length} records`);

  // Create FTS index on search_text
  try {
    await table.createIndex("search_text", { config: lancedb.Index.fts() });
    console.log("   Created FTS index on search_text");
  } catch (e) {
    console.log(`   FTS index: ${e.message}`);
  }

  // Test search
  console.log("\n🔍 Test searches:");
  
  const testQueries = [
    "review my code",
    "帮我写commit message",
    "翻译文档",
    "服务挂了怎么办",
    "天气",
  ];

  for (const query of testQueries) {
    const [qVec] = await embed([query], "retrieval.query");
    const results = await table.search(qVec).limit(3).toArray();
    const top = results.map(r => `${r.id}(${(r._distance ?? 0).toFixed(3)})`).join(", ");
    console.log(`   "${query}" → ${top}`);
  }

  console.log("\n✅ Done! Skills vectorized in LanceDB.");
  console.log(`   DB: ${DB_PATH}`);
  console.log(`   Table: ${TABLE_NAME} (${records.length} records)`);
}

main().catch(err => {
  console.error("❌ Error:", err.message);
  process.exit(1);
});
