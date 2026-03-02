#!/usr/bin/env node
/**
 * Memory Search Adapter
 * Direct LanceDB access via @lancedb/lancedb
 */

import * as lancedb from '@lancedb/lancedb';
import { homedir } from 'os';
import { join } from 'path';

const DB_PATH = join(homedir(), '.openclaw', 'memory', 'lancedb-pro');
const TABLE_NAME = 'memories';

/**
 * Search memory using direct LanceDB access
 * @param {string} query - Search query
 * @param {Object} options - Search options
 * @returns {Promise<Array>} Search results
 */
export async function searchMemory(query, options = {}) {
  const limit = options.limit || 5;
  const minScore = options.minScore || 0.3;
  
  try {
    // Connect to LanceDB (new API)
    const db = await lancedb.connect(DB_PATH);
    
    // Open table (new API)
    const table = await db.openTable(TABLE_NAME);
    
    // Perform full-text search
    // Note: .search() does FTS, .vectorSearch() does vector search
    const results = await table
      .search(query)
      .limit(limit * 3) // Get more candidates for filtering
      .toArray(); // New API: toArray() instead of execute()
    
    if (!results || results.length === 0) {
      return [];
    }
    
    // Transform and filter results
    const memories = results
      .filter(row => {
        // Filter by score if available
        if (row._distance !== undefined) {
          // LanceDB returns distance, lower is better
          // Convert to similarity score (0-1)
          const score = Math.max(0, 1 - row._distance);
          return score >= minScore;
        }
        return true;
      })
      .slice(0, limit)
      .map((row, index) => {
        const score = row._distance !== undefined 
          ? Math.max(0, 1 - row._distance)
          : 0.7 - index * 0.05;
        
        const text = row.text || row.content || '';
        const category = row.category || 'memory';
        
        return {
          title: `[${category}] ${text.slice(0, 60)}...`,
          content: text,
          score,
          source: 'memory',
          metadata: {
            category,
            importance: row.importance,
            scope: row.scope,
            timestamp: row.timestamp,
            memoryId: row.id
          }
        };
      });
    
    return memories;
  } catch (error) {
    console.error('[memory] Search failed:', error.message);
    return [];
  }
}

/**
 * Check if memory search is available
 * @returns {Promise<boolean>}
 */
export async function isAvailable() {
  try {
    const { existsSync } = await import('fs');
    return existsSync(DB_PATH);
  } catch {
    return false;
  }
}

export default { searchMemory, isAvailable };
