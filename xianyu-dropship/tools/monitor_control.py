"""
闲鱼监控控制工具 - 注册到 OpenClaw
"""

import subprocess
import json
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw/workspace"
SCRIPTS_DIR = WORKSPACE / "scripts"
SKILL_DIR = WORKSPACE / ".agents/skills/xianyu-dropship/commands"


def run_command(command: str) -> dict:
    """运行命令"""
    try:
        result = subprocess.run(
            ["bash", SKILL_DIR / f"{command}.sh"],
            capture_output=True,
            text=True,
            timeout=60
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr if result.returncode != 0 else None
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "命令执行超时"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def start_monitoring() -> dict:
    """启动监控"""
    return run_command("start")


def stop_monitoring() -> dict:
    """停止监控"""
    return run_command("stop")


def get_status() -> dict:
    """获取状态"""
    return run_command("status")


def get_logs() -> dict:
    """获取日志"""
    return run_command("logs")


def deploy_system() -> dict:
    """部署系统"""
    return run_command("deploy")


def get_pending_products() -> dict:
    """获取待处理商品"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        
        # 获取所有待处理商品的 key
        keys = r.keys("dropship:pending:*")
        
        if not keys:
            return {
                "success": True,
                "count": 0,
                "products": [],
                "message": "暂无待处理商品"
            }
        
        products = []
        for key in keys:
            product_data = r.get(key)
            if product_data:
                product = json.loads(product_data)
                products.append(product)
        
        return {
            "success": True,
            "count": len(products),
            "products": products
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"获取待处理商品失败: {str(e)}"
        }


# 导出函数供 OpenClaw 使用
__all__ = [
    "start_monitoring",
    "stop_monitoring",
    "get_status",
    "get_logs",
    "deploy_system",
    "get_pending_products"
]
