"""
Report Swarm — 统一任务编排引擎
核心决策模块：解析用户意图，判断复杂度，选择执行路径
"""

import re
import json
import logging
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# ─── 枚举定义 ────────────────────────────────────────────────────────────────

class ExecutionMode(Enum):
    DIRECT = "direct"              # 直接执行（简单任务）
    CREWAI = "crewai"              # CrewAI pipeline（中等任务）
    CLAWTEAM = "clawteam"          # ClawTeam（用户明确指定）
    CREWAI_CLAWTEAM = "crewai+clawteam"  # 联合编排（复杂任务）


class Complexity(Enum):
    SIMPLE = "simple"       # 直接执行
    MEDIUM = "medium"       # CrewAI
    COMPLEX = "complex"     # CrewAI + ClawTeam


# ─── 数据模型 ────────────────────────────────────────────────────────────────

@dataclass
class TaskIntent:
    """解析后的用户任务意图"""
    raw_input: str                     # 原始输入
    task_goal: str                      # 核心任务目标
    user_mode: Optional[str] = None    # 用户指定的模式（crewai/clawteam/...）
    user_subtasks: Optional[int] = None  # 用户指定的子任务数
    complexity: Complexity = Complexity.MEDIUM  # 系统判断的复杂度
    decision: ExecutionMode = ExecutionMode.CREWAI  # 最终执行决策
    reason: str = ""                   # 决策理由
    subtasks_identified: List[str] = field(default_factory=list)  # 识别出的子任务列表


@dataclass
class ExecutionPlan:
    """执行计划"""
    mode: ExecutionMode
    complexity: Complexity
    subtasks: List[str]
    crewai_roles: List[str] = field(default_factory=list)
    clawteam_workers: List[str] = field(default_factory=list)
    estimated_duration: str = ""
    manifest_path: str = ""


# ─── 用户模式识别 ─────────────────────────────────────────────────────────────

MODE_PATTERNS = [
    (r"crewai\s*\+\s*clawteam", ExecutionMode.CREWAI_CLAWTEAM, "用户强制 crewai+clawteam"),
    (r"全开|全部", ExecutionMode.CREWAI_CLAWTEAM, "用户要求全开模式"),
    (r"clawteam|claw-team|claw-team", ExecutionMode.CLAWTEAM, "用户强制 clawteam"),
    (r"crewai", ExecutionMode.CREWAI, "用户强制 crewai"),
    (r"自动|默认|auto", None, "用户要求自动判断"),
    (r"直接|简单|快速", ExecutionMode.DIRECT, "用户要求简单直接"),
]

SUBTASK_PATTERNS = [
    r"(\d+)\s*个?\s*子任务",
    r"(\d+)\s*步",
    r"(\d+)\s*阶段",
    r"分\s*(\d+)\s*步",
]


# ─── 复杂度关键词 ──────────────────────────────────────────────────────────────

COMPLEXITY_KEYWORDS = {
    Complexity.SIMPLE: [
        "告诉我", "查一下", "多少钱", "怎么做", "是什么",
        "翻译", "改写", "润色", "总结", "一句话",
        "查查", "看一下",
    ],
    Complexity.MEDIUM: [
        "分析", "调研", "报告", "对比", "评估",
        "研究", "策划", "方案", "建议", "调查",
        "写一篇", "做一份", "出一份",
    ],
    Complexity.COMPLEX: [
        "行业", "市场", "竞品", "全面", "深度",
        "战略", "规划", "体系", "架构", "生态",
        "多维度", "多角度", "系统化",
    ],
}


# ─── 核心类 ───────────────────────────────────────────────────────────────────

class IntentParser:
    """解析用户输入，提取任务意图"""

    def parse(self, raw_input: str) -> TaskIntent:
        intent = TaskIntent(raw_input=raw_input, task_goal=raw_input)
        self._extract_user_mode(intent)
        self._extract_user_subtasks(intent)
        self._extract_task_goal(intent)
        return intent

    def _extract_user_mode(self, intent: TaskIntent) -> None:
        for pattern, mode, reason in MODE_PATTERNS:
            if re.search(pattern, intent.raw_input, re.IGNORECASE):
                if mode is not None:
                    intent.user_mode = mode.value
                else:
                    intent.user_mode = "auto"
                logger.info(f"识别到用户指定模式: {intent.user_mode}（{reason}）")
                return
        # 不清理 raw_input，保留关键词供后续步骤使用

    def _extract_user_subtasks(self, intent: TaskIntent) -> None:
        for pattern in SUBTASK_PATTERNS:
            m = re.search(pattern, intent.raw_input)
            if m:
                intent.user_subtasks = int(m.group(1))
                logger.info(f"识别到用户指定子任务数: {intent.user_subtasks}")
                return

    def _extract_task_goal(self, intent: TaskIntent) -> None:
        """从输入中提取核心任务目标，移除模式指定词"""
        goal = intent.raw_input
        # 移除已知的模式关键词
        for pattern, _, _ in MODE_PATTERNS:
            goal = re.sub(pattern, "", goal, flags=re.IGNORECASE)
        # 移除子任务数量
        for pattern in SUBTASK_PATTERNS:
            goal = re.sub(pattern, "", goal)
        # 清理多余空白
        goal = re.sub(r"\s+", " ", goal).strip()
        intent.task_goal = goal if goal else intent.raw_input


class ComplexityAnalyzer:
    """判断任务复杂度"""

    def analyze(self, intent: TaskIntent) -> Complexity:
        if intent.user_subtasks is not None:
            n = intent.user_subtasks
            if n <= 2:
                return Complexity.SIMPLE
            elif n <= 5:
                return Complexity.MEDIUM
            else:
                return Complexity.COMPLEX

        score = self._calc_complexity_score(intent.raw_input)
        if score <= 2:
            return Complexity.SIMPLE
        elif score <= 5:
            return Complexity.MEDIUM
        else:
            return Complexity.COMPLEX

    def _calc_complexity_score(self, text: str) -> int:
        score = 0
        t = text.lower()
        for keyword_list, complexity_level in [
            (COMPLEXITY_KEYWORDS[Complexity.SIMPLE], Complexity.SIMPLE),
            (COMPLEXITY_KEYWORDS[Complexity.MEDIUM], Complexity.MEDIUM),
            (COMPLEXITY_KEYWORDS[Complexity.COMPLEX], Complexity.COMPLEX),
        ]:
            for kw in keyword_list:
                if kw in t:
                    weight = {"simple": -2, "medium": 1, "complex": 2}[complexity_level.value]
                    score += weight
        # 也考虑子任务数量的间接指示
        if re.search(r"多[个步阶段]", text):
            score += 2
        if re.search(r"[3456][个步阶段]", text):
            score += 1
        return max(0, score)


class SwarmOrchestrator:
    """统一编排引擎：决策 + 计划生成"""

    def __init__(self):
        self.parser = IntentParser()
        self.analyzer = ComplexityAnalyzer()

    def plan(self, raw_input: str) -> ExecutionPlan:
        intent = self.parser.parse(raw_input)
        complexity = self.analyzer.analyze(intent)
        intent.complexity = complexity

        # 决策
        if intent.user_mode:
            mode = ExecutionMode(intent.user_mode)
            upgraded = self._maybe_upgrade(mode, complexity)
            intent.decision = upgraded
        else:
            intent.decision = self._complexity_to_mode(complexity)

        intent.reason = self._build_reason(intent)

        # 生成计划
        subtasks = self._identify_subtasks(intent)
        intent.subtasks_identified = subtasks

        plan = ExecutionPlan(
            mode=intent.decision,
            complexity=complexity,
            subtasks=subtasks,
            crewai_roles=self._assign_crewai_roles(intent),
            clawteam_workers=self._assign_clawteam_workers(intent),
        )
        logger.info(f"执行决策: {intent.decision.value}（{intent.reason}）")
        logger.info(f"识别子任务: {subtasks}")
        return plan

    def _maybe_upgrade(self, user_mode: ExecutionMode, complexity: Complexity) -> ExecutionMode:
        """升级规则：系统往上加，不往下减"""
        if user_mode == ExecutionMode.CREWAI and complexity == Complexity.COMPLEX:
            logger.info("系统升级: 用户选 CrewAI → 升级为 CrewAI+ClawTeam（任务太复杂）")
            return ExecutionMode.CREWAI_CLAWTEAM
        if user_mode == ExecutionMode.DIRECT and complexity != Complexity.SIMPLE:
            logger.info("系统升级: 用户选直接执行 → 升级为 CrewAI（任务非简单）")
            return ExecutionMode.CREWAI
        return user_mode

    def _complexity_to_mode(self, c: Complexity) -> ExecutionMode:
        return {
            Complexity.SIMPLE: ExecutionMode.DIRECT,
            Complexity.MEDIUM: ExecutionMode.CREWAI,
            Complexity.COMPLEX: ExecutionMode.CREWAI_CLAWTEAM,
        }[c]

    def _build_reason(self, intent: TaskIntent) -> str:
        parts = []
        if intent.user_mode:
            parts.append(f"用户指定: {intent.user_mode}")
        parts.append(f"系统判断: {intent.complexity.value}（{len(intent.subtasks_identified)} 个子任务）")
        if intent.user_mode:
            parts.append(f"系统升级: {intent.decision.value}")
        return "; ".join(parts)

    def _identify_subtasks(self, intent: TaskIntent) -> List[str]:
        """识别子任务"""
        if intent.user_subtasks:
            return [f"子任务 {i+1}" for i in range(intent.user_subtasks)]
        # 自动识别：从任务关键词推断常见子任务模式
        t = intent.task_goal.lower()
        if any(kw in t for kw in ["抖音", "小红书", "b站", "微信", "微博", "x.com"]):
            return ["平台概况研究", "竞品分析", "用户画像", "内容策略", "商业化分析"]
        if "竞品" in t:
            return ["数据收集", "竞品对比", "差异化分析", "机会点识别", "建议报告"]
        if "行业" in t:
            return ["行业概况", "市场规模", "主要玩家", "趋势分析", "投资建议"]
        if "调研" in t or "调查" in t:
            return ["背景研究", "数据收集", "访谈分析", "报告撰写", "总结建议"]
        return ["信息收集", "数据分析", "报告撰写"]

    def _assign_crewai_roles(self, intent: TaskIntent) -> List[str]:
        mode = intent.decision
        n = len(intent.subtasks_identified)
        if mode == ExecutionMode.DIRECT:
            return []
        if n <= 3:
            return ["Researcher", "Writer"]
        elif n <= 5:
            return ["Researcher", "Analyst", "Writer"]
        else:
            return ["Researcher", "DataCollector", "Analyst", "Writer", "Publisher"]

    def _assign_clawteam_workers(self, intent: TaskIntent) -> List[str]:
        if intent.decision not in (ExecutionMode.CLAWTEAM, ExecutionMode.CREWAI_CLAWTEAM):
            return []
        n = len(intent.subtasks_identified)
        workers = []
        for i in range(min(n, 6)):
            workers.append(f"worker-{i+1}")
        return workers


# ─── CLI 工具 ─────────────────────────────────────────────────────────────────

def decide_and_explain(raw_input: str) -> ExecutionPlan:
    """一步完成决策+解释"""
    orchestrator = SwarmOrchestrator()
    plan = orchestrator.plan(raw_input)
    return plan


def plan_to_markdown(plan: ExecutionPlan) -> str:
    """将执行计划输出为 markdown"""
    md = [
        f"## 执行计划",
        f"",
        f"| 项目 | 内容 |",
        f"|------|------|",
        f"| 执行模式 | `{plan.mode.value}` |",
        f"| 复杂度 | `{plan.complexity.value}` |",
        f"| 子任务数 | `{len(plan.subtasks)}` |",
        f"| CrewAI 角色 | `{', '.join(plan.crewai_roles) or '无'}` |",
        f"| ClawTeam Worker | `{', '.join(plan.clawteam_workers) or '无'}` |",
        f"",
        f"### 子任务列表",
    ]
    for i, st in enumerate(plan.subtasks, 1):
        md.append(f"{i}. {st}")
    return "\n".join(md)


if __name__ == "__main__":
    import sys
    test_inputs = [
        "做一份抖音市场分析报告",
        "帮我调研一下小红书，3个子任务",
        "用crewai做一份行业分析",
        "用clawteam并行处理这5个任务",
        "分析一下微信视频号的竞品情况，6个步骤",
        "简单润色一下这段文字",
        "帮我写一份b站up主研究报告，crewai+clawteam全开",
    ]
    for inp in test_inputs:
        plan = decide_and_explain(inp)
        print(f"\n输入: {inp}")
        print(plan_to_markdown(plan))
        print("---")
