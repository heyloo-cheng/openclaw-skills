"""
Report Swarm — CrewAI Pipeline
封装 CrewAI Flow，支持 OpenClaw Agent 作为 Tool/Crew 角色
CrewAI 角色 -> OpenClaw Agent Tool -> OpenClaw 真实 agent 执行
"""

import sys
import os
import time
import logging
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).parent
OPENCLAW_BASE = Path.home() / ".openclaw"
CREWAI_DIR = OPENCLAW_BASE / "crewai"

# 所有外部依赖用 lazy import，避免顶层加载时触发 crewai 包初始化
HAS_CREWAI = None
HAS_LANGCHAIN = None


def _lazy_import_crewai():
    """延迟导入 CrewAI（避免顶层加载时触发 PermissionError）"""
    global HAS_CREWAI, HAS_LANGCHAIN
    if HAS_CREWAI is not None:
        return HAS_CREWAI

    import importlib
    spec = importlib.util.find_spec("crewai")
    if spec is None:
        HAS_CREWAI = False
        HAS_LANGCHAIN = False
        logger.warning("CrewAI 未安装，将使用 fallback 模式")
        return False

    try:
        # 直接 import，不通过 sys.path.insert
        from crewai.flow import Flow, listen, start
        from crewai import Agent, Task, Crew
        HAS_CREWAI = True
        logger.info("CrewAI 加载成功")
    except ImportError:
        HAS_CREWAI = False
        logger.warning("CrewAI 未安装，将使用 fallback 模式")

    try:
        from langchain_openai import ChatOpenAI
        HAS_LANGCHAIN = True
    except ImportError:
        HAS_LANGCHAIN = False

    return HAS_CREWAI


# ─── OpenClaw Agent Tool（连接 CrewAI 与 OpenClaw）───────────────────────────

class OpenClawAgentTool:
    """
    CrewAI Tool：将 OpenClaw agent 封装为 CrewAI 可调用的 Tool。
    CrewAI Agent 通过这个 Tool 调用真实的 OpenClaw agent 完成子任务。
    """

    name: str = "openclaw_agent"
    description: str = "调用 OpenClaw agent 执行任务（用于研究、分析、写作等）"

    def __init__(self, agent_id: str = "main", thinking: str = "medium", timeout: int = 300):
        self.agent_id = agent_id
        self.thinking = thinking
        self.timeout = timeout

    def _run(self, task: str) -> str:
        """同步调用 OpenClaw agent"""
        import subprocess
        cmd = [
            "openclaw",
            "agent",
            "-m", task,
            "--agent", self.agent_id,
            "--thinking", self.thinking,
        ]
        try:
            result = subprocess.run(
                cmd,
                cwd=str(OPENCLAW_BASE),
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            if result.returncode == 0:
                return result.stdout
            else:
                logger.error(f"OpenClaw agent error: {result.stderr}")
                return f"Error: {result.stderr}"
        except subprocess.TimeoutExpired:
            return f"Error: Task timed out after {self.timeout}s"
        except FileNotFoundError:
            return "Error: openclaw CLI not found"
        except Exception as e:
            return f"Error: {str(e)}"


# ─── CrewAI Flow 状态 ────────────────────────────────────────────────────────

# 使用 Dict 代替 TypedDict，避免顶层导入
# ReportFlowState = TypedDict("ReportFlowState", {...})  # 备选
FlowState = Dict[str, Any]


# ─── CrewAI Flow 定义 ────────────────────────────────────────────────────────

if _lazy_import_crewai():
    from crewai.flow import Flow, listen, start
    from crewai import Agent, Task, Crew
    from typing import TypedDict

    class ReportFlowState(TypedDict):
        goal: str
        research_data: List[str]
        analysis_data: Dict[str, Any]
        draft: str
        final_report: str
        published: bool

    class ReportFlow(Flow[ReportFlowState]):
        """
        研究 -> 分析 -> 写作 -> 发布 流水线。
        每个阶段调用 OpenClaw Agent Tool，由真实的 OpenClaw agent 执行。
        """

        def __init__(self, goal: str, tool_timeout: int = 300):
            super().__init__()
            self.goal = goal
            self.tool_timeout = tool_timeout
            self._setup_tools()

        def _setup_tools(self):
            """初始化 OpenClaw Agent Tools"""
            self.research_tool = OpenClawAgentTool(
                agent_id="main",
                thinking="high",
                timeout=self.tool_timeout,
            )
            self.analysis_tool = OpenClawAgentTool(
                agent_id="thinker",
                thinking="high",
                timeout=self.tool_timeout,
            )
            self.writer_tool = OpenClawAgentTool(
                agent_id="writer",
                thinking="medium",
                timeout=self.tool_timeout,
            )

        @start()
        def research_phase(self) -> List[str]:
            """研究阶段：并行收集多个维度的信息"""
            logger.info("=== 研究阶段开始 ===")
            queries = [
                f"收集 {self.goal} 的背景信息、市场概况、主要玩家",
                f"调研 {self.goal} 的最新动态、行业趋势、数据报告",
                f"分析 {self.goal} 的用户画像、竞争格局、机会点",
            ]
            results = []
            for q in queries:
                logger.info(f"研究查询: {q}")
                r = self.research_tool._run(q)
                results.append(r)
            self.state["research_data"] = results
            return results

        @listen(research_phase)
        def analysis_phase(self, research_data: List[str]) -> Dict[str, Any]:
            """分析阶段：对研究数据进行分析"""
            logger.info("=== 分析阶段开始 ===")
            prompt = f"""基于以下研究数据，对「{self.goal}」进行深度分析：

研究数据：
{''.join(research_data[:3])}

请分析：
1. 市场规模与增长趋势
2. 主要竞争者及市场份额
3. 用户画像与行为特征
4. 商业模式与盈利途径
5. 机会点与风险点
"""
            analysis = self.analysis_tool._run(prompt)
            self.state["analysis_data"] = {"raw": analysis, "source_count": len(research_data)}
            return self.state["analysis_data"]

        @listen(analysis_phase)
        def write_phase(self, analysis_data: Dict[str, Any]) -> str:
            """写作阶段：撰写报告"""
            logger.info("=== 写作阶段开始 ===")
            prompt = f"""基于以下研究和分析，撰写一份完整的报告：

主题：{self.goal}

分析内容：
{analysis_data.get('raw', '')[:3000]}

要求：
- 结构清晰：摘要、背景、分析、结论、建议
- 数据支撑充分
- 3000字以上
- 专业且有洞察
"""
            draft = self.writer_tool._run(prompt)
            self.state["draft"] = draft
            return draft

        @listen(write_phase)
        def finalize_phase(self, draft: str) -> str:
            """最终阶段：润色和格式化"""
            logger.info("=== 最终阶段开始 ===")
            prompt = f"""润色以下报告，使其更加精炼、有逻辑、有说服力：

{draft[:5000]}

输出格式：
1. 标题（吸引眼球）
2. 摘要（200字）
3. 正文（分章节）
4. 结论与建议
5. 参考资料（如有）
"""
            final = self.writer_tool._run(prompt)
            self.state["final_report"] = final
            return final


# ─── Fallback Pipeline（CrewAI 不可用时）────────────────────────────────────

class FallbackPipeline:
    """
    CrewAI 不可用时的 fallback。
    直接调用 OpenClaw agent 按顺序执行各个阶段。
    """

    def __init__(self, goal: str, roles: Optional[List[str]] = None, timeout: int = 300):
        self.goal = goal
        self.roles = roles or ["Researcher", "Analyst", "Writer"]
        self.timeout = timeout
        self.research_data: List[str] = []
        self.analysis_data: Dict[str, Any] = {}
        self.draft = ""
        self.final_report = ""

    def run(self) -> Dict[str, Any]:
        tool = OpenClawAgentTool(agent_id="main", thinking="high", timeout=self.timeout)
        logger.info(f"=== Fallback Pipeline 开始（goal: {self.goal}）===")

        # 研究
        logger.info("研究阶段...")
        queries = [
            f"全面调研 {self.goal} 的市场概况、主要玩家、最新数据",
            f"深入分析 {self.goal} 的竞争格局、用户画像、趋势",
        ]
        for q in queries:
            r = tool._run(q)
            self.research_data.append(r)

        # 分析
        logger.info("分析阶段...")
        analysis_prompt = f"""分析以下关于「{self.goal}」的研究材料，输出：
1. 市场规模与趋势
2. 竞争格局
3. 机会与风险
4. 建议

材料：
{''.join(self.research_data[:2])[:3000]}
"""
        self.analysis_data["raw"] = tool._run(analysis_prompt)
        self.analysis_data["source_count"] = len(self.research_data)

        # 写作
        logger.info("写作阶段...")
        write_prompt = f"""基于以下分析，撰写「{self.goal}」完整报告：
{self.analysis_data['raw'][:3000]}
"""
        self.draft = tool._run(write_prompt)
        self.final_report = self.draft

        logger.info("=== Fallback Pipeline 完成 ===")
        return {
            "research_data": self.research_data,
            "analysis_data": self.analysis_data,
            "draft": self.draft,
            "final_report": self.final_report,
        }


# ─── Pipeline 工厂 ────────────────────────────────────────────────────────────

class CrewAIPipeline:
    """
    CrewAI Pipeline 统一入口。
    自动检测 CrewAI 是否可用，选择 CrewAI Flow 或 Fallback Pipeline。
    """

    def __init__(self, goal: str, roles: Optional[List[str]] = None, timeout: int = 300):
        self.goal = goal
        self.roles = roles or ["Researcher", "Analyst", "Writer"]
        self.timeout = timeout

    def run(self) -> Dict[str, Any]:
        if _lazy_import_crewai():
            logger.info("使用 CrewAI Flow 执行")
            flow = ReportFlow(goal=self.goal, tool_timeout=self.timeout)
            flow.kickoff(inputs={"goal": self.goal})
            return {
                "research_data": flow.state.get("research_data", []),
                "analysis_data": flow.state.get("analysis_data", {}),
                "draft": flow.state.get("draft", ""),
                "final_report": flow.state.get("final_report", ""),
            }
        else:
            logger.info("CrewAI 不可用，使用 Fallback Pipeline")
            pipeline = FallbackPipeline(goal=self.goal, roles=self.roles, timeout=self.timeout)
            return pipeline.run()

    def run_research(self) -> List[str]:
        """单独运行研究阶段"""
        if _lazy_import_crewai():
            flow = ReportFlow(goal=self.goal, tool_timeout=self.timeout)
            return flow.research_phase()
        else:
            tool = OpenClawAgentTool(agent_id="main", thinking="high", timeout=self.timeout)
            q = f"全面调研 {self.goal} 的市场概况、主要玩家、最新数据"
            return [tool._run(q)]

    def run_analysis(self, research_data: List[str]) -> Dict[str, Any]:
        """单独运行分析阶段"""
        if _lazy_import_crewai():
            flow = ReportFlow(goal=self.goal, tool_timeout=self.timeout)
            return flow.analysis_phase(research_data)
        else:
            tool = OpenClawAgentTool(agent_id="thinker", thinking="high", timeout=self.timeout)
            prompt = f"分析以下材料：{''.join(research_data[:2])[:3000]}"
            return {"raw": tool._run(prompt), "source_count": len(research_data)}

    def run_write(self, analysis_data: Dict[str, Any]) -> str:
        """单独运行写作阶段"""
        if _lazy_import_crewai():
            flow = ReportFlow(goal=self.goal, tool_timeout=self.timeout)
            return flow.write_phase(analysis_data)
        else:
            tool = OpenClawAgentTool(agent_id="writer", thinking="medium", timeout=self.timeout)
            prompt = f"基于分析撰写报告：{analysis_data.get('raw', '')[:3000]}"
            return tool._run(prompt)


# ─── CLI 入口 ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python crewai_pipeline.py <任务目标>")
        sys.exit(1)
    goal = sys.argv[1]
    pipeline = CrewAIPipeline(goal=goal)
    result = pipeline.run()
    print(f"\n=== 最终报告 ===\n{result['final_report'][:1000]}")
