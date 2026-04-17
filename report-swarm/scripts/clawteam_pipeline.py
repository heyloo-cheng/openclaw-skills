"""
Report Swarm — ClawTeam Pipeline
封装 ClawTeam 多 agent 协作：spawn team、spawn workers、task board、inbox 通信
ClawTeam 已在 ~/.openclaw/clawteam/（直接 import）
"""

import sys
import os
import time
import logging
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

OPENCLAW_BASE = Path.home() / ".openclaw"
CLAWTEAM_DIR = OPENCLAW_BASE / "clawteam"
CLAWTEAM_SRC = CLAWTEAM_DIR / "clawteam"

# 延迟导入 ClawTeam（避免顶层加载时触发副作用）
HAS_CLAWTEAM = None


def _lazy_import_clawteam():
    """延迟导入 ClawTeam"""
    global HAS_CLAWTEAM
    if HAS_CLAWTEAM is not None:
        return HAS_CLAWTEAM
    clawteam_init = CLAWTEAM_SRC / "__init__.py"
    if not clawteam_init.exists():
        HAS_CLAWTEAM = False
        logger.warning("ClawTeam 模块不存在，将使用 CLI fallback")
        return False
    try:
        sys.path.insert(0, str(CLAWTEAM_SRC))
        from clawteam.team.manager import TeamManager
        from clawteam.team.tasks import TaskStore
        from clawteam.team.mailbox import MailboxManager
        HAS_CLAWTEAM = True
        logger.info("ClawTeam 模块加载成功")
        return True
    except ImportError:
        HAS_CLAWTEAM = False
        logger.warning("ClawTeam 模块加载失败，将使用 CLI fallback")
        return False


# ─── ClawTeam CLI 封装 ────────────────────────────────────────────────────────

class ClawTeamCLI:
    """ClawTeam CLI 命令封装（兼容 Python import 和 subprocess 两种调用方式）"""

    def __init__(self, team_name: str, data_dir: Optional[str] = None):
        self.team_name = team_name
        self.data_dir = data_dir or str(Path.home() / ".clawteam")
        self._manager: Optional["TeamManager"] = None

    # ─── 内部 Manager（如果 Python import 成功）────────────────────────────

    def _get_manager(self) -> Optional["TeamManager"]:
        if not _lazy_import_clawteam():
            return None
        if self._manager is None:
            try:
                config_path = Path(self.data_dir) / "config.json"
                self._manager = TeamManager(config_path=config_path)
            except Exception as e:
                logger.warning(f"无法初始化 TeamManager: {e}")
        return self._manager

    # ─── Team 操作 ────────────────────────────────────────────────────────

    def spawn_team(self, description: str = "") -> bool:
        """创建团队"""
        cmd = [
            "python3", "-m", "clawteam",
            "team", "spawn-team", self.team_name,
            "-d", description or f"Report Swarm team for task",
        ]
        return self._run_cmd(cmd, success_msg=f"Team {self.team_name} created")

    def team_status(self) -> Dict[str, Any]:
        """获取团队状态"""
        cmd = ["python3", "-m", "clawteam", "--json", "team", "discover"]
        result = self._run_cmd(cmd, capture=True)
        if result:
            try:
                import json
                return json.loads(result)
            except Exception:
                return {"raw": result}
        return {}

    # ─── Worker Spawn ─────────────────────────────────────────────────────

    def spawn_worker(
        self,
        worker_name: str,
        task: str,
        backend: str = "tmux",
        command: str = "openclaw",
    ) -> bool:
        """Spawn 一个 worker agent"""
        cmd = [
            "python3", "-m", "clawteam",
            "spawn", backend, command,
            "--team", self.team_name,
            "--agent-name", worker_name,
            "--task", task,
        ]
        return self._run_cmd(cmd, success_msg=f"Worker {worker_name} spawned")

    def spawn_workers(self, workers: List[Dict[str, str]]) -> List[bool]:
        """
        批量 spawn workers。
        workers: [{"name": "researcher-1", "task": "...", "backend": "tmux", "command": "openclaw"}, ...]
        """
        results = []
        for w in workers:
            r = self.spawn_worker(
                worker_name=w["name"],
                task=w["task"],
                backend=w.get("backend", "tmux"),
                command=w.get("command", "openclaw"),
            )
            results.append(r)
        return results

    # ─── Task 操作 ────────────────────────────────────────────────────────

    def create_task(
        self,
        task_name: str,
        owner: str = "",
        blocked_by: Optional[List[str]] = None,
    ) -> Optional[str]:
        """创建任务"""
        cmd = [
            "python3", "-m", "clawteam",
            "task", "create", self.team_name, task_name,
        ]
        if owner:
            cmd.extend(["-o", owner])
        if blocked_by:
            cmd.extend(["--blocked-by", ",".join(blocked_by)])
        result = self._run_cmd(cmd, capture=True)
        if result:
            import json
            try:
                data = json.loads(result)
                return data.get("id") or data.get("task_id")
            except Exception:
                for line in result.split("\n"):
                    if "id" in line.lower() or "created" in line.lower():
                        return line.strip()
        return None

    def update_task(self, task_id: str, status: str) -> bool:
        """更新任务状态"""
        cmd = [
            "python3", "-m", "clawteam",
            "task", "update", self.team_name, task_id,
            "--status", status,
        ]
        return self._run_cmd(cmd)

    def list_tasks(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出任务"""
        cmd = ["python3", "-m", "clawteam", "--json", "task", "list", self.team_name]
        if status:
            cmd.extend(["--status", status])
        result = self._run_cmd(cmd, capture=True)
        if result:
            try:
                import json
                return json.loads(result)
            except Exception:
                return []
        return []

    def get_ready_tasks(self) -> List[Dict[str, Any]]:
        """获取可调度的任务"""
        return self.list_tasks(status="pending")

    # ─── Inbox 通信 ──────────────────────────────────────────────────────

    def send_message(self, to_agent: str, message: str) -> bool:
        """发送消息给 agent"""
        cmd = [
            "python3", "-m", "clawteam",
            "inbox", "send", self.team_name, to_agent, message,
        ]
        return self._run_cmd(cmd, success_msg=f"Message sent to {to_agent}")

    def read_inbox(self, agent: str = "leader", peek: bool = True) -> List[str]:
        """读取 inbox"""
        action = "peek" if peek else "receive"
        cmd = [
            "python3", "-m", "clawteam",
            "--json", "inbox", action, self.team_name, agent,
        ]
        result = self._run_cmd(cmd, capture=True)
        if result:
            try:
                import json
                data = json.loads(result)
                if isinstance(data, list):
                    return [m.get("message", "") or m.get("content", "") or str(m) for m in data]
                elif isinstance(data, dict):
                    return [data.get("message", "") or data.get("content", "") or str(data)]
            except Exception:
                return [line for line in result.split("\n") if line.strip()]
        return []

    def broadcast(self, message: str) -> bool:
        """广播消息给所有成员"""
        cmd = [
            "python3", "-m", "clawteam",
            "inbox", "broadcast", self.team_name, message,
        ]
        return self._run_cmd(cmd, success_msg="Broadcast sent")

    # ─── Board 监控 ───────────────────────────────────────────────────────

    def show_board(self) -> str:
        """显示看板"""
        cmd = ["python3", "-m", "clawteam", "board", "show", self.team_name]
        return self._run_cmd(cmd, capture=True) or ""

    def wait_completion(self, timeout: int = 600, poll_interval: int = 10) -> bool:
        """等待所有任务完成"""
        logger.info(f"等待任务完成（timeout={timeout}s）...")
        start = time.time()
        while True:
            if timeout > 0 and (time.time() - start) > timeout:
                logger.warning("等待超时")
                return False
            tasks = self.list_tasks()
            if not tasks:
                time.sleep(poll_interval)
                continue
            all_done = all(
                t.get("state") in ("completed", "done", "failed")
                for t in tasks
            )
            if all_done:
                logger.info("所有任务已完成")
                return True
            time.sleep(poll_interval)

    # ─── 生命周期 ────────────────────────────────────────────────────────

    def request_shutdown(self, agent: str) -> bool:
        """请求关闭 agent"""
        cmd = [
            "python3", "-m", "clawteam",
            "lifecycle", "request-shutdown", self.team_name, agent,
        ]
        return self._run_cmd(cmd)

    def cleanup_team(self) -> bool:
        """清理团队"""
        cmd = ["python3", "-m", "clawteam", "team", "cleanup", self.team_name]
        return self._run_cmd(cmd, success_msg=f"Team {self.team_name} cleaned up")

    # ─── 辅助 ────────────────────────────────────────────────────────────

    def _run_cmd(
        self,
        cmd: List[str],
        capture: bool = False,
        success_msg: str = "",
    ) -> str:
        """运行命令"""
        logger.debug(f"CMD: {' '.join(cmd)}")
        try:
            cwd = str(CLAWTEAM_DIR)
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode == 0:
                if success_msg:
                    logger.info(success_msg)
                if capture:
                    return result.stdout.strip()
                return ""
            else:
                logger.error(f"CMD failed: {result.stderr.strip()}")
                if capture:
                    return result.stderr.strip()
                return ""
        except subprocess.TimeoutExpired:
            logger.error(f"CMD timeout: {' '.join(cmd)}")
            return ""
        except FileNotFoundError:
            logger.error("python3 -m clawteam not found")
            return ""
        except Exception as e:
            logger.error(f"CMD exception: {e}")
            return ""


# ─── ClawTeam Pipeline ───────────────────────────────────────────────────────

class ClawTeamPipeline:
    """
    ClawTeam Pipeline：spawn team -> 创建任务 -> spawn workers -> 监控 -> 收集结果
    """

    def __init__(
        self,
        goal: str,
        team_name: Optional[str] = None,
        subtasks: Optional[List[str]] = None,
        data_dir: Optional[str] = None,
    ):
        self.goal = goal
        self.team_name = team_name or f"swarm-{int(time.time())}"
        self.subtasks = subtasks or ["数据收集", "数据分析", "报告撰写"]
        self.cli = ClawTeamCLI(team_name=self.team_name, data_dir=data_dir)
        self.results: Dict[str, str] = {}

    def run(self) -> Dict[str, Any]:
        """执行完整 pipeline"""
        try:
            # 1. 创建团队
            logger.info(f"创建团队: {self.team_name}")
            self.cli.spawn_team(description=f"Report Swarm: {self.goal}")

            # 2. 创建任务
            task_ids = []
            for i, st in enumerate(self.subtasks):
                owner = f"worker-{i+1}"
                tid = self.cli.create_task(task_name=st, owner=owner)
                task_ids.append(tid)
                logger.info(f"任务 {i+1}: {st} (id={tid})")

            # 3. Spawn workers
            logger.info("Spawn workers...")
            workers = [
                {
                    "name": f"worker-{i+1}",
                    "task": f"请完成子任务「{st}」。整体目标：{self.goal}",
                    "backend": "tmux",
                    "command": "openclaw",
                }
                for i, st in enumerate(self.subtasks)
            ]
            self.cli.spawn_workers(workers)

            # 4. 等待完成
            self.cli.wait_completion(timeout=600)

            # 5. 收集结果
            for i, tid in enumerate(task_ids):
                messages = self.cli.read_inbox(agent=f"worker-{i+1}", peek=True)
                self.results[f"worker-{i+1}"] = "\n".join(messages)

            # 6. 汇总报告
            report = self._compile_report()

            # 7. 清理
            self.cli.cleanup_team()

            return {
                "team_name": self.team_name,
                "subtasks": self.subtasks,
                "results": self.results,
                "report": report,
            }

        except Exception as e:
            logger.error(f"ClawTeam Pipeline 异常: {e}")
            return {
                "team_name": self.team_name,
                "error": str(e),
                "results": self.results,
                "report": self._compile_report(),
            }

    def _compile_report(self) -> str:
        """汇总所有 worker 结果为报告"""
        sections = []
        for worker, result in self.results.items():
            sections.append(f"## {worker}\n\n{result[:2000]}\n")
        return f"# {self.goal}\n\n" + "\n".join(sections)


# ─── 联合 Pipeline（CrewAI + ClawTeam）────────────────────────────────────────

class CrewAIClawTeamPipeline:
    """
    CrewAI + ClawTeam 联合 Pipeline。
    CrewAI 做编排层，ClawTeam 做执行层。
    """

    def __init__(self, goal: str, subtasks: List[str], crewai_timeout: int = 300):
        self.goal = goal
        self.subtasks = subtasks
        self.crewai_timeout = crewai_timeout
        self.crewai_pipeline: Optional[Any] = None
        self.clawteam_pipeline: Optional[ClawTeamPipeline] = None
        self.results: Dict[str, Any] = {}

    def run(self) -> Dict[str, Any]:
        """
        执行流程：
        1. CrewAI 编排层分析任务，拆分为子任务分配给 ClawTeam
        2. ClawTeam spawn workers 并行执行
        3. 汇总结果给 CrewAI writer agent
        """
        logger.info(f"=== CrewAI + ClawTeam 联合 Pipeline 开始 ===")
        logger.info(f"目标: {self.goal}")
        logger.info(f"子任务数: {len(self.subtasks)}")

        # 阶段 1：ClawTeam spawn 并行执行子任务
        logger.info("阶段 1：ClawTeam spawn workers...")
        team_name = f"swarm-crewai-{int(time.time())}"
        self.clawteam_pipeline = ClawTeamPipeline(
            goal=self.goal,
            team_name=team_name,
            subtasks=self.subtasks,
        )
        ct_result = self.clawteam_pipeline.run()
        self.results["clawteam"] = ct_result

        # 阶段 2：CrewAI writer 整合结果
        logger.info("阶段 2：CrewAI writer 整合结果...")
        crewai_result = self._crewai_integrate()
        self.results["crewai"] = crewai_result

        logger.info("=== 联合 Pipeline 完成 ===")
        return self.results

    def _crewai_integrate(self) -> Dict[str, Any]:
        """用 CrewAI writer agent 整合 ClawTeam 的结果"""
        sys.path.insert(0, str(CREWAI_DIR))
        from crewai_pipeline import CrewAIPipeline, OpenClawAgentTool

        ct_report = self.clawteam_pipeline.results if self.clawteam_pipeline else {}
        prompt = f"""整合以下 ClawTeam workers 的研究成果，撰写完整报告：

目标：{self.goal}

各 Worker 研究结果：
{self._format_ct_results(ct_report)}

要求：
- 结构清晰，分章节
- 综合各 worker 的研究成果
- 给出结论和建议
- 3000字以上
"""
        tool = OpenClawAgentTool(agent_id="writer", thinking="medium", timeout=self.crewai_timeout)
        final_report = tool._run(prompt)
        return {"final_report": final_report}

    def _format_ct_results(self, results: Dict[str, str]) -> str:
        formatted = []
        for worker, content in results.items():
            formatted.append(f"--- {worker} ---\n{content[:1000]}")
        return "\n".join(formatted)


# ─── CLI 入口 ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python clawteam_pipeline.py <任务目标>")
        sys.exit(1)
    goal = sys.argv[1]
    pipeline = ClawTeamPipeline(goal=goal, subtasks=["数据收集", "竞品分析", "报告撰写"])
    result = pipeline.run()
    print(f"\n=== 报告摘要 ===\n{result.get('report', '')[:1000]}")
