#!/usr/bin/env node
/**
 * 电商选品完整工作流
 * 
 * 功能：
 * 1. 查询 1688 价格（Deep Search + 缓存）
 * 2. 查询闲鱼竞品价格
 * 3. 计算毛利率
 * 4. 竞争度分析
 * 5. 生成选品报告
 * 
 * 使用方法：
 *   node ecommerce_product_research.mjs "迷你加湿器"
 */

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

// 配置
const MIN_MARGIN = 0.5;  // 最低毛利率 50%
const MAX_PRICE = 400;   // 最高售价 400 元

/**
 * 查询 1688 价格
 */
async function query1688Price(keyword) {
  console.log('🔍 查询 1688 价格...');
  
  const scriptPath = path.join(
    process.env.HOME,
    '.openclaw/workspace/.agents/skills/scrapling/search_1688_cached.mjs'
  );
  
  try {
    const result = execSync(
      `node "${scriptPath}" "${keyword}"`,
      { encoding: 'utf-8', maxBuffer: 10 * 1024 * 1024 }
    );
    
    // 解析输出
    const priceMatch = result.match(/价格范围: ¥([\d.]+) - ¥([\d.]+)/);
    const avgMatch = result.match(/平均价格: ¥([\d.]+)/);
    
    if (priceMatch && avgMatch) {
      return {
        min: parseFloat(priceMatch[1]),
        max: parseFloat(priceMatch[2]),
        avg: parseFloat(avgMatch[1]),
        source: '1688'
      };
    }
    
    return null;
  } catch (e) {
    console.error('❌ 1688 查询失败:', e.message);
    return null;
  }
}

/**
 * 查询闲鱼竞品价格
 */
async function queryXianyuPrice(keyword) {
  console.log('🔍 查询闲鱼竞品价格...');
  
  try {
    // 直接调用 Python 脚本
    const scriptPath = path.join(
      process.env.HOME,
      '.openclaw/workspace/.agents/skills/scrapling/xianyu_search_direct.py'
    );
    
    const result = execSync(
      `python3 "${scriptPath}" "${keyword}"`,
      { encoding: 'utf-8', maxBuffer: 10 * 1024 * 1024, timeout: 30000 }
    );
    
    // 解析 JSON 输出
    const data = JSON.parse(result);
    
    if (data.success && data.count > 0) {
      return {
        min: data.min,
        max: data.max,
        avg: data.avg,
        count: data.count,
        source: '闲鱼'
      };
    }
    
    return null;
  } catch (e) {
    console.error('⚠️  闲鱼查询失败，使用估算价格');
    return null;
  }
}

/**
 * 计算毛利率
 */
function calculateMargin(cost, price) {
  return (price - cost) / price;
}

/**
 * 评估竞争度
 */
function evaluateCompetition(xianyuData) {
  if (!xianyuData) {
    return { level: 'unknown', score: 0, reason: '无闲鱼数据' };
  }
  
  const count = xianyuData.count;
  const priceRange = xianyuData.max - xianyuData.min;
  const avgPrice = xianyuData.avg;
  
  // 竞争度评分（0-100）
  let score = 0;
  let reasons = [];
  
  // 1. 商品数量（权重 40%）
  if (count < 50) {
    score += 40;
    reasons.push('商品数量少（低竞争）');
  } else if (count < 200) {
    score += 20;
    reasons.push('商品数量中等');
  } else {
    score += 0;
    reasons.push('商品数量多（高竞争）');
  }
  
  // 2. 价格分散度（权重 30%）
  const dispersion = priceRange / avgPrice;
  if (dispersion > 0.5) {
    score += 30;
    reasons.push('价格分散（机会大）');
  } else if (dispersion > 0.3) {
    score += 15;
    reasons.push('价格较分散');
  } else {
    score += 0;
    reasons.push('价格集中（竞争激烈）');
  }
  
  // 3. 平均价格（权重 30%）
  if (avgPrice > 100) {
    score += 30;
    reasons.push('客单价高（利润空间大）');
  } else if (avgPrice > 50) {
    score += 15;
    reasons.push('客单价中等');
  } else {
    score += 0;
    reasons.push('客单价低');
  }
  
  // 确定竞争等级
  let level;
  if (score >= 70) {
    level = 'low';
  } else if (score >= 40) {
    level = 'medium';
  } else {
    level = 'high';
  }
  
  return { level, score, reasons };
}

/**
 * 生成选品建议
 */
function generateRecommendation(data) {
  const { price1688, priceXianyu, margin, competition } = data;
  
  // 检查条件
  const checks = {
    margin: margin >= MIN_MARGIN,
    price: priceXianyu.avg <= MAX_PRICE,
    competition: competition.level !== 'high',
    data: price1688 && priceXianyu
  };
  
  // 生成建议
  if (!checks.data) {
    return {
      recommendation: 'data_insufficient',
      reason: '数据不足，无法评估',
      score: 0
    };
  }
  
  if (priceXianyu.avg > MAX_PRICE) {
    return {
      recommendation: 'exceeds_max_price',
      reason: `售价超过上限（¥${MAX_PRICE}）`,
      score: 0
    };
  }
  
  if (margin < MIN_MARGIN) {
    return {
      recommendation: 'low_margin',
      reason: `毛利率过低（${(margin * 100).toFixed(1)}% < ${MIN_MARGIN * 100}%）`,
      score: 20
    };
  }
  
  if (competition.level === 'high') {
    return {
      recommendation: 'high_competition',
      reason: '竞争激烈，需谨慎',
      score: 40
    };
  }
  
  // 计算综合评分
  const marginScore = Math.min(margin * 100, 100);
  const competitionScore = competition.score;
  const finalScore = (marginScore * 0.6 + competitionScore * 0.4);
  
  if (finalScore >= 70) {
    return {
      recommendation: 'highly_recommended',
      reason: '高毛利 + 低竞争，强烈推荐',
      score: finalScore
    };
  } else if (finalScore >= 50) {
    return {
      recommendation: 'recommended',
      reason: '综合条件良好，推荐',
      score: finalScore
    };
  } else {
    return {
      recommendation: 'caution',
      reason: '综合条件一般，需谨慎',
      score: finalScore
    };
  }
}

/**
 * 主函数
 */
async function main() {
  const keyword = process.argv[2];
  
  if (!keyword) {
    console.error('用法: node ecommerce_product_research.mjs <关键词>');
    process.exit(1);
  }
  
  console.log('🚀 电商选品完整分析');
  console.log('='.repeat(60));
  console.log(`关键词: ${keyword}`);
  console.log();
  
  // 1. 查询 1688 价格
  const price1688 = await query1688Price(keyword);
  
  if (!price1688) {
    console.log('❌ 无法获取 1688 价格，终止分析');
    process.exit(1);
  }
  
  console.log(`✅ 1688 成本: ¥${price1688.min.toFixed(2)} - ¥${price1688.max.toFixed(2)}`);
  console.log(`   平均成本: ¥${price1688.avg.toFixed(2)}`);
  console.log();
  
  // 2. 查询闲鱼价格
  const priceXianyu = await queryXianyuPrice(keyword);
  
  let xianyuPrice = priceXianyu;
  if (!xianyuPrice) {
    // 使用估算价格（1688 价格 * 3）
    console.log('⚠️  使用估算价格（1688 * 3）');
    xianyuPrice = {
      min: price1688.min * 3,
      max: price1688.max * 3,
      avg: price1688.avg * 3,
      count: 0,
      source: '估算'
    };
  }
  
  console.log(`✅ 闲鱼售价: ¥${xianyuPrice.min.toFixed(2)} - ¥${xianyuPrice.max.toFixed(2)}`);
  console.log(`   平均售价: ¥${xianyuPrice.avg.toFixed(2)}`);
  if (xianyuPrice.count > 0) {
    console.log(`   商品数量: ${xianyuPrice.count}`);
  }
  console.log();
  
  // 3. 计算毛利率
  const margin = calculateMargin(price1688.avg, xianyuPrice.avg);
  
  console.log('📊 毛利率分析');
  console.log('='.repeat(60));
  console.log(`成本: ¥${price1688.avg.toFixed(2)}`);
  console.log(`售价: ¥${xianyuPrice.avg.toFixed(2)}`);
  console.log(`毛利: ¥${(xianyuPrice.avg - price1688.avg).toFixed(2)}`);
  console.log(`毛利率: ${(margin * 100).toFixed(1)}%`);
  console.log();
  
  // 4. 竞争度分析
  const competition = evaluateCompetition(xianyuPrice);
  
  console.log('🎯 竞争度分析');
  console.log('='.repeat(60));
  console.log(`竞争等级: ${competition.level.toUpperCase()}`);
  console.log(`竞争评分: ${competition.score}/100`);
  console.log('原因:');
  competition.reasons.forEach(r => console.log(`  - ${r}`));
  console.log();
  
  // 5. 生成选品建议
  const recommendation = generateRecommendation({
    price1688,
    priceXianyu: xianyuPrice,
    margin,
    competition
  });
  
  console.log('💡 选品建议');
  console.log('='.repeat(60));
  console.log(`建议: ${recommendation.recommendation.toUpperCase()}`);
  console.log(`原因: ${recommendation.reason}`);
  console.log(`综合评分: ${recommendation.score.toFixed(1)}/100`);
  console.log();
  
  // 6. 保存报告
  const report = {
    keyword,
    timestamp: new Date().toISOString(),
    price1688,
    priceXianyu: xianyuPrice,
    margin,
    competition,
    recommendation
  };
  
  const reportDir = path.join(process.env.HOME, '.openclaw/workspace/data/product-research');
  if (!fs.existsSync(reportDir)) {
    fs.mkdirSync(reportDir, { recursive: true });
  }
  
  const reportPath = path.join(reportDir, `${keyword}_${Date.now()}.json`);
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
  
  console.log('💾 报告已保存');
  console.log(`   ${reportPath}`);
  console.log();
  console.log('✅ 分析完成!');
}

main().catch(e => {
  console.error('❌ 错误:', e.message);
  process.exit(1);
});
