#!/usr/bin/env node
/**
 * Deep Search Engine v1.0
 * Exa → Tavily → Crawl4AI/web_fetch 三层降级
 */

// === Types ===
class CircuitBreaker {
  constructor(name, maxFail = 3, cooldownMs = 30 * 60 * 1000) {
    this.name = name;
    this.failures = 0;
    this.maxFail = maxFail;
    this.cooldownMs = cooldownMs;
    this.openUntil = 0;
  }
  isOpen() {
    if (this.failures >= this.maxFail) {
      if (Date.now() < this.openUntil) return true;
      this.failures = 0; // half-open: reset and try
    }
    return false;
  }
  recordSuccess() { this.failures = 0; this.openUntil = 0; }
  recordFailure() {
    this.failures++;
    if (this.failures >= this.maxFail) {
      this.openUntil = Date.now() + this.cooldownMs;
      console.error(`[breaker] ${this.name} OPEN for ${this.cooldownMs / 60000}min`);
    }
  }
}

function withTimeout(promise, ms) {
  return Promise.race([
    promise,
    new Promise((_, rej) => setTimeout(() => rej(new Error(`Timeout ${ms}ms`)), ms)),
  ]);
}

// === Exa Provider ===
async function exaSearch(query, depth) {
  const key = process.env.EXA_API_KEY;
  if (!key) throw new Error("EXA_API_KEY not set");

  const typeMap = { quick: "auto", deep: "deep", max: "deep-max" };
  const body = {
    query,
    type: typeMap[depth] || "auto",
    numResults: depth === "quick" ? 5 : 10,
    contents: { text: { maxCharacters: 2000 } },
  };

  const res = await fetch("https://api.exa.ai/search", {
    method: "POST",
    headers: { "Content-Type": "application/json", "x-api-key": key },
    body: JSON.stringify(body),
  });

  if (res.status === 429) throw new Error("Exa quota exceeded");
  if (!res.ok) throw new Error(`Exa ${res.status}: ${await res.text()}`);

  const data = await res.json();
  return (data.results || []).map(r => ({
    title: r.title || "",
    url: r.url || "",
    content: r.text || r.summary || "",
    score: r.score,
    source: "exa",
  }));
}

// === Tavily Provider ===
async function tavilySearch(query, depth) {
  const key = process.env.TAVILY_API_KEY;
  if (!key) throw new Error("TAVILY_API_KEY not set");

  const body = {
    api_key: key,
    query,
    search_depth: depth === "quick" ? "basic" : "advanced",
    max_results: depth === "quick" ? 5 : 10,
    include_raw_content: false,
  };

  const res = await fetch("https://api.tavily.com/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (res.status === 429) throw new Error("Tavily quota exceeded");
  if (!res.ok) throw new Error(`Tavily ${res.status}: ${await res.text()}`);

  const data = await res.json();
  return (data.results || []).map(r => ({
    title: r.title || "",
    url: r.url || "",
    content: r.content || "",
    score: r.score,
    source: "tavily",
  }));
}

// === Crawl4AI / web_fetch Fallback ===
const JINA_KEY = process.env.JINA_API_KEY || "jina_263d8c05af5e425d9749551249952212fC2xGAojK2RS8mNXZFCQ879d9EH_";

async function fallbackSearch(query) {
  // Try Jina search (s.jina.ai)
  try {
    const res = await fetch(`https://s.jina.ai/${encodeURIComponent(query)}`, {
      headers: {
        "Accept": "application/json",
        "Authorization": `Bearer ${JINA_KEY}`,
        "X-Retain-Images": "none",
      },
    });
    if (res.ok) {
      const data = await res.json();
      const items = data.data || data.results || [];
      if (items.length > 0) {
        return items.slice(0, 5).map(r => ({
          title: r.title || "",
          url: r.url || "",
          content: r.content || r.description || r.snippet || "",
          source: "jina",
        }));
      }
    }
  } catch (e) { console.error(`[fallback] jina search error: ${e.message}`); }

  // Fallback: Jina reader on Google
  try {
    const res = await fetch(`https://r.jina.ai/https://www.google.com/search?q=${encodeURIComponent(query)}`, {
      headers: {
        "Authorization": `Bearer ${JINA_KEY}`,
        "X-Return-Format": "text",
      },
    });
    if (res.ok) {
      const text = await res.text();
      if (text.length > 100) {
        return [{ title: query, url: "google.com", content: text.slice(0, 3000), source: "jina-reader" }];
      }
    }
  } catch (e) { console.error(`[fallback] jina reader error: ${e.message}`); }

  return [];
}

// === Main Search Engine ===
const breakers = {
  exa: new CircuitBreaker("exa"),
  tavily: new CircuitBreaker("tavily"),
  fallback: new CircuitBreaker("fallback"),
};

async function deepSearch(query, depth = "deep") {
  const layers = [
    { name: "exa", fn: () => exaSearch(query, depth), breaker: breakers.exa },
    { name: "tavily", fn: () => tavilySearch(query, depth), breaker: breakers.tavily },
    { name: "fallback", fn: () => fallbackSearch(query), breaker: breakers.fallback },
  ];

  for (const layer of layers) {
    if (layer.breaker.isOpen()) {
      console.error(`[deep-search] ${layer.name} breaker OPEN, skipping`);
      continue;
    }

    try {
      const results = await withTimeout(layer.fn(), 15000);
      if (results && results.length > 0) {
        layer.breaker.recordSuccess();
        console.error(`[deep-search] ${layer.name} returned ${results.length} results`);
        return { provider: layer.name, results };
      }
      // Empty results: try next
      console.error(`[deep-search] ${layer.name} returned 0 results`);
    } catch (err) {
      layer.breaker.recordFailure();
      console.error(`[deep-search] ${layer.name} failed: ${err.message}`);
    }
  }

  return { provider: "none", results: [] };
}

// === CLI ===
const args = process.argv.slice(2);
let query = "", depth = "deep";
for (let i = 0; i < args.length; i++) {
  if (args[i] === "--query" && args[i + 1]) query = args[++i];
  else if (args[i] === "--depth" && args[i + 1]) depth = args[++i];
  else if (!args[i].startsWith("--")) query = args[i];
}

if (!query) {
  console.error("Usage: search-engine.mjs --query 'your question' [--depth quick|deep|max]");
  process.exit(1);
}

const result = await deepSearch(query, depth);
console.log(JSON.stringify(result, null, 2));
