#!/usr/bin/env node
/**
 * Local Files Search Adapter
 * Searches files in workspace using ripgrep
 */

import { execSync } from 'child_process';
import { existsSync } from 'fs';
import { resolve } from 'path';

/**
 * Search local files using ripgrep
 * @param {string} query - Search query
 * @param {Object} options - Search options
 * @returns {Promise<Array>} Search results
 */
export async function searchFiles(query, options = {}) {
  const limit = options.limit || 5;
  const searchPath = options.path || process.env.HOME + '/.openclaw/workspace';
  
  if (!existsSync(searchPath)) {
    console.error('[files] Search path does not exist:', searchPath);
    return [];
  }
  
  try {
    // Use ripgrep for fast file search
    const cmd = `rg --json --max-count 3 --ignore-case "${query}" "${searchPath}" 2>/dev/null | head -n ${limit * 10}`;
    const output = execSync(cmd, { encoding: 'utf8', timeout: 5000, maxBuffer: 1024 * 1024 });
    
    const lines = output.trim().split('\n').filter(Boolean);
    const results = [];
    
    for (const line of lines) {
      try {
        const item = JSON.parse(line);
        
        if (item.type === 'match') {
          const relativePath = item.data.path.text.replace(searchPath + '/', '');
          const lineNum = item.data.line_number;
          const matchText = item.data.lines.text.trim();
          
          results.push({
            title: `${relativePath}:${lineNum}`,
            content: matchText,
            score: 0.8, // Fixed score for file matches
            source: 'files',
            metadata: {
              path: item.data.path.text,
              line: lineNum,
              relativePath
            }
          });
          
          if (results.length >= limit) break;
        }
      } catch (parseError) {
        // Skip invalid JSON lines
        continue;
      }
    }
    
    return results;
  } catch (error) {
    // ripgrep returns exit code 1 when no matches found
    if (error.status === 1) {
      return [];
    }
    console.error('[files] Search failed:', error.message);
    return [];
  }
}

/**
 * Check if ripgrep is available
 * @returns {Promise<boolean>}
 */
export async function isAvailable() {
  try {
    execSync('which rg', { encoding: 'utf8', timeout: 1000 });
    return true;
  } catch {
    return false;
  }
}

export default { searchFiles, isAvailable };
