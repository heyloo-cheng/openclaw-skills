#!/usr/bin/env node
/**
 * Search Cache Manager
 * Caches search results to reduce API calls and improve response time
 */

import { readFile, writeFile, mkdir } from 'fs/promises';
import { existsSync } from 'fs';
import { join, dirname } from 'path';
import { createHash } from 'crypto';

const CACHE_DIR = join(process.env.HOME, '.openclaw', 'workspace', 'data');
const CACHE_FILE = join(CACHE_DIR, 'search-cache.json');

// Default TTL (Time To Live) in seconds
const DEFAULT_TTL = {
  lss: 3600,      // 1 hour - local content changes slowly
  memory: 1800,   // 30 minutes - memory updates moderately
  files: 600,     // 10 minutes - files can change frequently
  web: 600        // 10 minutes - web content changes frequently
};

/**
 * Generate cache key from query and options
 */
function getCacheKey(source, query, options = {}) {
  const normalized = {
    source,
    query: query.toLowerCase().trim(),
    ...options
  };
  const str = JSON.stringify(normalized);
  return createHash('md5').update(str).digest('hex');
}

/**
 * Load cache from disk
 */
async function loadCache() {
  try {
    if (!existsSync(CACHE_FILE)) {
      return {};
    }
    const data = await readFile(CACHE_FILE, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    console.error('[cache] Failed to load cache:', error.message);
    return {};
  }
}

/**
 * Save cache to disk
 */
async function saveCache(cache) {
  try {
    // Ensure directory exists
    if (!existsSync(CACHE_DIR)) {
      await mkdir(CACHE_DIR, { recursive: true });
    }
    
    await writeFile(CACHE_FILE, JSON.stringify(cache, null, 2), 'utf8');
  } catch (error) {
    console.error('[cache] Failed to save cache:', error.message);
  }
}

/**
 * Get cached results
 */
export async function getCached(source, query, options = {}) {
  const cache = await loadCache();
  const key = getCacheKey(source, query, options);
  const entry = cache[key];
  
  if (!entry) {
    return null;
  }
  
  const now = Date.now();
  const age = (now - entry.timestamp) / 1000; // seconds
  const ttl = entry.ttl || DEFAULT_TTL[source] || 600;
  
  if (age > ttl) {
    // Expired
    return null;
  }
  
  console.log(`[cache] HIT ${source}:${query.slice(0, 30)} (age: ${age.toFixed(0)}s)`);
  return entry.results;
}

/**
 * Set cached results
 */
export async function setCached(source, query, results, options = {}) {
  const cache = await loadCache();
  const key = getCacheKey(source, query, options);
  const ttl = options.ttl || DEFAULT_TTL[source] || 600;
  
  cache[key] = {
    source,
    query,
    results,
    timestamp: Date.now(),
    ttl,
    options
  };
  
  await saveCache(cache);
  console.log(`[cache] SET ${source}:${query.slice(0, 30)} (ttl: ${ttl}s)`);
}

/**
 * Clear expired entries
 */
export async function cleanCache() {
  const cache = await loadCache();
  const now = Date.now();
  let cleaned = 0;
  
  for (const [key, entry] of Object.entries(cache)) {
    const age = (now - entry.timestamp) / 1000;
    const ttl = entry.ttl || DEFAULT_TTL[entry.source] || 600;
    
    if (age > ttl) {
      delete cache[key];
      cleaned++;
    }
  }
  
  if (cleaned > 0) {
    await saveCache(cache);
    console.log(`[cache] Cleaned ${cleaned} expired entries`);
  }
  
  return cleaned;
}

/**
 * Clear all cache
 */
export async function clearCache() {
  await saveCache({});
  console.log('[cache] Cleared all cache');
}

/**
 * Get cache statistics
 */
export async function getCacheStats() {
  const cache = await loadCache();
  const now = Date.now();
  const stats = {
    total: 0,
    bySource: {},
    expired: 0,
    totalSize: 0
  };
  
  for (const entry of Object.values(cache)) {
    stats.total++;
    stats.bySource[entry.source] = (stats.bySource[entry.source] || 0) + 1;
    
    const age = (now - entry.timestamp) / 1000;
    const ttl = entry.ttl || DEFAULT_TTL[entry.source] || 600;
    
    if (age > ttl) {
      stats.expired++;
    }
    
    stats.totalSize += JSON.stringify(entry).length;
  }
  
  return stats;
}

// CLI usage
if (import.meta.url === `file://${process.argv[1]}`) {
  const command = process.argv[2];
  
  switch (command) {
    case 'clean':
      cleanCache().then(count => {
        console.log(`Cleaned ${count} entries`);
      });
      break;
    
    case 'clear':
      clearCache();
      break;
    
    case 'stats':
      getCacheStats().then(stats => {
        console.log('Cache Statistics:');
        console.log(`  Total entries: ${stats.total}`);
        console.log(`  Expired: ${stats.expired}`);
        console.log(`  Size: ${(stats.totalSize / 1024).toFixed(2)} KB`);
        console.log('  By source:');
        for (const [source, count] of Object.entries(stats.bySource)) {
          console.log(`    ${source}: ${count}`);
        }
      });
      break;
    
    default:
      console.log('Usage: node cache.mjs [clean|clear|stats]');
      console.log('  clean - Remove expired entries');
      console.log('  clear - Remove all entries');
      console.log('  stats - Show cache statistics');
  }
}

export default { getCached, setCached, cleanCache, clearCache, getCacheStats };
