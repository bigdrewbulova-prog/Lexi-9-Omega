from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from typing import Any

from .models import utc_now_iso
from .safety import is_probably_destructive_instruction, slugify_project_name


@dataclass(frozen=True)
class DomainProfile:
    name: str
    keywords: tuple[str, ...]
    intent: str
    stack: tuple[str, ...]
    features: tuple[str, ...]


DOMAIN_PROFILES: tuple[DomainProfile, ...] = (
    DomainProfile(
        name="desktop companion",
        keywords=("desktop", "dashboard", "tkinter", "window", "companion", "local", "file", "workspace"),
        intent="Build a local desktop companion that converts project intent into organized notes, briefs, and safe workspace files.",
        stack=("Python", "Tkinter", "JSON local memory", "Markdown exports"),
        features=("project memory", "brief generator", "safe workspace creation", "activity log"),
    ),
    DomainProfile(
        name="web archive",
        keywords=("website", "web", "poster", "archive", "gallery", "landing", "html", "css"),
        intent="Build a polished web archive that turns a concept universe into navigable sections and visual story panels.",
        stack=("HTML", "CSS", "JavaScript", "static assets"),
        features=("hero section", "image atlas", "fact-check cards", "prompt generator"),
    ),
    DomainProfile(
        name="AI assistant shell",
        keywords=("ai", "agent", "assistant", "lexi", "model", "prompt", "auto", "autonomous"),
        intent="Create an assistant shell with local reasoning templates, visible approval gates, and memory-backed project context.",
        stack=("Python", "local templates", "JSON memory", "approval workflow"),
        features=("template generation", "auto draft mode", "owner approval", "session logs"),
    ),
    DomainProfile(
        name="science fiction knowledge system",
        keywords=("quantum", "geometry", "e8", "casimir", "field", "physics", "cosmic", "signal"),
        intent="Package speculative science-fiction ideas into a clear knowledge system that separates verified science from mythic worldbuilding.",
        stack=("Markdown", "taxonomy files", "reference atlas", "static viewer"),
        features=("claim badges", "theme decoder", "worldbuilding canon", "research notes"),
    ),
    DomainProfile(
        name="automation toolkit",
        keywords=("automation", "command", "disk", "generate", "task", "workflow", "pipeline"),
        intent="Create a controlled automation toolkit that drafts plans and files while keeping execution behind user confirmation.",
        stack=("Python", "JSON task queue", "safe file writer", "audit log"),
        features=("task queue", "dry run previews", "versioned writes", "approval modal"),
    ),
    DomainProfile(
        name="data dashboard",
        keywords=("data", "chart", "analytics", "metrics", "table", "report", "log"),
        intent="Build a dashboard that turns project logs and notes into visible status, metrics, and next-step reports.",
        stack=("Python", "Tkinter", "JSONL logs", "CSV exports"),
        features=("activity feed", "project status", "export panel", "summary reports"),
    ),
)

VISUAL_THEMES = {
    "clean geometry": ("geometry", "grid", "minimal", "clean", "structure", "shape"),
    "dark command center": ("command", "dashboard", "terminal", "disk", "control", "owner"),
    "cyber-mystic neon": ("lexi", "quantum", "neon", "cosmic", "e8", "violet", "cyan"),
    "research lab": ("science", "lab", "physics", "casimir", "experiment", "architecture"),
    "calm productivity": ("notes", "brief", "workspace", "tasks", "simple", "safe"),
}


class TemplateSignalEngine:
    """Local deterministic generator.

    It uses simple keyword analysis plus curated templates. It is intentionally
    transparent: no remote model calls, no hidden network dependency.
    """

    def generate_project_note(self, project_name: str, notes: str, recent_context: str = "") -> str:
        profile = self._select_domain(project_name, notes, recent_context)
        theme = self._select_visual_theme(project_name, notes, recent_context)
        risk_flag = is_probably_destructive_instruction(notes)

        open_questions = self._open_questions(profile.name)
        if risk_flag:
            open_questions.insert(0, "Which file operations should require explicit approval before Lexi continues?")

        return f"""# Project Notes — {project_name.strip() or "Untitled Project"}

Generated: {utc_now_iso()}
Local mode: template-based generator

## Working Summary
{profile.intent}

## Current Design Signal
The project should use a **{theme}** interface style: clear hierarchy, readable panels, visible status, and a strong separation between draft thinking and approved actions.

## Owner Principle
Owner-approved actions come first. Lexi may generate notes and plans automatically, but workspace writes stay visible, logged, and confirmable.

## Important Context Extracted
{self._compact_context(notes, recent_context)}

## Open Questions
{self._bullet_lines(open_questions)}

## Next Useful Move
Generate a full project brief, then create a safe workspace with README, notes, design signal, task list, and activity log.
""".strip()

    def generate_design_signal(self, project_name: str, notes: str, recent_context: str = "") -> tuple[str, dict[str, Any]]:
        profile = self._select_domain(project_name, notes, recent_context)
        theme = self._select_visual_theme(project_name, notes, recent_context)
        slug = slugify_project_name(project_name)
        seed = self._stable_seed(project_name, notes, recent_context)
        rng = random.Random(seed)

        priorities = list(profile.features)
        rng.shuffle(priorities)

        safety_rules = [
            "Do not delete files.",
            "Do not execute shell commands.",
            "Do not overwrite existing workspace files; create versioned files instead.",
            "Preview generated content before creating a workspace.",
            "Log every saved note, generated signal, generated brief, and workspace write.",
        ]

        if is_probably_destructive_instruction(notes):
            safety_rules.insert(0, "Potentially destructive language was detected; require confirmation before any file action.")

        tasks = self.generate_tasks(profile.name, priorities)

        signal = f"""# Design Signal — {project_name.strip() or "Untitled Project"}

Generated: {utc_now_iso()}
Generator: Lexi local template engine
Project slug: `{slug}`
Detected domain: **{profile.name}**
Visual direction: **{theme}**

## Core Intent
{profile.intent}

## Interface Direction
Use a **{theme}** layout with a command-center rhythm:
- left/top area for project identity
- main panel for notes and signals
- output panel for generated briefs
- status bar for memory, safety, and save events
- approval gate before workspace creation

## Architecture Signal
Recommended stack:
{self._bullet_lines(profile.stack)}

Core modules:
- `memory`: local project persistence
- `signal_engine`: template-based generation
- `brief_generator`: structured project brief creation
- `workspace_manager`: safe folder/file writer
- `safety`: validation, slugging, and risk checks
- `ui`: desktop interface and owner approval flow

## Feature Signal
Prioritize:
{self._bullet_lines(priorities)}

## Safety Rules
{self._bullet_lines(safety_rules)}

## Generated Tasks
{self._task_lines(tasks)}

## Acceptance Criteria
- Project notes can be saved locally.
- A design signal can be generated with no internet access.
- A full brief can be generated from the project notes.
- A workspace can be created after owner approval.
- Existing files are preserved with versioned writes.
- Auto draft mode can suggest new signals without running commands.

## Implementation Mood
Precise, calm, local-first, transparent, and owner-controlled.
""".strip()

        metadata = {
            "domain": profile.name,
            "theme": theme,
            "slug": slug,
            "seed": seed,
            "tasks": tasks,
            "safety_detected_destructive_language": is_probably_destructive_instruction(notes),
        }
        return signal, metadata

    def generate_tasks(self, domain_name: str, priorities: list[str] | tuple[str, ...]) -> list[dict[str, Any]]:
        base_tasks = [
            {
                "id": "T-001",
                "title": "Create local project memory",
                "status": "todo",
                "priority": "high",
                "details": "Store notes, generated signals, briefs, drafts, and workspace records in JSON.",
            },
            {
                "id": "T-002",
                "title": "Wire the template signal engine",
                "status": "todo",
                "priority": "high",
                "details": "Generate deterministic notes and design signals from project text.",
            },
            {
                "id": "T-003",
                "title": "Add safe workspace creation",
                "status": "todo",
                "priority": "high",
                "details": "Create folders and Markdown files only after owner confirmation.",
            },
            {
                "id": "T-004",
                "title": "Add autonomous draft mode",
                "status": "todo",
                "priority": "medium",
                "details": "Generate periodic suggestions while keeping file writes non-destructive.",
            },
            {
                "id": "T-005",
                "title": "Add activity logging",
                "status": "todo",
                "priority": "medium",
                "details": "Append major events to a JSONL log for review.",
            },
        ]

        for index, item in enumerate(priorities[:3], start=6):
            base_tasks.append(
                {
                    "id": f"T-{index:03d}",
                    "title": f"Refine {item}",
                    "status": "todo",
                    "priority": "medium",
                    "details": f"Adapt the {item} feature for the {domain_name} project direction.",
                }
            )

        return base_tasks

    def _select_domain(self, project_name: str, notes: str, recent_context: str) -> DomainProfile:
        haystack = f"{project_name} {notes} {recent_context}".lower()
        best_profile = DOMAIN_PROFILES[0]
        best_score = -1

        for profile in DOMAIN_PROFILES:
            score = sum(2 for keyword in profile.keywords if keyword in haystack)
            # Add a tiny preference for explicit project-name matches.
            score += sum(1 for keyword in profile.keywords if keyword in project_name.lower())
            if score > best_score:
                best_profile = profile
                best_score = score

        return best_profile

    def _select_visual_theme(self, project_name: str, notes: str, recent_context: str) -> str:
        haystack = f"{project_name} {notes} {recent_context}".lower()
        best_theme = "calm productivity"
        best_score = -1

        for theme, keywords in VISUAL_THEMES.items():
            score = sum(1 for keyword in keywords if keyword in haystack)
            if score > best_score:
                best_theme = theme
                best_score = score

        return best_theme

    def _stable_seed(self, *parts: str) -> int:
        digest = hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()
        return int(digest[:12], 16)

    def _compact_context(self, notes: str, recent_context: str) -> str:
        text = (notes or "").strip()
        if recent_context.strip():
            text = f"{text}\n\nRecent memory:\n{recent_context.strip()}".strip()

        if not text:
            return "- No notes yet. Start with purpose, audience, core rules, and desired output."

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        compacted = lines[:8]
        return self._bullet_lines(compacted)

    def _bullet_lines(self, items: list[str] | tuple[str, ...]) -> str:
        return "\n".join(f"- {item}" for item in items)

    def _task_lines(self, tasks: list[dict[str, Any]]) -> str:
        return "\n".join(
            f"- [{task['priority']}] {task['id']}: {task['title']} — {task['details']}" for task in tasks
        )

    def _open_questions(self, domain: str) -> list[str]:
        common = [
            "What is the first screen or file the user should see?",
            "Which actions should be draft-only versus owner-approved?",
            "What output format matters most: Markdown, JSON, folders, or UI panels?",
        ]

        if domain == "web archive":
            common.append("Which images or sections should be treated as factual, speculative, or mythic?")
        elif domain == "desktop companion":
            common.append("Should the app prioritize notes, workspace generation, or live task tracking?")
        elif domain == "AI assistant shell":
            common.append("Should future model integration be local, cloud-based, or switchable?")

        return common
