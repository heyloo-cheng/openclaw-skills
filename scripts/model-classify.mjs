#!/usr/bin/env node
/**
 * model-classify.mjs — 判断消息复杂度，推荐模型
 * 用法: echo "message" | node model-classify.mjs
 *   或: node model-classify.mjs "message"
 */

const L1_PATTERNS = [
  /review|审查|检查代码|code review/i,
  /test|测试|单元测试|生成测试|补测试/i,
  /commit|提交/i,
  /deploy|部署|发布/i,
  /写.*功能|写.*代码|实现.*功能|build|create/i,
  /修.*bug|fix|修复/i,
  /文档|doc|readme/i,
  /重构|refactor/i,
  /估.*时|评估|estimate/i,
];

const L0_PATTERNS = [
  /^(hi|hello|hey|你好|嗨|早|晚安)/i,
  /天气|weather|气温|下雨/i,
  /几点|时间|日期|today|what time/i,
  /翻译|translate/i,
  /查(看|收)?邮件|check (email|inbox|mail)/i,
  /^(ok|好的|收到|谢谢|thanks|thx|got it)/i,
  /什么意思|是什么|what is|define/i,
  /提醒|remind/i,
  /日历|calendar|schedule/i,
];

const L2_PATTERNS = [
  /架构|architecture|设计方案|design/i,
  /头脑风暴|brainstorm|想法|ideas/i,
  /分析.*原因|root cause|深度分析/i,
  /重构.*整个|refactor.*entire|大规模/i,
  /多个文件|multiple files|跨模块/i,
  /为什么.*不工作|why.*not working|复杂.*bug/i,
  /规划|plan|strategy|策略/i,
  /对比.*方案|compare.*approach/i,
  /写一篇|write an article|长文/i,
  /创意|creative|故事|story/i,
];

const AGENT_DEFAULTS = {
  news: "L0",
  artist: "L1", // gemini, not in haiku/sonnet/opus tier
};

function classify(message, agent = "main") {
  // Agent override
  if (AGENT_DEFAULTS[agent]) {
    return { level: AGENT_DEFAULTS[agent], reason: `agent_default(${agent})` };
  }

  const len = message.length;

  // L0 pattern match
  for (const pat of L0_PATTERNS) {
    if (pat.test(message)) {
      return { level: "L0", reason: `pattern(${pat.source.slice(0, 20)})`, model: "claude-haiku" };
    }
  }

  // L2 pattern match
  for (const pat of L2_PATTERNS) {
    if (pat.test(message)) {
      return { level: "L2", reason: `pattern(${pat.source.slice(0, 20)})`, model: "claude-yunyi" };
    }
  }

  // L1 pattern match
  for (const pat of L1_PATTERNS) {
    if (pat.test(message)) {
      return { level: "L1", reason: `pattern(${pat.source.slice(0, 20)})`, model: "claude-sonnet" };
    }
  }

  // Length heuristic (adjusted for CJK: 1 CJK char ≈ 2-3 English chars)
  const cjkCount = (message.match(/[\u4e00-\u9fff\u3400-\u4dbf]/g) || []).length;
  const effectiveLen = len + cjkCount * 2; // CJK chars count triple

  if (effectiveLen < 30) {
    return { level: "L0", reason: `short(${len}→${effectiveLen})`, model: "claude-haiku" };
  }
  if (effectiveLen > 300) {
    return { level: "L2", reason: `long(${len}→${effectiveLen})`, model: "claude-yunyi" };
  }

  // Default: L1
  return { level: "L1", reason: "default", model: "claude-sonnet" };
}

// CLI
const msg = process.argv[2] || "";
if (!msg) {
  // Read from stdin
  let input = "";
  process.stdin.setEncoding("utf-8");
  process.stdin.on("data", chunk => input += chunk);
  process.stdin.on("end", () => {
    const result = classify(input.trim(), process.argv[3]);
    console.log(JSON.stringify(result));
  });
} else {
  const result = classify(msg, process.argv[3]);
  console.log(JSON.stringify(result));
}
