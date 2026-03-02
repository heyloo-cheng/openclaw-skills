#!/usr/bin/env node
/**
 * LSS (Local Semantic Search) 适配器
 * 使用 LSS 进行本地项目文档搜索
 */

import { execSync } from 'child_process';
import { existsSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';

// 项目路径映射
const PROJECT_PATHS = {
  toolbox: '~/projects/ToolBox',
  clipmind: '~/projects/ClipMind',
  vaultmind: '~/projects/VaultMind',
};

/**
 * 搜索项目文档
 * @param {string} query - 搜索关键词
 * @param {Object} options - 搜索选项
 * @returns {Promise<Array>} 搜索结果
 */
export async function search(query, options = {}) {
  const {
    project = null,
    limit = 5,
    minScore = 0.0,
  } = options;

  try {
    // 确定搜索路径
    let searchPath = process.cwd();
    if (project && PROJECT_PATHS[project]) {
      searchPath = PROJECT_PATHS[project].replace('~', homedir());
      if (!existsSync(searchPath)) {
        console.warn(`[lss] Project path not found: ${searchPath}`);
        return [];
      }
    }

    // 构建 LSS 命令
    const cmd = `lss "${query}" "${searchPath}" --json`;
    
    // 执行搜索
    const output = execSync(cmd, {
      encoding: 'utf-8',
      maxBuffer: 10 * 1024 * 1024, // 10MB
      timeout: 30000, // 30s
    });

    // 解析结果
    const results = JSON.parse(output);
    if (!results || !Array.isArray(results) || results.length === 0) {
      return [];
    }

    const hits = results[0]?.hits || [];

    // 转换为统一格式
    return hits
      .filter(hit => hit.score >= minScore)
      .slice(0, limit)
      .map(hit => ({
        source: 'lss',
        score: hit.score,
        title: extractTitle(hit.file_path),
        path: hit.file_path,
        snippet: hit.snippet || '',
        context: project ? `Project: ${project}` : '',
        metadata: {
          rank_stage: hit.rank_stage,
          indexed_at: hit.indexed_at,
        },
      }));
  } catch (error) {
    console.error('[lss] Search failed:', error.message);
    return [];
  }
}

/**
 * 从文件路径提取标题
 */
function extractTitle(filePath) {
  const parts = filePath.split('/');
  const filename = parts[parts.length - 1];
  return filename.replace(/\.(md|txt)$/, '');
}

/**
 * 检查 LSS 是否可用
 */
export function isAvailable() {
  try {
    execSync('which lss', { encoding: 'utf-8' });
    return true;
  } catch {
    return false;
  }
}

// CLI 测试
if (import.meta.url === `file://${process.argv[1]}`) {
  const query = process.argv[2] || 'authentication';
  const project = process.argv[3] || null;

  console.log(`[lss] Testing search: "${query}"${project ? ` in ${project}` : ''}`);
  console.log(`[lss] Available: ${isAvailable()}`);

  search(query, { project, limit: 5 }).then(results => {
    console.log(`\n[lss] Found ${results.length} results:\n`);
    results.forEach((r, i) => {
      console.log(`${i + 1}. ${r.title} (score: ${r.score.toFixed(4)})`);
      console.log(`   Path: ${r.path}`);
      console.log(`   Snippet: ${r.snippet.substring(0, 100)}...`);
      console.log();
    });
  });
}
