#!/usr/bin/env python3
"""skill-evolve.py — 分析 usage log，自动调参，检测异常，生成报告
由 cron 每周日 10:00 执行"""

import json
import os
import sys
from datetime import datetime, timedelta
from collections import defaultdict

DATA_DIR = os.path.expanduser("~/.openclaw/workspace/data")
LOG_PATH = os.path.join(DATA_DIR, "skill-usage-log.jsonl")
REGISTRY_PATH = os.path.join(DATA_DIR, "skill-registry.json")
HEALTH_PATH = os.path.join(DATA_DIR, "skill-health.json")
EVOLVE_LOG = os.path.join(DATA_DIR, "skill-evolve-log.jsonl")

def load_usage_log(days=30):
    """加载最近N天的usage log"""
    entries = []
    if not os.path.exists(LOG_PATH):
        return entries
    cutoff = datetime.now() - timedelta(days=days)
    with open(LOG_PATH, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                ts = datetime.fromisoformat(entry.get("timestamp", "2000-01-01"))
                if ts >= cutoff:
                    entries.append(entry)
            except:
                continue
    return entries

def analyze_skills(entries):
    """按 skill 聚合统计"""
    stats = defaultdict(lambda: {
        "total": 0, "success": 0, "failed": 0,
        "accepted": 0, "modified": 0, "rejected": 0,
        "routes": defaultdict(int),
        "agents": defaultdict(int),
        "avg_time_ms": 0, "times": [],
    })
    
    for e in entries:
        if e.get("type") == "delegation":
            continue
        sid = e.get("skill_id", "unknown")
        s = stats[sid]
        s["total"] += 1
        if e.get("success"):
            s["success"] += 1
        else:
            s["failed"] += 1
        if e.get("user_accepted"):
            s["accepted"] += 1
        if e.get("user_modified"):
            s["modified"] += 1
        if e.get("routed_to"):
            s["routes"][e["routed_to"]] += 1
        if e.get("agent"):
            s["agents"][e["agent"]] += 1
        if e.get("execution_time_ms"):
            s["times"].append(e["execution_time_ms"])
    
    # Calculate averages
    for sid, s in stats.items():
        if s["times"]:
            s["avg_time_ms"] = sum(s["times"]) / len(s["times"])
        s["success_rate"] = s["success"] / s["total"] if s["total"] > 0 else 0
        s["accept_rate"] = s["accepted"] / s["total"] if s["total"] > 0 else 0
        del s["times"]
        s["routes"] = dict(s["routes"])
        s["agents"] = dict(s["agents"])
    
    return dict(stats)

def compute_health(stats):
    """计算每个 skill 的健康分 (0-100)"""
    health = {}
    for sid, s in stats.items():
        success_score = s["success_rate"] * 40  # max 40
        usage_score = min(s["total"] / 10, 1) * 30  # max 30, saturates at 10 uses
        accept_score = s["accept_rate"] * 30  # max 30
        score = round(success_score + usage_score + accept_score, 1)
        
        status = "healthy"
        if s["success_rate"] < 0.7:
            status = "needs_optimization"
        if s["total"] >= 3 and s["success_rate"] < 0.5:
            status = "critical"
        if s["total"] == 0:
            status = "unused"
        
        health[sid] = {
            "score": score,
            "status": status,
            "total_uses": s["total"],
            "success_rate": round(s["success_rate"], 2),
            "accept_rate": round(s["accept_rate"], 2),
        }
    return health

def detect_anomalies(stats):
    """检测异常模式"""
    alerts = []
    for sid, s in stats.items():
        # 连续失败
        if s["failed"] >= 3 and s["success_rate"] < 0.5:
            alerts.append({
                "type": "consecutive_failures",
                "skill": sid,
                "message": f"{sid} 成功率仅 {s['success_rate']:.0%} ({s['failed']}/{s['total']} 失败)",
                "action": "suggest_fallback"
            })
        # 用户总是修改输出
        if s["total"] >= 5 and s["modified"] / s["total"] > 0.5:
            alerts.append({
                "type": "high_modification_rate",
                "skill": sid,
                "message": f"{sid} 输出被修改率 {s['modified']/s['total']:.0%}，prompt 可能需要优化",
                "action": "suggest_prompt_update"
            })
        # 路由偏好偏移
        if len(s["routes"]) >= 2:
            total_routed = sum(s["routes"].values())
            for route, count in s["routes"].items():
                if count / total_routed > 0.85 and total_routed >= 5:
                    alerts.append({
                        "type": "route_preference",
                        "skill": sid,
                        "message": f"{sid} 有 {count/total_routed:.0%} 路由到 {route}，考虑设为默认",
                        "action": "suggest_default_route"
                    })
    return alerts

def auto_adjust_registry(stats, alerts):
    """根据分析结果自动调整 registry"""
    if not os.path.exists(REGISTRY_PATH):
        return []
    
    with open(REGISTRY_PATH, 'r') as f:
        registry = json.load(f)
    
    adjustments = []
    registry_map = {s["id"]: s for s in registry}
    
    for sid, s in stats.items():
        if sid not in registry_map:
            continue
        skill = registry_map[sid]
        
        # 更新 use_count 和 success_rate
        old_count = skill.get("use_count", 0)
        old_rate = skill.get("success_rate")
        skill["use_count"] = s["total"]
        skill["success_rate"] = round(s["success_rate"], 2)
        skill["last_used"] = datetime.now().isoformat()
        
        if old_count != s["total"] or old_rate != skill["success_rate"]:
            adjustments.append(f"{sid}: use_count {old_count}→{s['total']}, success_rate {old_rate}→{skill['success_rate']}")
    
    with open(REGISTRY_PATH, 'w') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    return adjustments

def generate_report(stats, health, alerts, adjustments):
    """生成文本报告"""
    lines = [f"## Skill 自我进化报告 ({datetime.now().strftime('%Y-%m-%d')})\n"]
    
    total_executions = sum(s["total"] for s in stats.values())
    lines.append(f"📊 总执行次数: {total_executions}\n")
    
    # Top skills
    top = sorted(stats.items(), key=lambda x: x[1]["total"], reverse=True)[:5]
    if top:
        lines.append("🏆 最常用:")
        for i, (sid, s) in enumerate(top, 1):
            lines.append(f"  {i}. {sid} — {s['total']}次 (成功率 {s['success_rate']:.0%})")
        lines.append("")
    
    # Health alerts
    critical = [sid for sid, h in health.items() if h["status"] == "critical"]
    needs_opt = [sid for sid, h in health.items() if h["status"] == "needs_optimization"]
    if critical:
        lines.append(f"🚨 严重问题: {', '.join(critical)}")
    if needs_opt:
        lines.append(f"⚠️ 需要优化: {', '.join(needs_opt)}")
    
    # Anomaly alerts
    if alerts:
        lines.append("\n🔔 异常检测:")
        for a in alerts:
            lines.append(f"  - {a['message']}")
    
    # Adjustments
    if adjustments:
        lines.append("\n🔧 自动调整:")
        for adj in adjustments:
            lines.append(f"  - {adj}")
    
    # Unused
    unused = [sid for sid, h in health.items() if h["status"] == "unused"]
    if unused:
        lines.append(f"\n💤 未使用: {', '.join(unused)}")
    
    return "\n".join(lines)

def main():
    entries = load_usage_log(days=30)
    
    if not entries:
        print("📭 暂无 usage log 数据，跳过进化分析")
        sys.exit(0)
    
    stats = analyze_skills(entries)
    health = compute_health(stats)
    alerts = detect_anomalies(stats)
    adjustments = auto_adjust_registry(stats, alerts)
    
    # Save health scores
    with open(HEALTH_PATH, 'w') as f:
        json.dump(health, f, indent=2, ensure_ascii=False)
    
    # Log evolution run
    evolve_entry = {
        "timestamp": datetime.now().isoformat(),
        "total_entries": len(entries),
        "skills_analyzed": len(stats),
        "alerts": len(alerts),
        "adjustments": len(adjustments),
    }
    with open(EVOLVE_LOG, 'a') as f:
        f.write(json.dumps(evolve_entry, ensure_ascii=False) + "\n")
    
    # Generate report
    report = generate_report(stats, health, alerts, adjustments)
    print(report)
    
    # Save report
    report_path = os.path.join(DATA_DIR, "skill-evolve-report.md")
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"\n📁 Health: {HEALTH_PATH}")
    print(f"📁 Report: {report_path}")

if __name__ == "__main__":
    main()
