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

/**
 * Main search function
 * @param {string} query - Search query
 * @param {Object} options - Search options
 * @returns {Promise<Object>} Search results with metadata
 */
export async function search(query, options = {}) {
  const startTime = Date.now();
  const limit = options.limit || 5;
  
  // Route the query
  const routing = routeQuery(query);
  const sources = routing.sources || [];
  const confidence = routing.confidence || 0.8; // Default confidence
  const reasoning = routing.reason || routing.reasoning || 'No specific routing rule matched';
  
  console.log(`[unified-search] Routing: ${sources.join(' + ')} (confidence: ${confidence})`);
  console.log(`[unified-search] Reasoning: ${reasoning}`);
  
  // Execute searches in parallel
  const searchPromises = sources.map(async (source) => {
    try {
      switch (source) {
        case 'lss':
          return { source: 'lss', results: await searchLSS(query, { limit }) };
        case 'memory':
          return { source: 'memory', results: await searchMemory(query, { limit }) };
        case 'files':
          return { source: 'files', results: await searchFiles(query, { limit }) };
        case 'web':
          return { source: 'web', results: await searchWeb(query, { limit, fetchContent: true }) };
        default:
          console.warn(`[unified-search] Unknown source: ${source}`);
          return { source, results: [] };
      }
    } catch (error) {
      console.error(`[unified-search] ${source} search failed:`, error.message);
      return { source, results: [] };
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
  
  return {
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
