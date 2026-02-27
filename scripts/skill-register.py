#!/usr/bin/env python3
"""skill-register.py — Scan all SKILL.md files and generate skill-registry.json
New skills without triggers will be flagged for manual trigger assignment."""

import json
import os
import re
import glob

REGISTRY_PATH = os.path.expanduser("~/.openclaw/workspace/data/skill-registry.json")
TRIGGERS_PATH = os.path.expanduser("~/.openclaw/workspace/data/skill-triggers.json")

SCAN_DIRS = [
    ("workspace", os.path.expanduser("~/.openclaw/workspace/skills")),
    ("agent", os.path.expanduser("~/.agents/skills")),
    ("builtin", "/opt/homebrew/lib/node_modules/openclaw/skills"),
    ("extension", "/opt/homebrew/lib/node_modules/openclaw/extensions"),
]

CATEGORY_PATTERNS = {
    "code": r"review|code|test|refactor|commit|pr-review|coding",
    "ops": r"deploy|incident|health|tmux",
    "content": r"doc|translation|writ|summarize|prose|blog",
    "messaging": r"feishu|discord|slack|telegram|signal|imsg|whatsapp|bluebubble|wacli",
    "media": r"camera|video|image|photo|camsnap|banana|whisper|tts|sag|voice|spotify|song",
    "productivity": r"note|reminder|things|bear|obsidian|notion|trello|github|gh-issue|1password",
    "lifestyle": r"weather|goplaces|openhue",
}

# Curated triggers for all known skills (中英文)
SKILL_TRIGGERS = {
    # Workspace skills
    "code-review-router": {
        "triggers": ["review", "code review", "审查", "代码检查", "看看代码", "diff review", "检查代码"],
        "examples": ["帮我review代码", "看看有没有bug", "审查当前改动", "review my changes"]
    },
    "commit-message-router": {
        "triggers": ["commit", "提交", "commit message", "提交信息", "git commit", "写commit"],
        "examples": ["帮我写commit message", "生成提交信息", "generate commit message"]
    },
    "test-generator-router": {
        "triggers": ["test", "测试", "生成测试", "单元测试", "unit test", "写测试", "补测试"],
        "examples": ["帮我生成测试", "补充单元测试", "generate tests for this"]
    },
    "refactor-planner": {
        "triggers": ["refactor", "重构", "优化代码", "代码质量", "code smell", "坏味道", "整理代码"],
        "examples": ["重构这个模块", "代码太乱了", "refactor this file"]
    },
    "deploy-reviewer": {
        "triggers": ["deploy", "部署", "发布检查", "dockerfile", "k8s", "CI/CD", "上线检查"],
        "examples": ["检查部署配置", "review dockerfile", "部署有没有问题"]
    },
    "incident-router": {
        "triggers": ["incident", "故障", "排查", "error", "报错", "崩溃", "crash", "debug", "排错"],
        "examples": ["服务挂了", "这个报错怎么解决", "帮我排查问题"]
    },
    "doc-generator-router": {
        "triggers": ["doc", "文档", "readme", "changelog", "API文档", "注释", "generate doc", "写文档"],
        "examples": ["生成API文档", "更新README", "帮我写文档"]
    },
    "translation-router": {
        "triggers": ["translate", "翻译", "translation", "中译英", "英译中", "本地化", "localize"],
        "examples": ["翻译这段文档", "translate to Chinese", "帮我翻译"]
    },
    "pr-reviewer-router": {
        "triggers": ["PR", "pull request", "合并请求", "PR review", "merge request", "审查PR"],
        "examples": ["review这个PR", "帮我看看PR", "PR有没有问题"]
    },
    "task-estimator": {
        "triggers": ["estimate", "估时", "评估", "工作量", "多久", "complexity", "排期", "估算"],
        "examples": ["这个需求要多久", "评估一下工作量", "estimate this task"]
    },
    "team-tasks": {
        "triggers": ["team", "团队", "任务分配", "协作", "pipeline", "多agent", "派发任务"],
        "examples": ["分配开发任务", "团队协作开发", "coordinate agents"]
    },
    # Agent skills
    "cursor-agent": {
        "triggers": ["cursor", "cursor agent", "cursor IDE", "cursor任务"],
        "examples": ["用cursor做这个", "派发cursor任务"]
    },
    # Built-in skills
    "coding-agent": {
        "triggers": ["coding", "编码", "开发", "写代码", "build", "create app", "新功能"],
        "examples": ["帮我写个功能", "开发这个feature", "build a new app"]
    },
    "gemini": {
        "triggers": ["gemini", "gemini CLI", "问gemini"],
        "examples": ["用gemini回答", "ask gemini"]
    },
    "weather": {
        "triggers": ["weather", "天气", "气温", "下雨", "forecast", "温度"],
        "examples": ["今天天气怎么样", "明天会下雨吗", "weather forecast"]
    },
    "healthcheck": {
        "triggers": ["healthcheck", "安全检查", "security audit", "系统检查", "hardening"],
        "examples": ["检查系统安全", "run healthcheck", "安全审计"]
    },
    "clawhub": {
        "triggers": ["clawhub", "skill market", "安装skill", "搜索skill", "发布skill"],
        "examples": ["搜索新skill", "install skill from clawhub"]
    },
    "tmux": {
        "triggers": ["tmux", "终端", "terminal session", "远程终端"],
        "examples": ["操作tmux", "send keys to tmux"]
    },
    "video-frames": {
        "triggers": ["video", "视频", "frame", "截帧", "ffmpeg", "视频截图"],
        "examples": ["从视频截帧", "extract frames from video"]
    },
    "skill-creator": {
        "triggers": ["create skill", "新建skill", "skill模板", "打包skill"],
        "examples": ["创建一个新skill", "帮我做个skill"]
    },
    "github": {
        "triggers": ["github", "repo", "仓库", "clone", "fork"],
        "examples": ["查看github仓库", "github操作"]
    },
    "gh-issues": {
        "triggers": ["issue", "issues", "bug report", "提issue"],
        "examples": ["查看issues", "创建issue"]
    },
    "nano-pdf": {
        "triggers": ["pdf", "PDF", "读PDF", "解析PDF"],
        "examples": ["读取这个PDF", "parse this PDF"]
    },
    "himalaya": {
        "triggers": ["email", "邮件", "收件箱", "inbox", "发邮件"],
        "examples": ["查看邮件", "check inbox", "send email"]
    },
    "apple-notes": {
        "triggers": ["apple notes", "备忘录", "笔记"],
        "examples": ["查看备忘录", "create a note"]
    },
    "apple-reminders": {
        "triggers": ["reminder", "提醒", "提醒事项", "todo"],
        "examples": ["设置提醒", "add reminder"]
    },
    "bear-notes": {
        "triggers": ["bear", "bear笔记"],
        "examples": ["查看bear笔记"]
    },
    "obsidian": {
        "triggers": ["obsidian", "obsidian笔记", "vault"],
        "examples": ["查看obsidian笔记"]
    },
    "notion": {
        "triggers": ["notion", "notion页面"],
        "examples": ["查看notion", "create notion page"]
    },
    "trello": {
        "triggers": ["trello", "看板", "board", "card"],
        "examples": ["查看trello看板"]
    },
    "things-mac": {
        "triggers": ["things", "things3", "待办"],
        "examples": ["查看待办事项"]
    },
    "1password": {
        "triggers": ["1password", "密码", "password", "credential"],
        "examples": ["查找密码", "look up password"]
    },
    "discord": {
        "triggers": ["discord", "discord消息"],
        "examples": ["发discord消息"]
    },
    "slack": {
        "triggers": ["slack", "slack消息"],
        "examples": ["发slack消息"]
    },
    "spotify-player": {
        "triggers": ["spotify", "音乐", "播放", "play music"],
        "examples": ["播放音乐", "play on spotify"]
    },
    "openai-image-gen": {
        "triggers": ["生成图片", "image gen", "画图", "DALL-E", "生成图像"],
        "examples": ["帮我画一张图", "generate an image"]
    },
    "openai-whisper": {
        "triggers": ["whisper", "语音转文字", "transcribe", "转录"],
        "examples": ["转录这段音频", "transcribe audio"]
    },
    "openai-whisper-api": {
        "triggers": ["whisper api", "语音识别API"],
        "examples": ["用whisper API转录"]
    },
    "sag": {
        "triggers": ["tts", "语音合成", "朗读", "text to speech", "说话"],
        "examples": ["朗读这段文字", "convert to speech"]
    },
    "sherpa-onnx-tts": {
        "triggers": ["sherpa", "离线tts", "本地语音"],
        "examples": ["用本地TTS朗读"]
    },
    "voice-call": {
        "triggers": ["voice call", "语音通话", "打电话"],
        "examples": ["发起语音通话"]
    },
    "camsnap": {
        "triggers": ["camera", "拍照", "摄像头", "snap"],
        "examples": ["拍张照片", "take a photo"]
    },
    "canvas": {
        "triggers": ["canvas", "画布", "可视化"],
        "examples": ["展示canvas"]
    },
    "summarize": {
        "triggers": ["summarize", "总结", "摘要", "概括"],
        "examples": ["总结这篇文章", "summarize this"]
    },
    "blogwatcher": {
        "triggers": ["blog", "博客", "RSS", "订阅"],
        "examples": ["检查博客更新"]
    },
    "model-usage": {
        "triggers": ["model usage", "token用量", "费用", "cost"],
        "examples": ["查看token用量", "check model usage"]
    },
    "session-logs": {
        "triggers": ["session log", "会话日志", "历史记录"],
        "examples": ["查看会话日志"]
    },
    "oracle": {
        "triggers": ["oracle", "预测", "决策"],
        "examples": ["帮我做决策"]
    },
    "xurl": {
        "triggers": ["url", "链接", "网页", "fetch url"],
        "examples": ["抓取这个网页"]
    },
    "gifgrep": {
        "triggers": ["gif", "表情包", "动图"],
        "examples": ["找个gif", "search gif"]
    },
    "imsg": {
        "triggers": ["imessage", "短信", "iMessage"],
        "examples": ["发iMessage"]
    },
    "bluebubbles": {
        "triggers": ["bluebubbles", "imessage server"],
        "examples": ["通过bluebubbles发消息"]
    },
    "blucli": {
        "triggers": ["bluetooth", "蓝牙"],
        "examples": ["蓝牙操作"]
    },
    "sonoscli": {
        "triggers": ["sonos", "音箱", "speaker"],
        "examples": ["控制sonos音箱"]
    },
    "openhue": {
        "triggers": ["hue", "灯光", "智能灯", "philips hue"],
        "examples": ["开灯", "调灯光"]
    },
    "goplaces": {
        "triggers": ["places", "地点", "附近", "搜索地点"],
        "examples": ["附近有什么餐厅"]
    },
    "ordercli": {
        "triggers": ["order", "订单", "外卖"],
        "examples": ["查看订单"]
    },
    "peekaboo": {
        "triggers": ["peekaboo", "窗口", "screenshot", "截屏"],
        "examples": ["截个屏"]
    },
    "mcporter": {
        "triggers": ["mcp", "MCP server", "model context"],
        "examples": ["管理MCP server"]
    },
    "gog": {
        "triggers": ["gog", "游戏"],
        "examples": ["GOG游戏"]
    },
    "eightctl": {
        "triggers": ["8sleep", "睡眠", "bed"],
        "examples": ["调节床温"]
    },
    "songsee": {
        "triggers": ["song", "歌曲识别", "听歌识曲"],
        "examples": ["这是什么歌"]
    },
    "wacli": {
        "triggers": ["whatsapp", "WA"],
        "examples": ["发whatsapp消息"]
    },
    "nano-banana-pro": {
        "triggers": ["banana", "图像生成", "AI画图"],
        "examples": ["用banana生成图片"]
    },
    # Extension skills
    "feishu-doc": {
        "triggers": ["feishu doc", "飞书文档", "云文档", "docx"],
        "examples": ["读取飞书文档", "写飞书文档"]
    },
    "feishu-wiki": {
        "triggers": ["feishu wiki", "飞书知识库", "wiki", "知识库"],
        "examples": ["查看知识库", "搜索wiki"]
    },
    "feishu-drive": {
        "triggers": ["feishu drive", "飞书云盘", "云空间", "cloud drive"],
        "examples": ["查看云盘文件"]
    },
    "feishu-perm": {
        "triggers": ["feishu perm", "飞书权限", "分享", "协作者"],
        "examples": ["设置文档权限"]
    },
    "prose": {
        "triggers": ["prose", "写作", "润色", "改写"],
        "examples": ["润色这段文字", "rewrite this"]
    },
    "lobster": {
        "triggers": ["lobster", "lobste.rs", "tech news"],
        "examples": ["查看lobster新闻"]
    },
    "acp-router": {
        "triggers": ["acp", "agent protocol", "coding session"],
        "examples": ["启动ACP session"]
    },
    # Skill Intelligence System
    "skill-router": {
        "triggers": ["skill", "找skill", "哪个skill", "what skill", "help me find", "推荐", "recommend"],
        "examples": ["帮我找skill", "哪个skill能用", "recommend a skill"]
    },
    "skill-recipes": {
        "triggers": ["recipe", "workflow", "发版", "release", "新功能", "new feature", "修bug", "bugfix", "重构", "refactor", "流程", "pipeline"],
        "examples": ["发版流程", "新功能开发流程", "修bug流程"]
    },
    "skill-sandbox": {
        "triggers": ["skill test", "测试skill", "validate skill", "dry run", "沙盒测试", "skill验证", "验证skill"],
        "examples": ["测试这个skill", "验证新skill", "dry run skill"]
    },
    "skill-intelligence": {
        "triggers": ["skill推荐", "推荐skill", "skill report", "skill stats", "使用报告", "skill usage"],
        "examples": ["查看skill使用报告", "skill统计", "推荐skill"]
    },
}

def parse_frontmatter(content):
    m = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not m:
        return None, None
    fm = m.group(1)
    name = desc = None
    for line in fm.split('\n'):
        if line.startswith('name:'):
            name = line.split(':', 1)[1].strip().strip('"\'')
        elif line.startswith('description:'):
            desc = line.split(':', 1)[1].strip().strip('"\'')
    return name, desc

def detect_cli_deps(content):
    deps = []
    for tool in ["opencode", "claude", "gemini", "git", "cursor"]:
        if re.search(r'\b' + tool + r'\b', content):
            deps.append(tool)
    return deps

def detect_category(skill_id, content):
    text = (skill_id + " " + content[:500]).lower()
    for cat, pattern in CATEGORY_PATTERNS.items():
        if re.search(pattern, text):
            return cat
    return "general"

def scan_skills():
    skills = []
    seen = set()
    
    for source, base_dir in SCAN_DIRS:
        if not os.path.isdir(base_dir):
            continue
        for skill_md in glob.glob(os.path.join(base_dir, "**/SKILL.md"), recursive=True):
            skill_dir = os.path.dirname(skill_md)
            skill_id = os.path.basename(skill_dir)
            if skill_id in seen:
                continue
            seen.add(skill_id)
            
            try:
                with open(skill_md, 'r') as f:
                    content = f.read()
            except:
                continue
            
            name, desc = parse_frontmatter(content)
            if not name:
                name = skill_id
            if not desc:
                lines = [l for l in content.split('\n') if l.strip() and not l.startswith('---') and not l.startswith('#')]
                desc = lines[0][:200] if lines else ""
            
            trigger_data = SKILL_TRIGGERS.get(skill_id, {})
            
            skills.append({
                "id": skill_id,
                "name": name,
                "description": desc[:300],
                "path": skill_md,
                "source": source,
                "category": detect_category(skill_id, content),
                "cli_deps": detect_cli_deps(content),
                "triggers": trigger_data.get("triggers", []),
                "examples": trigger_data.get("examples", []),
                "use_count": 0,
                "success_rate": None,
                "last_used": None,
            })
    
    return skills

def main():
    skills = scan_skills()
    os.makedirs(os.path.dirname(REGISTRY_PATH), exist_ok=True)
    
    with open(REGISTRY_PATH, 'w') as f:
        json.dump(skills, f, indent=2, ensure_ascii=False)
    
    # Save triggers separately for easy editing
    with open(TRIGGERS_PATH, 'w') as f:
        json.dump(SKILL_TRIGGERS, f, indent=2, ensure_ascii=False)
    
    # Report
    no_triggers = [s["id"] for s in skills if not s["triggers"]]
    
    print(f"Registry: {REGISTRY_PATH} ({len(skills)} skills)")
    from collections import Counter
    for src, cnt in Counter(s["source"] for s in skills).most_common():
        print(f"  {src}: {cnt}")
    print(f"Categories:")
    for cat, cnt in Counter(s["category"] for s in skills).most_common():
        print(f"  {cat}: {cnt}")
    
    if no_triggers:
        print(f"\n⚠️  {len(no_triggers)} skills without triggers:")
        for sid in no_triggers:
            print(f"  - {sid}")
        print(f"Add triggers in: {TRIGGERS_PATH}")

if __name__ == "__main__":
    main()
