from __future__ import annotations

from typing import Any

from .models import utc_now_iso
from .safety import slugify_project_name


class TemplateBriefGenerator:
    """Formats a generated design signal into a project brief."""

    def generate_brief(
        self,
        project_name: str,
        notes: str,
        design_signal: str,
        metadata: dict[str, Any],
        tasks: list[dict[str, Any]],
    ) -> str:
        slug = slugify_project_name(project_name)
        domain = metadata.get("domain", "general project")
        theme = metadata.get("theme", "calm productivity")

        return f"""# Project Brief — {project_name.strip() or "Untitled Project"}

Generated: {utc_now_iso()}
Project slug: `{slug}`
Mode: Local template-based generator

## 1. Purpose
Create a working **{domain}** system that converts rough project notes into structured notes, design signals, briefs, and safe workspace files.

## 2. Source Notes
{self._safe_block(notes)}

## 3. Design Direction
Theme: **{theme}**

The interface should feel deliberate and controlled:
- clean project identity at the top
- clear command buttons
- large readable input/output panels
- visible local-save status
- no hidden destructive behavior

## 4. System Architecture
Recommended local architecture:
- UI layer handles user input and approval.
- Controller coordinates generation and persistence.
- Signal engine creates local template-based notes and signals.
- Brief generator turns signals into structured Markdown.
- Memory layer stores JSON project history.
- Workspace manager creates folders and files safely.
- Safety layer validates names, paths, and risky instructions.

## 5. Core Features
- Save project notes locally.
- Generate project notes from local templates.
- Generate design signals from local templates.
- Generate a full project brief.
- Create a workspace after confirmation.
- Preserve existing files with versioned writes.
- Generate autonomous draft suggestions without executing commands.

## 6. Safety Controls
- No shell execution.
- No deletion.
- No silent overwrites.
- User confirmation before workspace creation.
- Activity logs saved locally.
- Destructive wording is flagged for extra caution.

## 7. Generated Design Signal
{design_signal}

## 8. Task List
{self._task_markdown(tasks)}

## 9. Next Steps
1. Run the desktop app.
2. Enter or refine project notes.
3. Click **Generate Brief**.
4. Review the generated brief.
5. Click **Create Workspace**.
6. Continue editing files inside the generated workspace.
""".strip()

    def _safe_block(self, text: str) -> str:
        stripped = (text or "").strip()
        if not stripped:
            return "_No source notes were provided._"
        return "\n".join(f"> {line}" if line.strip() else ">" for line in stripped.splitlines())

    def _task_markdown(self, tasks: list[dict[str, Any]]) -> str:
        if not tasks:
            return "- No tasks generated."

        return "\n".join(
            f"- [ ] **{task.get('id', 'T-000')}** — {task.get('title', 'Untitled task')} "
            f"({task.get('priority', 'medium')}): {task.get('details', '')}"
            for task in tasks
        )
