#!/usr/bin/env python3
"""
Report Swarm — 统一任务编排入口
Usage:
    python3 run.py "做一份抖音市场分析报告"
    python3 run.py "做一份抖音市场分析报告" --mode crewai
    python3 run.py "做一份抖音市场分析报告" --mode clawteam
    python3 run.py "做一份抖音市场分析报告" --mode crewai+clawteam
    python3 run.py "做一份抖音市场分析报告" --subtasks 5
    python3 run.py "做一份抖音市场分析报告" --json
    python3 run.py --decide "做一份抖音市场分析报告"  # 只输出决策，不执行
"""

import sys
import os
import json
import time
import argparse
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("report-swarm")

SCRIPT_DIR = Path(__file__).parent
OPENCLAW_BASE = Path.home() / ".openclaw"

sys.path.insert(0, str(SCRIPT_DIR))

from orchestrator import (
    SwarmOrchestrator,
    ExecutionMode,
    Complexity,
    decide_and_explain,
    plan_to_markdown,
)
from memory_store import MemoryStore
from task_manager import TaskManager, Task, TaskState

HAS_CREWAI = None   # None = not yet checked
HAS_CLAWTEAM = None

def check_crewai() -> bool:
    """通过检查包目录来判断 CrewAI 是否可用（避免触发 import 副作用）"""
    global HAS_CREWAI
    if HAS_CREWAI is None:
        try:
            import importlib.util
            spec = importlib.util.find_spec("crewai")
            HAS_CREWAI = spec is not None
        except Exception:
            HAS_CREWAI = False
    return HAS_CREWAI

def check_clawteam() -> bool:
    """通过检查源码目录来判断 ClawTeam 是否可用"""
    global HAS_CLAWTEAM
    if HAS_CLAWTEAM is None:
        clawteam_dir = OPENCLAW_BASE / "clawteam" / "clawteam"
        HAS_CLAWTEAM = clawteam_dir.exists() and (clawteam_dir / "__init__.py").exists()
    return HAS_CLAWTEAM


# ─── Pipeline 执行器 ─────────────────────────────────────────────────────────

class DirectPipeline:
    """直接执行：简单任务"""

    def __init__(self, goal: str, timeout: int = 300):
        self.goal = goal
        self.timeout = timeout

    def run(self) -> Dict[str, Any]:
        import subprocess
        logger.info(f"直接执行: {self.goal}")
        try:
            result = subprocess.run(
                ["openclaw", "agent", "-m", self.goal, "--thinking", "medium"],
                cwd=str(OPENCLAW_BASE),
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            output = result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
        except subprocess.TimeoutExpired:
            output = f"Error: Task timed out after {self.timeout}s"
        except FileNotFoundError:
            output = "Error: openclaw CLI not found"
        except Exception as e:
            output = f"Error: {str(e)}"

        return {
            "mode": "direct",
            "output": output,
            "final_report": output,
        }


def run_pipeline(
    mode: ExecutionMode,
    goal: str,
    subtasks: list,
    crewai_roles: list,
    clawteam_workers: list,
    store: MemoryStore,
    task_mgr: TaskManager,
    json_output: bool = False,
) -> Dict[str, Any]:
    """根据执行模式路由到对应的 pipeline"""

    # 保存任务到 TaskManager
    for i, st_name in enumerate(subtasks):
        task = Task(
            task_id=f"task-{i+1}",
            name=st_name,
            pipeline=mode.value,
            owner=clawteam_workers[i] if clawteam_workers and i < len(clawteam_workers) else crewai_roles[i] if crewai_roles and i < len(crewai_roles) else "",
            description=f"子任务: {st_name}",
        )
        task_mgr.create_task(task)

    results: Dict[str, Any] = {}

    if mode == ExecutionMode.DIRECT:
        logger.info("Pipeline: Direct")
        pipeline = DirectPipeline(goal=goal)
        results = pipeline.run()

    elif mode == ExecutionMode.CREWAI:
        logger.info("Pipeline: CrewAI")
        results = _run_crewai(goal, subtasks, crewai_roles, store)

    elif mode == ExecutionMode.CLAWTEAM:
        logger.info("Pipeline: ClawTeam")
        results = _run_clawteam(goal, subtasks, clawteam_workers, store, task_mgr)

    elif mode == ExecutionMode.CREWAI_CLAWTEAM:
        logger.info("Pipeline: CrewAI + ClawTeam")
        results = _run_crewai_clawteam(goal, subtasks, crewai_roles, clawteam_workers, store, task_mgr)

    return results


def _run_crewai(goal: str, subtasks: list, roles: list, store: MemoryStore) -> Dict[str, Any]:
    """CrewAI Pipeline"""
    try:
        from crewai_pipeline import CrewAIPipeline
        pipeline = CrewAIPipeline(goal=goal, roles=roles)
        result = pipeline.run()

        # 存入 cortex-memory
        for rd in result.get("research_data", []):
            store.store_to_cortex(rd, category="report-swarm-research", scope="task")
        store.store_to_cortex(
            result.get("final_report", ""),
            category="report-swarm",
            scope="task",
            metadata={"type": "final_report"},
        )

        # 保存结构化输出
        store.save_structured("research", "data.json", {
            "items": result.get("research_data", []),
        })
        store.save_structured("analysis", "insights.json", result.get("analysis_data", {}))
        report_path = store.save_report(result.get("final_report", ""))

        return {
            "mode": "crewai",
            "research_data": result.get("research_data", []),
            "analysis_data": result.get("analysis_data", {}),
            "final_report": result.get("final_report", ""),
            "report_path": str(report_path),
        }
    except Exception as e:
        logger.error(f"CrewAI Pipeline 失败: {e}")
        return {"mode": "crewai", "error": str(e)}


def _run_clawteam(
    goal: str,
    subtasks: list,
    workers: list,
    store: MemoryStore,
    task_mgr: TaskManager,
) -> Dict[str, Any]:
    """ClawTeam Pipeline"""
    try:
        from clawteam_pipeline import ClawTeamPipeline
        team_name = f"swarm-{int(time.time())}"
        pipeline = ClawTeamPipeline(goal=goal, team_name=team_name, subtasks=subtasks)
        result = pipeline.run()

        # 存入 cortex-memory
        store.store_to_cortex(
            result.get("report", ""),
            category="report-swarm",
            scope="task",
            metadata={"type": "final_report", "pipeline": "clawteam", "team": team_name},
        )

        # 保存结构化输出
        store.save_structured("clawteam", "results.json", {
            "team": team_name,
            "results": result.get("results", {}),
        })
        report_path = store.save_report(result.get("report", ""))

        return {
            "mode": "clawteam",
            "team_name": team_name,
            "results": result.get("results", {}),
            "final_report": result.get("report", ""),
            "report_path": str(report_path),
        }
    except Exception as e:
        logger.error(f"ClawTeam Pipeline 失败: {e}")
        return {"mode": "clawteam", "error": str(e)}


def _run_crewai_clawteam(
    goal: str,
    subtasks: list,
    crewai_roles: list,
    clawteam_workers: list,
    store: MemoryStore,
    task_mgr: TaskManager,
) -> Dict[str, Any]:
    """CrewAI + ClawTeam 联合 Pipeline"""
    try:
        from clawteam_pipeline import CrewAIClawTeamPipeline
        pipeline = CrewAIClawTeamPipeline(goal=goal, subtasks=subtasks)
        result = pipeline.run()

        # 汇总两个 pipeline 的结果
        ct_report = result.get("clawteam", {}).get("report", "")
        crewai_report = result.get("crewai", {}).get("final_report", "")

        # 优先用 CrewAI 整合的结果
        final = crewai_report if crewai_report else ct_report

        # 存入 cortex-memory
        store.store_to_cortex(
            final,
            category="report-swarm",
            scope="task",
            metadata={"type": "final_report", "pipeline": "crewai+clawteam"},
        )

        # 保存
        store.save_structured("crewai", "integration.json", result.get("crewai", {}))
        store.save_structured("clawteam", "results.json", result.get("clawteam", {}))
        report_path = store.save_report(final)

        return {
            "mode": "crewai+clawteam",
            "clawteam_results": result.get("clawteam", {}),
            "crewai_integration": result.get("crewai", {}),
            "final_report": final,
            "report_path": str(report_path),
        }
    except Exception as e:
        logger.error(f"联合 Pipeline 失败: {e}")
        return {"mode": "crewai+clawteam", "error": str(e)}


# ─── 主函数 ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Report Swarm — 统一任务编排入口")
    parser.add_argument("goal", nargs="?", help="任务目标")
    parser.add_argument("--mode", choices=["direct", "crewai", "clawteam", "crewai+clawteam", "auto"],
                        default="auto", help="执行模式（默认自动判断）")
    parser.add_argument("--subtasks", type=int, default=None, help="子任务数量")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    parser.add_argument("--decide", action="store_true", help="只输出执行决策，不执行")
    parser.add_argument("--timeout", type=int, default=300, help="超时时间（秒）")
    parser.add_argument("--run-id", default=None, help="指定 run ID（用于追踪）")
    args = parser.parse_args()

    # 读取 goal（支持 stdin）
    if not args.goal and not sys.stdin.isatty():
        args.goal = sys.stdin.read().strip()

    if not args.goal:
        print("用法: python3 run.py \"任务目标\" [--mode crewai|clawteam|crewai+clawteam] [--subtasks N] [--json] [--decide]")
        sys.exit(1)

    # 如果用户指定了 mode，在输入里追加（用于 orchestrator 识别）
    raw_input = args.goal
    if args.mode != "auto":
        raw_input = f"{args.goal} --mode {args.mode}"
    if args.subtasks:
        raw_input = f"{raw_input} {args.subtasks}个子任务"

    # 决策
    orchestrator = SwarmOrchestrator()
    plan = orchestrator.plan(raw_input)

    # 如果用户指定了 mode，覆盖决策
    if args.mode != "auto":
        plan.mode = ExecutionMode(args.mode)

    if args.subtasks:
        plan.subtasks = [f"子任务 {i+1}" for i in range(args.subtasks)]

    # 初始化存储和任务管理器
    store = MemoryStore(run_id=args.run_id)
    task_mgr = TaskManager(run_id=store.run_id)

    # 保存 manifest
    manifest_path = store.save_manifest(
        mode=plan.mode.value,
        complexity=plan.complexity.value,
        subtasks=plan.subtasks,
        task_states={},
        duration_seconds=0,
    )

    # ─── Decide 模式（只输出决策）────────────────────────────────────────
    if args.decide:
        if args.json:
            print(json.dumps({
                "goal": plan.subtasks,
                "mode": plan.mode.value,
                "complexity": plan.complexity.value,
                "crewai_roles": plan.crewai_roles,
                "clawteam_workers": plan.clawteam_workers,
            }, ensure_ascii=False, indent=2))
        else:
            print(f"任务目标: {orchestrator.parser.parse(args.goal).task_goal}")
            print(plan_to_markdown(plan))
        return

    # ─── 执行 ─────────────────────────────────────────────────────────────
    start_time = time.time()

    if args.json:
        print(json.dumps({
            "status": "started",
            "goal": args.goal,
            "plan": {
                "mode": plan.mode.value,
                "complexity": plan.complexity.value,
                "subtasks": plan.subtasks,
                "crewai_roles": plan.crewai_roles,
                "clawteam_workers": plan.clawteam_workers,
            },
            "run_id": store.run_id,
            "manifest": str(manifest_path),
        }, ensure_ascii=False, indent=2))

    # 执行 pipeline
    results = run_pipeline(
        mode=plan.mode,
        goal=orchestrator.parser.parse(args.goal).task_goal,
        subtasks=plan.subtasks,
        crewai_roles=plan.crewai_roles,
        clawteam_workers=plan.clawteam_workers,
        store=store,
        task_mgr=task_mgr,
        json_output=args.json,
    )

    duration = time.time() - start_time

    # 更新 manifest
    task_states = {t.task_id: t.state.value for t in task_mgr.list_tasks()}
    store.update_manifest({
        "duration_seconds": round(duration, 1),
        "task_states": task_states,
        "results_summary": {
            "has_report": bool(results.get("final_report")),
            "report_path": results.get("report_path", ""),
            "error": results.get("error", ""),
        },
    })

    # 输出结果
    if args.json:
        print(json.dumps({
            "status": "completed",
            "run_id": store.run_id,
            "mode": plan.mode.value,
            "duration_seconds": round(duration, 1),
            "results": results,
            "output_dir": str(store.run_path),
            "manifest": str(manifest_path),
        }, ensure_ascii=False, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"✅ Report Swarm 完成")
        print(f"模式: {plan.mode.value} | 耗时: {duration:.1f}s")
        print(f"输出目录: {store.run_path}")
        print(f"{'='*60}\n")
        if results.get("final_report"):
            preview = results["final_report"][:800]
            print(f"报告预览：\n{preview}...")
        elif results.get("error"):
            print(f"错误: {results['error']}")
        else:
            print("执行完成，请查看输出目录获取详细结果。")


if __name__ == "__main__":
    main()
