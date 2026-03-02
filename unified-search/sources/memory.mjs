#!/usr/bin/env node
/**
 * Memory Search Adapter
 * Searches OpenClaw's long-term memory (LanceDB)
 * Note: This is a placeholder - actual implementation requires direct LanceDB access
 */

/**
 * Search memory (placeholder)
 * @param {string} query - Search query
 * @param {Object} options - Search options
 * @returns {Promise<Array>} Search results
 */
export async function searchMemory(query, options = {}) {
  // TODO: Implement direct LanceDB query
  // For now, return empty results
  console.warn('[memory] Direct memory search not yet implemented');
  return [];
}

/**
 * Check if memory search is available
 * @returns {Promise<boolean>}
 */
export async function isAvailable() {
  return false; // Disabled until implemented
}

export default { searchMemory, isAvailable };
