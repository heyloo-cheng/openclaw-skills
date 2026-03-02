#!/usr/bin/env node
/**
 * Web Search Proxy
 * Direct Brave Search API calls
 */

import https from 'https';

const BRAVE_API_KEY = process.env.BRAVE_SEARCH_API_KEY;
const BRAVE_API_URL = 'https://api.search.brave.com/res/v1/web/search';

/**
 * Search the web using Brave Search API
 * @param {string} query - Search query
 * @param {Object} options - Search options
 * @returns {Promise<Array>} Search results
 */
export async function searchWeb(query, options = {}) {
  const limit = options.limit || 5;
  const freshness = options.freshness || null; // 'pd', 'pw', 'pm', 'py'
  
  if (!BRAVE_API_KEY) {
    console.warn('[web] BRAVE_SEARCH_API_KEY not set, returning empty results');
    return [];
  }
  
  const url = new URL(BRAVE_API_URL);
  url.searchParams.set('q', query);
  url.searchParams.set('count', limit);
  if (freshness) {
    url.searchParams.set('freshness', freshness);
  }
  
  return new Promise((resolve, reject) => {
    const req = https.get(url, {
      headers: {
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip',
        'X-Subscription-Token': BRAVE_API_KEY
      }
    }, (res) => {
      let data = '';
      
      // Handle gzip encoding
      const encoding = res.headers['content-encoding'];
      if (encoding === 'gzip') {
        const zlib = require('zlib');
        const gunzip = zlib.createGunzip();
        res.pipe(gunzip);
        gunzip.on('data', chunk => data += chunk);
        gunzip.on('end', () => parseResponse(data, resolve, reject));
      } else {
        res.on('data', chunk => data += chunk);
        res.on('end', () => parseResponse(data, resolve, reject));
      }
    });
    
    req.on('error', (error) => {
      console.error('[web] Request failed:', error.message);
      resolve([]); // Return empty instead of rejecting
    });
    
    req.setTimeout(10000, () => {
      req.destroy();
      console.error('[web] Request timeout');
      resolve([]);
    });
  });
}

/**
 * Parse Brave Search API response
 */
function parseResponse(data, resolve, reject) {
  try {
    const json = JSON.parse(data);
    
    if (!json.web || !json.web.results) {
      console.warn('[web] No results in response');
      resolve([]);
      return;
    }
    
    const results = json.web.results.map((r, index) => ({
      title: r.title || 'Untitled',
      content: r.description || '',
      score: 0.9 - index * 0.1,
      source: 'web',
      metadata: {
        url: r.url,
        age: r.age,
        favicon: r.profile?.img
      }
    }));
    
    resolve(results);
  } catch (error) {
    console.error('[web] Failed to parse response:', error.message);
    resolve([]);
  }
}

/**
 * Check if web search is available
 * @returns {boolean}
 */
export function isAvailable() {
  return !!BRAVE_API_KEY;
}

// CLI test
if (import.meta.url === `file://${process.argv[1]}`) {
  const query = process.argv[2] || 'test query';
  
  console.log(`[web] Testing search: "${query}"`);
  console.log(`[web] API key available: ${isAvailable()}`);
  
  searchWeb(query, { limit: 3 }).then(results => {
    console.log(`\n[web] Found ${results.length} results:\n`);
    results.forEach((r, i) => {
      console.log(`${i + 1}. ${r.title} (score: ${r.score.toFixed(2)})`);
      console.log(`   URL: ${r.metadata.url}`);
      console.log(`   ${r.content.substring(0, 100)}...`);
      console.log();
    });
  });
}

export default { searchWeb, isAvailable };
