/**
 * context-engine: Topic-based dynamic context loading for OpenClaw
 * 
 * Inspired by virtual-context's 3-layer architecture:
 * - Layer 0: Active turns (in context window)
 * - Layer 1: Topic segment summaries (compressed)
 * - Layer 2: Tag summaries (bird's-eye view)
 * 
 * Uses before_prompt_build hook to dynamically load only relevant context.
 */

import type { OpenClawPluginApi } from "openclaw/plugin-sdk";

// --- Types ---

interface TopicEntry {
  tag: string;
  summary: string;
  messageCount: number;
  lastSeen: number;
  tokens: number;
}

interface TopicStore {
  topics: Map<string, TopicEntry>;
  currentTopic: string | null;
}

// --- Topic Classification ---

const TOPIC_PATTERNS: Record<string, RegExp[]> = {
  coding: [/代码|code|bug|fix|refactor|review|commit|git|deploy|test|编程|开发|重构/i],
  config: [/配置|config|设置|setting|plugin|插件|install|安装/i],
  memory: [/记忆|memory|lancedb|recall|store|记录/i],
  skill: [/skill|技能|router|路由|trigger|触发/i],
  agent: [/agent|委派|delegate|thinker|coder|writer|artist/i],
  security: [/安全|security|audit|审计|secureclaw|权限/i],
  search: [/搜索|search|查找|find|github|reddit/i],
  planning: [/计划|plan|roadmap|路线|phase|阶段/i],
  chat: [/聊天|chat|闲聊|你好|hi|hello/i],
};

function classifyTopic(prompt: string): string {
  for (const [topic, patterns] of Object.entries(TOPIC_PATTERNS)) {
    for (const p of patterns) {
      if (p.test(prompt)) return topic;
    }
  }
  return "general";
}

// --- Summary Generation ---

function generateTopicSummary(messages: unknown[], topic: string): string {
  // Extract text from messages related to this topic
  const relevant: string[] = [];
  for (const msg of messages) {
    const m = msg as Record<string, unknown>;
    const content = String(m.content || "");
    if (classifyTopic(content) === topic) {
      const role = String(m.role || "unknown");
      relevant.push(`[${role}] ${content.slice(0, 200)}`);
    }
  }
  if (relevant.length === 0) return "";
  // Keep last 3 exchanges as summary
  const kept = relevant.slice(-6);
  return `[Topic: ${topic}] ${kept.length} recent exchanges:\n${kept.join("\n")}`;
}

// --- Plugin ---

const store: TopicStore = {
  topics: new Map(),
  currentTopic: null,
};

export default function contextEngine(api: OpenClawPluginApi) {
  const logger = api.logger;
  logger.info("[context-engine] v0.1.0 initializing — topic-based dynamic context loading");

  // Hook: before_prompt_build
  // Fires before the system prompt is assembled.
  // We classify the current message's topic, then inject only relevant context.
  api.on("before_prompt_build", (event, ctx) => {
    const { prompt, messages } = event;
    const currentTopic = classifyTopic(prompt);
    const previousTopic = store.currentTopic;

    // Topic switch detected
    if (previousTopic && previousTopic !== currentTopic) {
      logger.info(`[context-engine] Topic switch: ${previousTopic} → ${currentTopic}`);

      // Compress the old topic into a summary
      const oldSummary = generateTopicSummary(messages, previousTopic);
      if (oldSummary) {
        store.topics.set(previousTopic, {
          tag: previousTopic,
          summary: oldSummary,
          messageCount: messages.length,
          lastSeen: Date.now(),
          tokens: oldSummary.length / 4, // rough estimate
        });
      }
    }

    store.currentTopic = currentTopic;

    // Build dynamic context: current topic full + other topics as 1-line summaries
    const contextParts: string[] = [];
    contextParts.push(`<context-engine topic="${currentTopic}">`);

    // Add summaries of other topics (compressed)
    for (const [tag, entry] of store.topics) {
      if (tag !== currentTopic && entry.summary) {
        // Only include 1-line summary for non-active topics
        const oneLiner = entry.summary.split("\n")[0];
        contextParts.push(`  [${tag}] ${oneLiner} (${entry.messageCount} msgs, last: ${new Date(entry.lastSeen).toLocaleTimeString()})`);
      }
    }

    contextParts.push("</context-engine>");

    // Only prepend if we have compressed topics
    if (store.topics.size > 0) {
      return {
        prependContext: contextParts.join("\n"),
      };
    }

    return undefined;
  });

  // Hook: llm_output — track topic after each response
  api.on("llm_output", (event, ctx) => {
    const texts = event.assistantTexts || [];
    if (texts.length > 0 && store.currentTopic) {
      const existing = store.topics.get(store.currentTopic);
      if (existing) {
        existing.lastSeen = Date.now();
        existing.messageCount++;
      }
    }
  });

  // Hook: before_compaction — save all topic summaries before compaction wipes history
  api.on("before_compaction", (event, ctx) => {
    logger.info(`[context-engine] Pre-compaction: saving ${store.topics.size} topic summaries`);
    // Topics are already in memory store, they survive compaction
  });

  logger.info(`[context-engine] Registered hooks: before_prompt_build, llm_output, before_compaction`);
}
