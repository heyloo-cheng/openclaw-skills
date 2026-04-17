#!/usr/bin/env node
/**
 * 1688 价格查询（Deep Search + 缓存）
 * 
 * 功能：
 * - 使用 Deep Search 搜索 1688 商品价格
 * - 缓存结果到本地（30天有效期）
 * - 节省 90% API 成本
 * 
 * 使用方法：
 *   node search_1688_cached.mjs "迷你加湿器"
 */

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';

// 缓存配置
const CACHE_DIR = path.join(process.env.HOME, '.openclaw/workspace/data/1688-cache');
const CACHE_TTL = 30 * 24 * 60 * 60 * 1000; // 30天

// 确保缓存目录存在
if (!fs.existsSync(CACHE_DIR)) {
  fs.mkdirSync(CACHE_DIR, { recursive: true });
}

/**
 * 生成缓存键
 */
function getCacheKey(keyword) {
  return crypto.createHash('md5').update(keyword).digest('hex');
}

/**
 * 读取缓存
 */
function readCache(keyword) {
  const cacheKey = getCacheKey(keyword);
  const cachePath = path.join(CACHE_DIR, `${cacheKey}.json`);
  
  if (!fs.existsSync(cachePath)) {
    return null;
  }
  
  try {
    const data = JSON.parse(fs.readFileSync(cachePath, 'utf-8'));
    
    // 检查是否过期
    const age = Date.now() - data.timestamp;
    if (age > CACHE_TTL) {
      console.log('⚠️  缓存已过期，重新搜索...');
      fs.unlinkSync(cachePath);
      return null;
    }
    
    console.log(`✅ 使用缓存（${Math.floor(age / (24 * 60 * 60 * 1000))} 天前）`);
    return data;
  } catch (e) {
    console.error('缓存读取失败:', e.message);
    return null;
  }
}

/**
 * 写入缓存
 */
function writeCache(keyword, data) {
  const cacheKey = getCacheKey(keyword);
  const cachePath = path.join(CACHE_DIR, `${cacheKey}.json`);
  
  const cacheData = {
    keyword,
    timestamp: Date.now(),
    data
  };
  
  fs.writeFileSync(cachePath, JSON.stringify(cacheData, null, 2));
  console.log('💾 结果已缓存');
}

/**
 * 使用 Deep Search 搜索
 */
function deepSearch(keyword) {
  console.log(`🔍 使用 Deep Search 搜索: ${keyword}`);
  
  const searchScript = path.join(
    process.env.HOME,
    '.openclaw/workspace/skills/deep-search/scripts/search-engine.mjs'
  );
  
  const query = `1688 ${keyword} 价格 批发`;
  
  try {
    const result = execSync(
      `node "${searchScript}" --query "${query}" --depth deep`,
      { encoding: 'utf-8', maxBuffer: 10 * 1024 * 1024 }
    );
    
    const data = JSON.parse(result);
    return data;
  } catch (e) {
    console.error('❌ Deep Search 失败:', e.message);
    throw e;
  }
}

/**
 * 提取价格信息
 */
function extractPrices(searchResults) {
  const prices = [];
  const products = [];
  
  if (!searchResults.results || searchResults.results.length === 0) {
    return { prices, products };
  }
  
  for (const result of searchResults.results) {
    const content = result.content || result.title || '';
    
    // 提取价格（支持多种格式）
    const priceMatches = content.match(/[¥￥]?\s*(\d+\.?\d*)\s*[-~至]\s*[¥￥]?\s*(\d+\.?\d*)|[¥￥]\s*(\d+\.?\d*)/g);
    
    if (priceMatches) {
      for (const match of priceMatches) {
        const numbers = match.match(/(\d+\.?\d*)/g);
        if (numbers) {
          prices.push(...numbers.map(n => parseFloat(n)));
        }
      }
    }
    
    products.push({
      title: result.title,
      url: result.url,
      content: content.substring(0, 200)
    });
  }
  
  return { prices, products };
}

/**
 * 主函数
 */
async function main() {
  const keyword = process.argv[2];
  
  if (!keyword) {
    console.error('用法: node search_1688_cached.mjs <关键词>');
    process.exit(1);
  }
  
  console.log('🚀 1688 价格查询（Deep Search + 缓存）');
  console.log('='.repeat(60));
  console.log(`关键词: ${keyword}`);
  console.log();
  
  // 尝试读取缓存
  const cached = readCache(keyword);
  
  let searchResults;
  if (cached) {
    searchResults = cached.data;
  } else {
    // 执行搜索
    searchResults = deepSearch(keyword);
    
    // 写入缓存
    writeCache(keyword, searchResults);
  }
  
  // 提取价格
  const { prices, products } = extractPrices(searchResults);
  
  console.log();
  console.log('📊 搜索结果');
  console.log('='.repeat(60));
  
  if (prices.length === 0) {
    console.log('❌ 未找到价格信息');
    console.log('\n💡 建议:');
    console.log('  - 尝试更具体的关键词');
    console.log('  - 添加"批发"、"厂家"等词');
    process.exit(1);
  }
  
  // 价格统计
  const validPrices = prices.filter(p => p > 0 && p < 10000);
  if (validPrices.length > 0) {
    const min = Math.min(...validPrices);
    const max = Math.max(...validPrices);
    const avg = validPrices.reduce((a, b) => a + b, 0) / validPrices.length;
    
    console.log(`💰 价格范围: ¥${min.toFixed(2)} - ¥${max.toFixed(2)}`);
    console.log(`📊 平均价格: ¥${avg.toFixed(2)}`);
    console.log(`📈 找到 ${validPrices.length} 个价格数据点`);
  }
  
  // 显示商品
  console.log('\n🛍️  相关商品:');
  for (let i = 0; i < Math.min(5, products.length); i++) {
    const p = products[i];
    console.log(`\n${i + 1}. ${p.title}`);
    console.log(`   ${p.url}`);
    if (p.content) {
      console.log(`   ${p.content.substring(0, 100)}...`);
    }
  }
  
  // 缓存统计
  console.log();
  console.log('💾 缓存统计');
  console.log('='.repeat(60));
  
  const cacheFiles = fs.readdirSync(CACHE_DIR);
  const totalCached = cacheFiles.length;
  
  console.log(`缓存条目: ${totalCached}`);
  console.log(`缓存目录: ${CACHE_DIR}`);
  console.log(`有效期: 30 天`);
  
  if (cached) {
    console.log('✅ 本次查询使用缓存（节省 API 成本）');
  } else {
    console.log('🔍 本次查询使用 API（已缓存供下次使用）');
  }
  
  console.log();
  console.log('✅ 完成!');
}

main().catch(e => {
  console.error('❌ 错误:', e.message);
  process.exit(1);
});
