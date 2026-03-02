#!/usr/bin/env node
/**
 * Search Quality Feedback Tracker
 * Records search effectiveness to optimize routing thresholds
 */

import { readFile, writeFile, mkdir } from 'fs/promises';
import { existsSync } from 'fs';
import { join } from 'path';

const DATA_DIR = join(process.env.HOME, '.openclaw', 'workspace', 'data');
const FEEDBACK_FILE = join(DATA_DIR, 'search-feedback.jsonl');

/**
 * Record search feedback
 * @param {Object} searchResult - Result from search()
 * @param {Object} feedback - User feedback
 */
export async function recordFeedback(searchResult, feedback = {}) {
  const entry = {
    timestamp: Date.now(),
    query: searchResult.query,
    sources: searchResult.metadata.sources,
    confidence: searchResult.metadata.confidence,
    reasoning: searchResult.metadata.reasoning,
    totalResults: searchResult.metadata.totalResults,
    returnedResults: searchResult.metadata.returnedResults,
    elapsedMs: searchResult.metadata.elapsedMs,
    
    // Feedback signals
    userSatisfied: feedback.satisfied ?? null,
    followUpQuery: feedback.followUpQuery ?? null,
    clickedResult: feedback.clickedResult ?? null,
    fallbackTriggered: feedback.fallbackTriggered ?? false,
    
    // Auto-detected signals
    noResults: searchResult.results.length === 0,
    lowScores: searchResult.results.length > 0 && searchResult.results[0].score < 0.5,
    multiSource: searchResult.metadata.sources.length > 1
  };
  
  // Ensure directory exists
  if (!existsSync(DATA_DIR)) {
    await mkdir(DATA_DIR, { recursive: true });
  }
  
  // Append to JSONL file
  const line = JSON.stringify(entry) + '\n';
  await writeFile(FEEDBACK_FILE, line, { flag: 'a', encoding: 'utf8' });
  
  console.log('[feedback] Recorded:', entry.query);
}

/**
 * Analyze feedback to generate insights
 */
export async function analyzeFeedback(options = {}) {
  const days = options.days || 7;
  const cutoff = Date.now() - days * 24 * 60 * 60 * 1000;
  
  if (!existsSync(FEEDBACK_FILE)) {
    return {
      totalSearches: 0,
      insights: []
    };
  }
  
  const data = await readFile(FEEDBACK_FILE, 'utf8');
  const lines = data.trim().split('\n').filter(Boolean);
  
  const entries = lines
    .map(line => {
      try {
        return JSON.parse(line);
      } catch {
        return null;
      }
    })
    .filter(e => e && e.timestamp >= cutoff);
  
  // Calculate statistics
  const stats = {
    totalSearches: entries.length,
    bySource: {},
    avgElapsedMs: 0,
    noResultsRate: 0,
    lowScoreRate: 0,
    fallbackRate: 0,
    satisfactionRate: 0
  };
  
  let totalElapsed = 0;
  let noResults = 0;
  let lowScores = 0;
  let fallbacks = 0;
  let satisfiedCount = 0;
  let satisfiedTotal = 0;
  
  for (const entry of entries) {
    // By source
    for (const source of entry.sources) {
      stats.bySource[source] = (stats.bySource[source] || 0) + 1;
    }
    
    totalElapsed += entry.elapsedMs;
    if (entry.noResults) noResults++;
    if (entry.lowScores) lowScores++;
    if (entry.fallbackTriggered) fallbacks++;
    
    if (entry.userSatisfied !== null) {
      satisfiedTotal++;
      if (entry.userSatisfied) satisfiedCount++;
    }
  }
  
  stats.avgElapsedMs = Math.round(totalElapsed / entries.length);
  stats.noResultsRate = (noResults / entries.length * 100).toFixed(1) + '%';
  stats.lowScoreRate = (lowScores / entries.length * 100).toFixed(1) + '%';
  stats.fallbackRate = (fallbacks / entries.length * 100).toFixed(1) + '%';
  stats.satisfactionRate = satisfiedTotal > 0
    ? (satisfiedCount / satisfiedTotal * 100).toFixed(1) + '%'
    : 'N/A';
  
  // Generate insights
  const insights = [];
  
  if (noResults / entries.length > 0.2) {
    insights.push({
      type: 'warning',
      message: `High no-results rate (${stats.noResultsRate}). Consider expanding search sources or lowering thresholds.`
    });
  }
  
  if (lowScores / entries.length > 0.3) {
    insights.push({
      type: 'warning',
      message: `High low-score rate (${stats.lowScoreRate}). Results may not be relevant enough.`
    });
  }
  
  if (stats.avgElapsedMs > 5000) {
    insights.push({
      type: 'info',
      message: `Average search time is ${stats.avgElapsedMs}ms. Consider enabling cache.`
    });
  }
  
  const mostUsedSource = Object.entries(stats.bySource)
    .sort((a, b) => b[1] - a[1])[0];
  
  if (mostUsedSource) {
    insights.push({
      type: 'info',
      message: `Most used source: ${mostUsedSource[0]} (${mostUsedSource[1]} searches)`
    });
  }
  
  return { stats, insights, entries };
}

/**
 * Clean old feedback entries
 */
export async function cleanFeedback(daysToKeep = 30) {
  if (!existsSync(FEEDBACK_FILE)) {
    return 0;
  }
  
  const cutoff = Date.now() - daysToKeep * 24 * 60 * 60 * 1000;
  const data = await readFile(FEEDBACK_FILE, 'utf8');
  const lines = data.trim().split('\n').filter(Boolean);
  
  const kept = lines.filter(line => {
    try {
      const entry = JSON.parse(line);
      return entry.timestamp >= cutoff;
    } catch {
      return false;
    }
  });
  
  await writeFile(FEEDBACK_FILE, kept.join('\n') + '\n', 'utf8');
  
  const removed = lines.length - kept.length;
  console.log(`[feedback] Cleaned ${removed} old entries, kept ${kept.length}`);
  return removed;
}

// CLI usage
if (import.meta.url === `file://${process.argv[1]}`) {
  const command = process.argv[2];
  
  switch (command) {
    case 'analyze':
      const days = parseInt(process.argv[3]) || 7;
      analyzeFeedback({ days }).then(result => {
        console.log('\n=== Search Quality Analysis ===\n');
        console.log('Statistics:');
        console.log(`  Total searches: ${result.stats.totalSearches}`);
        console.log(`  Avg response time: ${result.stats.avgElapsedMs}ms`);
        console.log(`  No results rate: ${result.stats.noResultsRate}`);
        console.log(`  Low score rate: ${result.stats.lowScoreRate}`);
        console.log(`  Fallback rate: ${result.stats.fallbackRate}`);
        console.log(`  Satisfaction rate: ${result.stats.satisfactionRate}`);
        console.log('\nBy source:');
        for (const [source, count] of Object.entries(result.stats.bySource)) {
          console.log(`  ${source}: ${count}`);
        }
        console.log('\nInsights:');
        result.insights.forEach(insight => {
          const icon = insight.type === 'warning' ? '⚠️' : 'ℹ️';
          console.log(`  ${icon} ${insight.message}`);
        });
      });
      break;
    
    case 'clean':
      const keep = parseInt(process.argv[3]) || 30;
      cleanFeedback(keep);
      break;
    
    default:
      console.log('Usage: node feedback.mjs [analyze|clean] [days]');
      console.log('  analyze [days] - Analyze feedback from last N days (default: 7)');
      console.log('  clean [days]   - Remove feedback older than N days (default: 30)');
  }
}

export default { recordFeedback, analyzeFeedback, cleanFeedback };
