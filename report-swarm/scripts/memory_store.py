"""
Report Swarm — 跨 Pipeline 结果共享存储
CrewAI pipeline 和 ClawTeam pipeline 共用此存储交换中间结果
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

OPENCLAW_BASE = Path.home() / ".openclaw"
CORTEX_BASE = OPENCLAW_BASE / "workspace" / "plugins" / "cortex-memory"
REPORT_SWARM_BASE = OPENCLAW_BASE / "workspace" / "data" / "report-swarm"
OUTPUT_BASE = REPORT_SWARM_BASE / "outputs"


class MemoryStore:
    """统一存储：Cortex Memory（共享）+ 本地文件（结构化输出）"""

    def __init__(self, run_id: Optional[str] = None):
        self.run_id = run_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_dir = OUTPUT_BASE / self.run_id
        self.run_dir.mkdir(parents=True, exist_ok=True)
        CORTEX_BASE.mkdir(parents=True, exist_ok=True)

    # ─── 文件存储（结构化输出）───────────────────────────────────────────────

    def save_structured(self, phase: str, filename: str, data: Dict[str, Any]) -> Path:
        """保存结构化数据到 run 目录"""
        phase_dir = self.run_dir / phase
        phase_dir.mkdir(parents=True, exist_ok=True)
        path = phase_dir / filename
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"保存结构化数据: {path}")
        return path

    def save_text(self, phase: str, filename: str, content: str) -> Path:
        """保存文本内容到 run 目录"""
        phase_dir = self.run_dir / phase
        phase_dir.mkdir(parents=True, exist_ok=True)
        path = phase_dir / filename
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"保存文本: {path}")
        return path

    def save_report(self, content: str, filename: str = "report.md") -> Path:
        """保存最终报告"""
        path = self.run_dir / filename
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"保存报告: {path}")
        return path

    def save_artifacts(self, phase: str, artifacts: List[Dict[str, Any]]) -> Path:
        """保存附件（图片、JSON 数据等）"""
        return self.save_structured(phase, "artifacts.json", {"artifacts": artifacts})

    # ─── Cortex Memory（跨 Pipeline 共享）─────────────────────────────────

    def store_to_cortex(
        self,
        text: str,
        category: str = "report-swarm",
        scope: str = "task",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """写入 OpenClaw cortex-memory"""
        try:
            cortex_script = CORTEX_BASE / "src" / "index.ts"
            if not cortex_script.exists():
                logger.warning(f"Cortex script not found: {cortex_script}")
                return self._fallback_cortex(text, category, scope, metadata)
            import subprocess
            cmd = [
                "node",
                str(cortex_script),
                "store",
                "--text", text,
                "--category", category,
                "--scope", scope,
            ]
            if metadata:
                cmd.extend(["--metadata", json.dumps(metadata)])
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                logger.info(f"Cortex 存储成功（{len(text)} chars）")
                return True
            else:
                logger.warning(f"Cortex 存储失败: {result.stderr}，使用 fallback")
                return self._fallback_cortex(text, category, scope, metadata)
        except Exception as e:
            logger.warning(f"Cortex 存储异常: {e}，使用 fallback")
            return self._fallback_cortex(text, category, scope, metadata)

    def _fallback_cortex(
        self,
        text: str,
        category: str,
        scope: str,
        metadata: Optional[Dict[str, Any]],
    ) -> bool:
        """Fallback：直接写入 cortex-memory 的 JSONL 文件"""
        try:
            cortex_data = CORTEX_BASE / "data"
            cortex_data.mkdir(parents=True, exist_ok=True)
            log_file = cortex_data / f"{category}.jsonl"
            entry = {
                "timestamp": datetime.now().isoformat(),
                "scope": scope,
                "text": text,
                "metadata": metadata or {},
            }
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            logger.info(f"Cortex fallback 写入: {log_file}")
            return True
        except Exception as e:
            logger.error(f"Cortex fallback 也失败: {e}")
            return False

    def read_from_cortex(self, query: str, limit: int = 5) -> List[str]:
        """从 cortex-memory 读取相关内容"""
        try:
            import subprocess
            cmd = ["node", str(CORTEX_BASE / "src" / "index.ts"), "search", "--query", query]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return [line for line in result.stdout.strip().split("\n") if line]
            return []
        except Exception as e:
            logger.warning(f"Cortex 读取失败: {e}")
            return self._fallback_cortex_search(query, limit)

    def _fallback_cortex_search(self, query: str, limit: int) -> List[str]:
        """Fallback 搜索：遍历 JSONL 文件"""
        results = []
        cortex_data = CORTEX_BASE / "data"
        if not cortex_data.exists():
            return []
        keywords = query.lower().split()
        for log_file in cortex_data.glob("*.jsonl"):
            try:
                with open(log_file, encoding="utf-8") as f:
                    for line in f:
                        entry = json.loads(line)
                        text = entry.get("text", "").lower()
                        if any(kw in text for kw in keywords):
                            results.append(text[:200])
                            if len(results) >= limit:
                                return results
            except Exception:
                continue
        return results

    # ─── Manifest 管理 ────────────────────────────────────────────────────

    def save_manifest(
        self,
        mode: str,
        complexity: str,
        subtasks: List[str],
        task_states: Dict[str, str],
        duration_seconds: float,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Path:
        """保存执行 manifest"""
        manifest = {
            "run_id": self.run_id,
            "timestamp": datetime.now().isoformat(),
            "mode": mode,
            "complexity": complexity,
            "subtasks": subtasks,
            "task_states": task_states,
            "duration_seconds": round(duration_seconds, 1),
            "output_dir": str(self.run_dir),
            **(extra or {}),
        }
        path = self.save_structured("", "manifest.json", manifest)
        logger.info(f"Manifest 保存: {path}")
        return path

    def update_manifest(self, updates: Dict[str, Any]) -> None:
        """更新 manifest 中的部分字段"""
        manifest_path = self.run_dir / "manifest.json"
        if manifest_path.exists():
            with open(manifest_path, encoding="utf-8") as f:
                manifest = json.load(f)
        else:
            manifest = {}
        manifest.update(updates)
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

    # ─── 工具方法 ─────────────────────────────────────────────────────────

    @property
    def run_path(self) -> Path:
        return self.run_dir

    def list_runs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """列出最近的执行记录"""
        runs = []
        if not OUTPUT_BASE.exists():
            return []
        for run_dir in sorted(OUTPUT_BASE.iterdir(), reverse=True)[:limit]:
            manifest_path = run_dir / "manifest.json"
            if manifest_path.exists():
                with open(manifest_path, encoding="utf-8") as f:
                    runs.append(json.load(f))
        return runs
