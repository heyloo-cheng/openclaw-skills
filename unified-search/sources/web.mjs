#!/usr/bin/env node
/**
 * Web Search Adapter
 * Uses web-search-proxy for direct Brave Search API calls
 */

import { searchWeb as searchWebProxy, isAvailable as isProxyAvailable } from '../scripts/web-search-proxy.mjs';

/**
 * Search the web
 * @param {string} query - Search query
 * @param {Object} options - Search options
 * @returns {Promise<Array>} Search results
 */
export async function searchWeb(query, options = {}) {
  return searchWebProxy(query, options);
}

/**
 * Check if web search is available
 * @returns {Promise<boolean>}
 */
export async function isAvailable() {
  return isProxyAvailable();
}

export default { searchWeb, isAvailable };
