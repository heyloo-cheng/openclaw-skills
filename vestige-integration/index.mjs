import { spawn } from 'child_process';
import { promisify } from 'util';
import { exec as execCallback } from 'child_process';

const exec = promisify(execCallback);

// vestige CLI 路径
const VESTIGE_BIN = process.env.VESTIGE_BIN || `${process.env.HOME}/.local/bin/vestige`;
const VESTIGE_DATA_DIR = process.env.VESTIGE_DATA_DIR || `${process.env.HOME}/.vestige/data`;

/**
 * 存储记忆到 vestige
 * @param {Object} options
 * @param {string} options.text - 记忆内容
 * @param {string[]} options.tags - 标签列表
 * @param {number} options.importance - 重要性 (0-1)
 * @param {string} options.nodeType - 节点类型 (fact, concept, event, etc.)
 * @returns {Promise<Object>} 存储结果
 */
export async function store({ text, tags = [], importance = 0.7, nodeType = 'fact' }) {
  const tagsStr = tags.join(',');
  const cmd = `cd ${VESTIGE_DATA_DIR} && ${VESTIGE_BIN} ingest "${text}" --tags "${tagsStr}" --node-type ${nodeType}`;
  
  try {
    const { stdout, stderr } = await exec(cmd);
    
    // 解析输出
    const lines = stdout.split('\n');
    const decisionLine = lines.find(l => l.includes('Decision:'));
    const nodeIdLine = lines.find(l => l.includes('Node ID:'));
    
    const decision = decisionLine ? decisionLine.split(':')[1].trim() : 'unknown';
    const nodeId = nodeIdLine ? nodeIdLine.split(':')[1].trim() : null;
    
    return {
      success: true,
      decision,
      nodeId,
      text,
      tags,
      importance
    };
  } catch (error) {
    console.error('vestige store error:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * 从 vestige 检索记忆
 * @param {string} query - 搜索查询
 * @param {Object} options
 * @param {number} options.limit - 返回结果数量
 * @returns {Promise<Array>} 检索结果
 */
export async function recall(query, { limit = 5 } = {}) {
  // vestige export 需要输出文件参数
  const tmpFile = `/tmp/vestige-export-${Date.now()}.json`;
  const cmd = `cd ${VESTIGE_DATA_DIR} && ${VESTIGE_BIN} export ${tmpFile} 2>&1 && cat ${tmpFile} && rm ${tmpFile}`;
  
  try {
    const { stdout } = await exec(cmd);
    
    // 提取 JSON 部分（跳过统计信息）
    const jsonStart = stdout.indexOf('[');
    if (jsonStart === -1) {
      return [];
    }
    const jsonStr = stdout.slice(jsonStart);
    const memories = JSON.parse(jsonStr);
    
    // 简单的关键词匹配（实际应该用向量搜索）
    const results = memories
      .filter(m => m.content && m.content.toLowerCase().includes(query.toLowerCase()))
      .slice(0, limit)
      .map(m => ({
        id: m.id,
        text: m.content,
        tags: m.tags || [],
        retention: m.retentionStrength || 1.0,
        importance: m.utilityScore || 0.5,
        created: m.createdAt,
        lastAccessed: m.lastAccessed,
        stability: m.stability,
        difficulty: m.difficulty
      }));
    
    return results;
  } catch (error) {
    console.error('vestige recall error:', error);
    return [];
  }
}

/**
 * 获取复习计划
 * @returns {Promise<Array>} 需要复习的记忆列表
 */
export async function getReviewPlan() {
  const cmd = `cd ${VESTIGE_DATA_DIR} && ${VESTIGE_BIN} stats`;
  
  try {
    const { stdout } = await exec(cmd);
    
    // 解析统计信息
    const lines = stdout.split('\n');
    const dueForReviewLine = lines.find(l => l.includes('Due for Review:'));
    const dueCount = dueForReviewLine ? parseInt(dueForReviewLine.split(':')[1].trim()) : 0;
    
    return {
      dueCount,
      message: `${dueCount} memories due for review`
    };
  } catch (error) {
    console.error('vestige getReviewPlan error:', error);
    return { dueCount: 0, error: error.message };
  }
}

/**
 * 运行记忆巩固
 * @returns {Promise<Object>} 巩固结果
 */
export async function consolidate() {
  const cmd = `cd ${VESTIGE_DATA_DIR} && ${VESTIGE_BIN} consolidate`;
  
  try {
    const { stdout } = await exec(cmd);
    return {
      success: true,
      output: stdout
    };
  } catch (error) {
    console.error('vestige consolidate error:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * 健康检查
 * @returns {Promise<Object>} 健康状态
 */
export async function health() {
  const cmd = `cd ${VESTIGE_DATA_DIR} && ${VESTIGE_BIN} health`;
  
  try {
    const { stdout } = await exec(cmd);
    return {
      healthy: true,
      output: stdout
    };
  } catch (error) {
    console.error('vestige health error:', error);
    return {
      healthy: false,
      error: error.message
    };
  }
}

/**
 * 获取统计信息
 * @returns {Promise<Object>} 统计数据
 */
export async function stats() {
  const cmd = `cd ${VESTIGE_DATA_DIR} && ${VESTIGE_BIN} stats`;
  
  try {
    const { stdout } = await exec(cmd);
    
    // 解析统计信息
    const lines = stdout.split('\n');
    const parseValue = (key) => {
      const line = lines.find(l => l.includes(key));
      if (!line) return null;
      const value = line.split(':')[1].trim();
      return value;
    };
    
    return {
      totalMemories: parseInt(parseValue('Total Memories')) || 0,
      dueForReview: parseInt(parseValue('Due for Review')) || 0,
      averageRetention: parseFloat(parseValue('Average Retention')) || 0,
      embeddingCoverage: parseFloat(parseValue('Embedding Coverage')) || 0,
      raw: stdout
    };
  } catch (error) {
    console.error('vestige stats error:', error);
    return {
      totalMemories: 0,
      error: error.message
    };
  }
}

/**
 * 备份数据库
 * @param {string} outputPath - 备份文件路径
 * @returns {Promise<Object>} 备份结果
 */
export async function backup(outputPath) {
  const cmd = `cd ${VESTIGE_DATA_DIR} && ${VESTIGE_BIN} backup`;
  
  try {
    const { stdout } = await exec(cmd);
    return {
      success: true,
      output: stdout
    };
  } catch (error) {
    console.error('vestige backup error:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * 导出记忆
 * @param {Object} options
 * @param {string} options.format - 导出格式 (json, jsonl)
 * @returns {Promise<Array>} 导出的记忆列表
 */
export async function exportMemories({ format = 'json' } = {}) {
  const tmpFile = `/tmp/vestige-export-${Date.now()}.${format}`;
  const cmd = `cd ${VESTIGE_DATA_DIR} && ${VESTIGE_BIN} export ${tmpFile} 2>&1 && cat ${tmpFile} && rm ${tmpFile}`;
  
  try {
    const { stdout } = await exec(cmd);
    
    // 提取 JSON 部分
    const jsonStart = stdout.indexOf('[');
    if (jsonStart === -1) {
      return [];
    }
    const jsonStr = stdout.slice(jsonStart);
    return JSON.parse(jsonStr);
  } catch (error) {
    console.error('vestige export error:', error);
    return [];
  }
}

// 默认导出
export default {
  store,
  recall,
  getReviewPlan,
  consolidate,
  health,
  stats,
  backup,
  exportMemories
};
