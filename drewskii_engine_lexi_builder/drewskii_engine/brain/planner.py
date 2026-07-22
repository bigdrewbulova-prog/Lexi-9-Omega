"""Local CLI planning — structured plans + roadmap."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .artifacts import WORKSPACE, ensure_dirs, slugify, utc_stamp, write_bundle, write_json, write_text


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ROADMAP_PATH = PROJECT_ROOT / "docs" / "lexi_build_roadmap.md"


def roadmap() -> str:
    try:
        return ROADMAP_PATH.read_text(encoding="utf-8")
    except OSError:
        pass

    return """
LEXI-9-OMEGA ROADMAP

1. Core Brain — CLI, memory, logs, safety
2. Knowledge Core — identity, skills, prompts
3. Android Companion — Termux helpers (user-approved only)
4. UI Shell — web dashboard
5. AI Agent Layer — tools + evaluation logs
6. Lexi.PHYS — simulation / lore / visualization (not finished hardware)
"""


def build_plan_struct(idea: str) -> dict[str, Any]:
    idea = (idea or "").strip() or "Untitled Lexi module"
    return {
        "title": idea,
        "goal": f"Turn “{idea}” into a working Lexi-9-Omega prototype slice.",
        "reality_check": (
            "Build the safe, testable version first. Advanced autonomy, deep Android "
            "integration, or physics concepts stay separated from what can run today."
        ),
        "prototype_path": [
            "Define the feature in one sentence.",
            "Create a local file/template for it.",
            "Add memory/logging if it needs to learn from past use.",
            "Add a permission gate if it touches phone tools, files, camera, location, contacts, messages, or accounts.",
            "Test it manually.",
            "Save results in the project log and evaluation log.",
            "Improve one version at a time.",
        ],
        "stack": [
            "Python local engine",
            "SQLite project memory",
            "Markdown / JSON / HTML artifacts",
            "Termux:API helpers (user-approved only)",
            "Web dashboard shell",
        ],
        "safety": [
            "No hidden control",
            "No account bypassing",
            "No password collection",
            "No unauthorized surveillance",
            "No OS-level control outside official APIs",
            "Speculative physics = simulation / lore / visualization only",
        ],
        "next_action": f"Write the first module file or deliverable for: {idea}",
        "summary": f"Safe prototype plan for {idea}",
    }


def build_plan(idea: str) -> str:
    plan = build_plan_struct(idea)
    lines = [
        f"PROJECT PLAN: {plan['title']}",
        "",
        "Goal:",
        plan["goal"],
        "",
        "Reality Check:",
        plan["reality_check"],
        "",
        "Prototype Path:",
    ]
    for i, step in enumerate(plan["prototype_path"], 1):
        lines.append(f"{i}. {step}")
    lines += ["", "Suggested Build Stack:"]
    for item in plan["stack"]:
        lines.append(f"- {item}")
    lines += ["", "Safety Layer:"]
    for item in plan["safety"]:
        lines.append(f"- {item}")
    lines += ["", "Next Action:", plan["next_action"]]
    return "\n".join(lines)


def save_plan(memory, idea: str) -> dict[str, Any]:
    """Create structured plan, write MD/JSON, store in SQLite."""
    ensure_dirs()
    plan = build_plan_struct(idea)
    markdown = build_plan(idea) + "\n"
    paths = write_bundle(
        kind="plans",
        title=plan["title"],
        markdown=markdown,
        data=plan,
        html=None,
        subdir="plans",
    )
    # also keep a simple copy under workspace/plans
    stamp = utc_stamp()
    slug = slugify(plan["title"])
    write_text(WORKSPACE / "plans" / f"{stamp}-{slug}.md", markdown)
    write_json(WORKSPACE / "plans" / f"{stamp}-{slug}.json", plan)

    plan_id = memory.save_plan(plan["title"], plan)
    deliverable_id = memory.save_deliverable("plan", plan["title"], paths, meta={"plan_id": plan_id})
    return {
        "plan_id": plan_id,
        "deliverable_id": deliverable_id,
        "plan": plan,
        "paths": paths,
        "text": markdown,
    }
