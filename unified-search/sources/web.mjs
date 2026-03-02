#!/usr/bin/env node
/**
 * Web Search Adapter
 * Placeholder for web search integration
 * Note: Actual web search should be called from the main agent context
 */

/**
 * Search the web (placeholder)
 * @param {string} query - Search query
 * @param {Object} options - Search options
 * @returns {Promise<Array>} Search results
 */
export async function searchWeb(query, options = {}) {
  // TODO: Implement web search via agent tool call
  // For now, return empty results
  console.warn('[web] Web search should be called from agent context');
  return [];
}

/**
 * Check if web search is available
 * @returns {Promise<boolean>}
 */
export async function isAvailable() {
  return false; // Disabled until implemented properly
}

export default { searchWeb, isAvailable };
