#!/usr/bin/env python3
"""skill-deps.py — 分析 skill 之间的依赖关系，生成依赖图"""

import json
import os
import re

SKILLS_DIR = os.path.expanduser("~/.openclaw/workspace/skills")
REGISTRY_PATH = os.path.expanduser("~/.openclaw/workspace/data/skill-registry.json")
DEPS_PATH = os.path.expanduser("~/.openclaw/workspace/data/skill-deps.json")
RECIPES_PATH = os.path.expanduser("~/.openclaw/workspace/data/skill-recipes.yaml")

def load_registry():
    with open(REGISTRY_PATH, 'r') as f:
        return {s["id"]: s for s in json.load(f)}

def find_references(skill_id, content, all_ids):
    """在 SKILL.md 内容中查找对其他 skill 的引用"""
    refs = []
    for other_id in all_ids:
        if other_id == skill_id:
            continue
        if other_id in content:
            refs.append(other_id)
    return refs

def load_recipe_deps():
    """从 recipes 中提取 skill 链"""
    chains = {}
    try:
        import yaml
        with open(RECIPES_PATH, 'r') as f:
            data = yaml.safe_load(f)
        for rid, recipe in data.get("recipes", {}).items():
            steps = [s["skill"] for s in recipe.get("steps", [])]
            chains[rid] = steps
    except:
        # fallback: parse yaml manually
        chains = {}
        try:
            with open(RECIPES_PATH, 'r') as f:
                content = f.read()
            current_recipe = None
            for line in content.split('\n'):
                m = re.match(r'^  (\w[\w-]+):', line)
                if m and not line.strip().startswith('- '):
                    current_recipe = m.group(1)
                    if current_recipe not in ['name', 'triggers', 'steps', 'desc', 'skill']:
                        chains[current_recipe] = []
                m2 = re.match(r'\s+- skill:\s*(.+)', line)
                if m2 and current_recipe:
                    chains[current_recipe] = chains.get(current_recipe, [])
                    chains[current_recipe].append(m2.group(1).strip())
        except:
            pass
    return chains

def main():
    registry = load_registry()
    all_ids = set(registry.keys())
    
    # Build dependency graph
    graph = {}
    for skill_id in all_ids:
        path = registry[skill_id].get("path", "")
        if not os.path.exists(path):
            continue
        with open(path, 'r') as f:
            content = f.read()
        refs = find_references(skill_id, content, all_ids)
        if refs:
            graph[skill_id] = refs
    
    # Recipe chains
    chains = load_recipe_deps()
    
    # Detect orphans (no references to or from)
    referenced = set()
    for refs in graph.values():
        referenced.update(refs)
    workspace_ids = {sid for sid, s in registry.items() if s.get("source") == "workspace"}
    orphans = workspace_ids - set(graph.keys()) - referenced
    
    # Detect circular deps
    circular = []
    for a, refs in graph.items():
        for b in refs:
            if b in graph and a in graph[b]:
                pair = tuple(sorted([a, b]))
                if pair not in circular:
                    circular.append(pair)
    
    result = {
        "graph": graph,
        "recipe_chains": chains,
        "orphans": list(orphans),
        "circular": [list(p) for p in circular],
        "stats": {
            "total_skills": len(all_ids),
            "with_deps": len(graph),
            "orphans": len(orphans),
            "circular": len(circular),
            "recipes": len(chains),
        }
    }
    
    with open(DEPS_PATH, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print(f"📊 Skill 依赖分析")
    print(f"  总 skills: {len(all_ids)}")
    print(f"  有依赖关系: {len(graph)}")
    print(f"  孤立 skills: {len(orphans)} — {', '.join(orphans) if orphans else '无'}")
    print(f"  循环依赖: {len(circular)} — {circular if circular else '无'}")
    print(f"  Recipe 链: {len(chains)}")
    
    for rid, steps in chains.items():
        print(f"    {rid}: {' → '.join(steps)}")
    
    print(f"\n📁 {DEPS_PATH}")

if __name__ == "__main__":
    main()
