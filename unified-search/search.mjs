#!/usr/bin/env node
/**
 * Unified Search - Main Entry Point
 * Routes queries to appropriate search sources and combines results
 */

import { routeQuery } from './router.mjs';
import { search as searchLSS } from './sources/lss.mjs';
import { searchMemory } from './sources/memory.mjs';
import { searchFiles } from './sources/files.mjs';
import { searchWeb } from './sources/web.mjs';
import { getCached, setCached } from './cache.mjs';
import { recordFeedback } from './feedback.mjs';
import { readFile } from 'fs/promises';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const CONFIG_PATH = join(__dirname, 'config.json');

/**
 * Load configuration
 */
async function loadConfig() {
  try {
    const data = await readFile(CONFIG_PATH, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    console.warn('[unified-search] Failed to load config, using defaults');
    return { cache: { enabled: false } };
  }
}

/**
 * Main search function
 * @param {string} query - Search query
 * @param {Object} options - Search options
 * @returns {Promise<Object>} Search results with metadata
 */
export async function search(query, options = {}) {
  const startTime = Date.now();
  const limit = options.limit || 5;
  const config = await loadConfig();
  const cacheEnabled = config.cache?.enabled ?? false;
  
  // Route the query
  const routing = routeQuery(query);
  const sources = routing.sources || [];
  const confidence = routing.confidence || 0.8; // Default confidence
  const reasoning = routing.reason || routing.reasoning || 'No specific routing rule matched';
  
  console.log(`[unified-search] Routing: ${sources.join(' + ')} (confidence: ${confidence})`);
  console.log(`[unified-search] Reasoning: ${reasoning}`);
  
  // Execute searches in parallel with caching
  const searchPromises = sources.map(async (source) => {
    try {
      // Check cache first
      if (cacheEnabled) {
        const cached = await getCached(source, query, { limit });
        if (cached) {
          return { source, results: cached, fromCache: true };
        }
      }
      
      // Execute search
      let results;
      switch (source) {
        case 'lss':
          results = await searchLSS(query, { limit });
          break;
        case 'memory':
          results = await searchMemory(query, { limit });
          break;
        case 'files':
          results = await searchFiles(query, { limit });
          break;
        case 'web':
          results = await searchWeb(query, { limit, fetchContent: true });
          break;
        default:
          console.warn(`[unified-search] Unknown source: ${source}`);
          results = [];
      }
      
      // Cache results
      if (cacheEnabled && results.length > 0) {
        await setCached(source, query, results, { limit });
      }
      
      return { source, results, fromCache: false };
    } catch (error) {
      console.error(`[unified-search] ${source} search failed:`, error.message);
      return { source, results: [], fromCache: false };
    }
  });
  
  const searchResults = await Promise.all(searchPromises);
  
  // Combine and deduplicate results
  const allResults = [];
  const seenContent = new Set();
  
  for (const { source, results } of searchResults) {
    for (const result of results) {
      // Normalize content field (some sources use 'snippet')
      if (!result.content && result.snippet) {
        result.content = result.snippet;
      }
      
      // Ensure content exists
      if (!result.content) {
        result.content = result.title || '';
      }
      
      // Simple deduplication by content similarity
      const contentKey = result.content.slice(0, 100).toLowerCase();
      if (!seenContent.has(contentKey)) {
        seenContent.add(contentKey);
        allResults.push(result);
      }
    }
  }
  
  // Sort by score (descending)
  allResults.sort((a, b) => b.score - a.score);
  
  // Limit total results
  const finalResults = allResults.slice(0, limit);
  
  const elapsedMs = Date.now() - startTime;
  
  const searchResponse = {
    query,
    results: finalResults,
    metadata: {
      sources: sources,
      confidence,
      reasoning,
      totalResults: allResults.length,
      returnedResults: finalResults.length,
      elapsedMs,
      timestamp: new Date().toISOString()
    }
  };
  
  // Auto-record feedback (async, don't wait)
  recordFeedback(searchResponse, {
    fallbackTriggered: false // TODO: detect fallback
  }).catch(err => console.error('[feedback] Failed to record:', err.message));
  
  return searchResponse;
}

/**
 * Format search results for display
 * @param {Object} searchResponse - Response from search()
 * @returns {string} Formatted output
 */
export function formatResults(searchResponse) {
  const { query, results, metadata } = searchResponse;
  
  let output = `🔍 Search: "${query}"\n`;
  output += `📊 Sources: ${metadata.sources.join(' + ')} (${metadata.elapsedMs}ms)\n`;
  output += `💡 ${metadata.reasoning}\n\n`;
  
  if (results.length === 0) {
    output += '❌ No results found.\n';
    return output;
  }
  
  results.forEach((result, index) => {
    const stars = '★'.repeat(Math.ceil(result.score * 5));
    const sourceEmoji = {
      lss: '📁',
      memory: '🧠',
      files: '📄',
      web: '🌐'
    }[result.source] || '❓';
    
    output += `${index + 1}. ${sourceEmoji} ${result.title}\n`;
    output += `   Score: ${stars} (${result.score.toFixed(2)})\n`;
    output += `   ${result.content.slice(0, 200)}${result.content.length > 200 ? '...' : ''}\n`;
    
    if (result.metadata?.url) {
      output += `   🔗 ${result.metadata.url}\n`;
    }
    
    output += '\n';
  });
  
  return output;
}

// CLI usage
if (import.meta.url === `file://${process.argv[1]}`) {
  const query = process.argv[2];
  
  if (!query) {
    console.error('Usage: node search.mjs "your query"');
    process.exit(1);
  }
  
  search(query)
    .then(response => {
      console.log(formatResults(response));
      
      // Also output JSON for programmatic use
      if (process.argv.includes('--json')) {
        console.log('\n--- JSON ---');
        console.log(JSON.stringify(response, null, 2));
      }
    })
    .catch(error => {
      console.error('Search failed:', error);
      process.exit(1);
    });
}

export default { search, formatResults };
