"""
Report Swarm — 任务生命周期管理器
基于 file-based 的任务状态追踪，支持 crewai 和 clawteam pipeline 共用
"""

import os
import json
import time
import logging
import fcntl
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from enum import Enum

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class TaskState(Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    BLOCKED = "blocked"


class Task:
    """单个任务"""

    def __init__(
        self,
        task_id: str,
        name: str,
        pipeline: str,  # "crewai" | "clawteam" | "direct"
        owner: str = "",
        description: str = "",
        dependencies: Optional[List[str]] = None,
    ):
        self.task_id = task_id
        self.name = name
        self.pipeline = pipeline
        self.owner = owner
        self.description = description
        self.dependencies = dependencies or []
        self.state = TaskState.PENDING
        self.result = ""
        self.error = ""
        self.started_at: Optional[str] = None
        self.completed_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "pipeline": self.pipeline,
            "owner": self.owner,
            "description": self.description,
            "dependencies": self.dependencies,
            "state": self.state.value,
            "result": self.result,
            "error": self.error,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Task":
        task = cls(
            task_id=d["task_id"],
            name=d["name"],
            pipeline=d["pipeline"],
            owner=d.get("owner", ""),
            description=d.get("description", ""),
            dependencies=d.get("dependencies", []),
        )
        task.state = TaskState(d.get("state", "pending"))
        task.result = d.get("result", "")
        task.error = d.get("error", "")
        task.started_at = d.get("started_at")
        task.completed_at = d.get("completed_at")
        return task


class TaskManager:
    """
    任务生命周期管理器。
    数据存储在 JSON 文件中，使用 fcntl 做文件锁保证并发安全。
    crewai_pipeline 和 clawteam_pipeline 共用同一个 TaskManager 实例。
    """

    LOCK_SUFFIX = ".lock"

    def __init__(self, run_id: str, store_dir: Optional[Path] = None):
        self.run_id = run_id
        from memory_store import REPORT_SWARM_BASE, OUTPUT_BASE
        self.store_dir = (store_dir or (OUTPUT_BASE / run_id))
        self.store_dir.mkdir(parents=True, exist_ok=True)
        self.tasks_file = self.store_dir / "tasks.json"
        self.lock_file = self.store_dir / "tasks.json.lock"
        if not self.tasks_file.exists():
            self._write_tasks({})

    # ─── 文件锁读写 ────────────────────────────────────────────────────────

    def _read_tasks(self) -> Dict[str, Dict[str, Any]]:
        with open(self.tasks_file, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                return json.load(f)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def _write_tasks(self, tasks: Dict[str, Dict[str, Any]]) -> None:
        with open(self.tasks_file, "w", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                json.dump(tasks, f, ensure_ascii=False, indent=2)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def _update_tasks(self, updater: Callable[[Dict[str, Dict[str, Any]]], None]) -> None:
        tasks = self._read_tasks()
        updater(tasks)
        self._write_tasks(tasks)

    # ─── 任务操作 ──────────────────────────────────────────────────────────

    def create_task(self, task: Task) -> None:
        """创建任务"""
        def updater(tasks: Dict[str, Dict[str, Any]]):
            if task.task_id in tasks:
                logger.warning(f"Task {task.task_id} 已存在，跳过创建")
                return
            tasks[task.task_id] = task.to_dict()
        self._update_tasks(updater)
        logger.info(f"创建任务: {task.task_id} [{task.name}]")

    def create_tasks(self, task_list: List[Task]) -> None:
        """批量创建任务"""
        def updater(tasks: Dict[str, Dict[str, Any]]):
            for task in task_list:
                if task.task_id not in tasks:
                    tasks[task.task_id] = task.to_dict()
        self._update_tasks(updater)
        logger.info(f"批量创建任务: {len(task_list)} 个")

    def start_task(self, task_id: str, owner: str = "") -> None:
        """标记任务为运行中"""
        def updater(tasks: Dict[str, Dict[str, Any]]):
            if task_id not in tasks:
                logger.error(f"Task {task_id} 不存在")
                return
            tasks[task_id]["state"] = TaskState.RUNNING.value
            tasks[task_id]["started_at"] = datetime.now().isoformat()
            if owner:
                tasks[task_id]["owner"] = owner
        self._update_tasks(updater)
        logger.info(f"任务开始: {task_id}")

    def complete_task(self, task_id: str, result: str = "") -> None:
        """标记任务为完成"""
        def updater(tasks: Dict[str, Dict[str, Any]]):
            if task_id not in tasks:
                return
            tasks[task_id]["state"] = TaskState.DONE.value
            tasks[task_id]["completed_at"] = datetime.now().isoformat()
            if result:
                tasks[task_id]["result"] = result
        self._update_tasks(updater)
        logger.info(f"任务完成: {task_id}")

    def fail_task(self, task_id: str, error: str = "") -> None:
        """标记任务为失败"""
        def updater(tasks: Dict[str, Dict[str, Any]]):
            if task_id not in tasks:
                return
            tasks[task_id]["state"] = TaskState.FAILED.value
            tasks[task_id]["completed_at"] = datetime.now().isoformat()
            tasks[task_id]["error"] = error
        self._update_tasks(updater)
        logger.error(f"任务失败: {task_id} — {error}")

    def update_state(self, task_id: str, state: TaskState) -> None:
        """更新任务状态"""
        def updater(tasks: Dict[str, Dict[str, Any]]):
            if task_id not in tasks:
                return
            tasks[task_id]["state"] = state.value
        self._update_tasks(updater)

    # ─── 查询 ─────────────────────────────────────────────────────────────

    def get_task(self, task_id: str) -> Optional[Task]:
        tasks = self._read_tasks()
        if task_id in tasks:
            return Task.from_dict(tasks[task_id])
        return None

    def list_tasks(self, pipeline: Optional[str] = None, state: Optional[TaskState] = None) -> List[Task]:
        tasks = self._read_tasks()
        result = []
        for t in tasks.values():
            if pipeline and t.get("pipeline") != pipeline:
                continue
            if state and TaskState(t.get("state", "pending")) != state:
                continue
            result.append(Task.from_dict(t))
        return result

    def get_ready_tasks(self) -> List[Task]:
        """获取所有可调度任务（无未完成依赖）"""
        tasks = self._read_tasks()
        ready = []
        for t in tasks.values():
            if TaskState(t.get("state", "pending")) != TaskState.PENDING:
                continue
            deps = t.get("dependencies", [])
            deps_done = all(
                tasks.get(dep, {}).get("state") == TaskState.DONE.value
                for dep in deps
            )
            if deps_done:
                ready.append(Task.from_dict(t))
        return ready

    def is_all_done(self) -> bool:
        """检查是否所有任务都完成"""
        tasks = self._read_tasks()
        return all(
            TaskState(t.get("state", "pending")) in (TaskState.DONE, TaskState.FAILED)
            for t in tasks.values()
        )

    def wait_for_completion(
        self,
        timeout: int = 600,
        poll_interval: int = 5,
        on_progress: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> bool:
        """阻塞等待所有任务完成"""
        start = time.time()
        while True:
            tasks = self._read_tasks()
            if self.is_all_done():
                return True
            if timeout > 0 and (time.time() - start) > timeout:
                logger.warning(f"等待超时（{timeout}s）")
                return False
            if on_progress:
                on_progress(tasks)
            time.sleep(poll_interval)

    # ─── 汇总 ─────────────────────────────────────────────────────────────

    def summary(self) -> Dict[str, Any]:
        """获取任务汇总"""
        tasks = self._read_tasks()
        state_counts: Dict[str, int] = {}
        for t in tasks.values():
            s = t.get("state", "pending")
            state_counts[s] = state_counts.get(s, 0) + 1
        return {
            "total": len(tasks),
            "done": state_counts.get("done", 0),
            "running": state_counts.get("running", 0),
            "pending": state_counts.get("pending", 0),
            "failed": state_counts.get("failed", 0),
            "by_pipeline": {
                p: len([t for t in tasks.values() if t.get("pipeline") == p])
                for p in set(t.get("pipeline") for t in tasks.values())
            },
        }

    def get_results(self) -> Dict[str, str]:
        """获取所有已完成任务的结果"""
        tasks = self._read_tasks()
        return {
            tid: t.get("result", "")
            for tid, t in tasks.items()
            if TaskState(t.get("state", "pending")) == TaskState.DONE and t.get("result")
        }
