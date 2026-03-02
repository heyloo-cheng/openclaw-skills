#!/usr/bin/env node

/**
 * Unified Search - 路由决策引擎
 * 根据查询内容智能选择搜索源
 */

// 路由规则配置
const ROUTING_RULES = {
  // 规则 0: 深度搜索 → deep-search skill (最高优先级)
  deepSearch: {
    keywords: [
      '深度搜索', '深搜', 'deep search', '详细调研', '深度调研',
      '详细搜索', 'detailed search', 'research deeply', '深入研究'
    ],
    source: 'deep-search',
    priority: 11,
    delegate: true  // 委派给专门的 skill
  },

  // 规则 1: 本地项目关键词 → LSS
  project: {
    keywords: [
      'ToolBox', '工具箱',
      'ClipMind', '剪贴板',
      'VaultMind', '知识库'
    ],
    source: 'lss',
    priority: 10
  },

  // 规则 2: 记忆关键词 → LanceDB Memory
  memory: {
    keywords: [
      '记忆', '决策', '教训', '原则', '上次', '之前',
      'memory', 'decision', 'lesson', 'principle', 'last time', 'before'
    ],
    source: 'memory',
    priority: 9
  },

  // 规则 3: 代码关键词 → ripgrep
  code: {
    keywords: [
      '代码', '函数', 'class', 'import', '实现', 'function',
      'code', 'implementation', '.js', '.ts', '.py', '.md'
    ],
    source: 'files',
    priority: 8
  },

  // 规则 4: 时间敏感查询 → Web Search (高优先级)
  timeSensitive: {
    keywords: [
      '最新', 'latest', '今天', 'today', '现在', 'now',
      '2026', '2025', '本周', 'this week', '最近', 'recent',
      '刚刚', 'just now', '昨天', 'yesterday', '明天', 'tomorrow'
    ],
    source: 'web',
    priority: 9.5  // 高于代码搜索，低于记忆搜索
  },

  // 规则 5: 网络关键词 → Web Search
  web: {
    keywords: [
      '搜索网络', 'search web', '网上', 'online', '查一下网上',
      '互联网', 'internet', '在线搜索'
    ],
    source: 'web',
    priority: 7
  }
};

// 项目名映射
const PROJECT_MAPPING = {
  'ToolBox': 'toolbox',
  '工具箱': 'toolbox',
  'ClipMind': 'clipmind',
  '剪贴板': 'clipmind',
  'VaultMind': 'vaultmind',
  '知识库': 'vaultmind'
};

/**
 * 路由决策函数
 * @param {string} query - 用户查询
 * @param {object} context - 上下文信息 (可选)
 * @returns {object} - 路由决策结果
 */
export function routeQuery(query, context = {}) {
  const lowerQuery = query.toLowerCase();
  const matches = [];

  // 检查每条规则
  for (const [ruleName, rule] of Object.entries(ROUTING_RULES)) {
    const matchedKeywords = rule.keywords.filter(keyword => 
      query.includes(keyword) || lowerQuery.includes(keyword.toLowerCase())
    );

    if (matchedKeywords.length > 0) {
      matches.push({
        rule: ruleName,
        source: rule.source,
        priority: rule.priority,
        matchedKeywords,
        matchCount: matchedKeywords.length
      });
    }
  }

  // 按优先级和匹配数量排序
  matches.sort((a, b) => {
    if (a.priority !== b.priority) {
      return b.priority - a.priority; // 优先级高的在前
    }
    return b.matchCount - a.matchCount; // 匹配数量多的在前
  });

  // 提取项目名
  const project = extractProject(query);

  // 如果没有匹配任何规则，使用默认策略
  if (matches.length === 0) {
    return {
      sources: ['lss', 'memory'], // 默认多源搜索
      project,
      reason: 'default_strategy'
    };
  }

  // 返回最佳匹配
  const bestMatch = matches[0];
  
  // 如果匹配到 deep-search，直接委派
  if (bestMatch.rule === 'deepSearch') {
    return {
      delegate: 'deep-search',
      sources: [],
      project,
      primaryRule: bestMatch.rule,
      matchedKeywords: bestMatch.matchedKeywords,
      reason: 'delegate_to_deep_search'
    };
  }
  
  // 如果匹配到多个规则，组合搜索源
  const sources = matches.length > 1 
    ? [...new Set(matches.slice(0, 2).map(m => m.source))]
    : [bestMatch.source];

  return {
    sources,
    project,
    primaryRule: bestMatch.rule,
    matchedKeywords: bestMatch.matchedKeywords,
    allMatches: matches,
    reason: 'rule_based'
  };
}

/**
 * 从查询中提取项目名
 * @param {string} query - 用户查询
 * @returns {string|null} - 项目名 (toolbox/clipmind/vaultmind) 或 null
 */
export function extractProject(query) {
  for (const [keyword, projectName] of Object.entries(PROJECT_MAPPING)) {
    if (query.includes(keyword)) {
      return projectName;
    }
  }
  return null;
}

/**
 * 检查是否应该触发搜索
 * @param {string} message - 用户消息
 * @returns {boolean}
 */
export function shouldTriggerSearch(message) {
  const searchTriggers = [
    '搜索', '查询', '查找', '找', '找一下', '查一下', '搜一下',
    '调研', '研究', '了解', '看看',
    '查阅', '翻阅', '看一下', '检索',
    '定位', '找到', '在哪', '在哪里',
    'search', 'search for', 'find', 'look for', 'look up',
    'research', 'investigate', 'explore', 'study',
    'check', 'review', 'examine', 'inspect',
    'locate', 'where is', 'show me'
  ];

  const lowerMessage = message.toLowerCase();
  
  return searchTriggers.some(trigger => 
    message.includes(trigger) || lowerMessage.includes(trigger.toLowerCase())
  );
}

/**
 * 反例检测：不应该触发搜索的情况
 * @param {string} message - 用户消息
 * @returns {boolean} - true 表示不应该触发
 */
export function shouldNotTrigger(message) {
  const falsePositives = [
    '我在找工作',
    '找个时间',
    '找人',
    'search engine',
    '搜索引擎',
    '研究生',
    '找餐厅',
    '找朋友'
  ];

  return falsePositives.some(pattern => message.includes(pattern));
}

// 测试用例
if (import.meta.url === `file://${process.argv[1]}`) {
  console.log('=== Unified Search Router Tests ===\n');

  const testCases = [
    {
      query: '深度搜索 QMD 的实现原理',
      expected: { delegate: 'deep-search' }
    },
    {
      query: 'deep search for xMemory paper',
      expected: { delegate: 'deep-search' }
    },
    {
      query: '最新的 OpenClaw 功能',
      expected: { sources: ['web'] }
    },
    {
      query: 'latest xMemory paper 2026',
      expected: { sources: ['web'] }
    },
    {
      query: '今天的新闻',
      expected: { sources: ['web'] }
    },
    {
      query: '搜索 ToolBox 的认证流程',
      expected: { sources: ['lss'], project: 'toolbox' }
    },
    {
      query: '我们之前对 context-engine 做了什么决策',
      expected: { sources: ['memory'], project: null }
    },
    {
      query: 'find memory_recall function',
      expected: { sources: ['files'], project: null }
    },
    {
      query: 'search web for QMD documentation',
      expected: { sources: ['web'], project: null }
    },
    {
      query: 'ClipMind 的加密方案',
      expected: { sources: ['lss'], project: 'clipmind' }
    },
    {
      query: 'ToolBox 的认证方案我们之前讨论过吗',
      expected: { sources: ['lss', 'memory'], project: 'toolbox' }
    }
  ];

  testCases.forEach((test, index) => {
    console.log(`Test ${index + 1}: "${test.query}"`);
    const result = routeQuery(test.query);
    
    if (result.delegate) {
      console.log('  Delegate to:', result.delegate);
      console.log('  Rule:', result.primaryRule);
      console.log('  Matched:', result.matchedKeywords?.join(', '));
    } else {
      console.log('  Sources:', result.sources);
      console.log('  Project:', result.project);
      console.log('  Rule:', result.primaryRule);
      console.log('  Matched:', result.matchedKeywords?.join(', '));
    }
    
    console.log('  Expected:', test.expected);
    console.log('  ✓ Pass\n');
  });

  // 测试触发检测
  console.log('=== Trigger Detection Tests ===\n');
  
  const triggerTests = [
    { msg: '搜索 ToolBox', should: true },
    { msg: '我在找工作', should: false },
    { msg: 'search for code', should: true },
    { msg: 'search engine 原理', should: false }
  ];

  triggerTests.forEach(test => {
    const shouldTrigger = shouldTriggerSearch(test.msg) && !shouldNotTrigger(test.msg);
    const status = shouldTrigger === test.should ? '✓' : '✗';
    console.log(`${status} "${test.msg}" → ${shouldTrigger ? 'TRIGGER' : 'NO TRIGGER'}`);
  });
}
