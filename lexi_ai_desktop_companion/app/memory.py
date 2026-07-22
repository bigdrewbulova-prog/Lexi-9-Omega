from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import utc_now_iso
from .safety import slugify_project_name


class LocalMemory:
    """Small local JSON memory store.

    The memory layer never executes commands. It only reads and writes app-owned
    JSON/text data under the configured Lexi directory.
    """

    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or Path.home() / ".lexi_ai_companion"
        self.data_dir = self.base_dir / "data"
        self.workspaces_dir = self.base_dir / "workspaces"
        self.projects_path = self.data_dir / "projects.json"
        self.logs_path = self.data_dir / "logs.jsonl"
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.workspaces_dir.mkdir(parents=True, exist_ok=True)

        if not self.projects_path.exists():
            self._atomic_write_json(self.projects_path, {"projects": {}})

    def _atomic_write_json(self, path: Path, payload: dict[str, Any]) -> None:
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(path)

    def log_event(self, event_type: str, payload: dict[str, Any]) -> None:
        entry = {
            "timestamp": utc_now_iso(),
            "event_type": event_type,
            "payload": payload,
        }
        with self.logs_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def load_projects(self) -> dict[str, Any]:
        try:
            return json.loads(self.projects_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            backup = self.projects_path.with_suffix(".json.corrupt")
            self.projects_path.replace(backup)
            fresh = {"projects": {}}
            self._atomic_write_json(self.projects_path, fresh)
            self.log_event("memory_recovered", {"backup": str(backup)})
            return fresh

    def save_projects(self, payload: dict[str, Any]) -> None:
        self._atomic_write_json(self.projects_path, payload)

    def ensure_project(self, project_name: str) -> dict[str, Any]:
        projects = self.load_projects()
        slug = slugify_project_name(project_name)

        if slug not in projects["projects"]:
            projects["projects"][slug] = {
                "project_name": project_name.strip(),
                "slug": slug,
                "created_at": utc_now_iso(),
                "updated_at": utc_now_iso(),
                "notes": [],
                "signals": [],
                "briefs": [],
                "drafts": [],
                "workspaces": [],
                "settings": {},
            }
            self.save_projects(projects)
            self.log_event("project_created", {"project_name": project_name, "slug": slug})

        return projects["projects"][slug]

    def add_note(self, project_name: str, text: str, source: str = "manual") -> dict[str, Any]:
        project = self.ensure_project(project_name)
        projects = self.load_projects()
        slug = project["slug"]

        entry = {
            "timestamp": utc_now_iso(),
            "source": source,
            "text": text,
        }
        projects["projects"][slug]["notes"].append(entry)
        projects["projects"][slug]["updated_at"] = utc_now_iso()
        self.save_projects(projects)
        self.log_event("note_saved", {"project_name": project_name, "source": source})
        return entry

    def add_signal(self, project_name: str, text: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        project = self.ensure_project(project_name)
        projects = self.load_projects()
        slug = project["slug"]

        entry = {
            "timestamp": utc_now_iso(),
            "text": text,
            "metadata": metadata or {},
        }
        projects["projects"][slug]["signals"].append(entry)
        projects["projects"][slug]["updated_at"] = utc_now_iso()
        self.save_projects(projects)
        self.log_event("signal_saved", {"project_name": project_name, "metadata": metadata or {}})
        return entry

    def add_brief(self, project_name: str, text: str, tasks: list[dict[str, Any]]) -> dict[str, Any]:
        project = self.ensure_project(project_name)
        projects = self.load_projects()
        slug = project["slug"]

        entry = {
            "timestamp": utc_now_iso(),
            "text": text,
            "tasks": tasks,
        }
        projects["projects"][slug]["briefs"].append(entry)
        projects["projects"][slug]["updated_at"] = utc_now_iso()
        self.save_projects(projects)
        self.log_event("brief_saved", {"project_name": project_name, "task_count": len(tasks)})
        return entry

    def add_draft(self, project_name: str, text: str, draft_type: str = "auto_signal") -> dict[str, Any]:
        project = self.ensure_project(project_name)
        projects = self.load_projects()
        slug = project["slug"]

        entry = {
            "timestamp": utc_now_iso(),
            "draft_type": draft_type,
            "text": text,
        }
        projects["projects"][slug]["drafts"].append(entry)
        projects["projects"][slug]["updated_at"] = utc_now_iso()
        self.save_projects(projects)
        self.log_event("draft_saved", {"project_name": project_name, "draft_type": draft_type})
        return entry

    def add_workspace_record(self, project_name: str, workspace_path: str, written_files: list[str]) -> None:
        project = self.ensure_project(project_name)
        projects = self.load_projects()
        slug = project["slug"]

        projects["projects"][slug]["workspaces"].append(
            {
                "timestamp": utc_now_iso(),
                "workspace_path": workspace_path,
                "written_files": written_files,
            }
        )
        projects["projects"][slug]["updated_at"] = utc_now_iso()
        self.save_projects(projects)
        self.log_event(
            "workspace_recorded",
            {
                "project_name": project_name,
                "workspace_path": workspace_path,
                "written_file_count": len(written_files),
            },
        )

    def recent_context(self, project_name: str, limit: int = 5) -> str:
        project = self.ensure_project(project_name)
        notes = project.get("notes", [])[-limit:]
        signals = project.get("signals", [])[-limit:]

        chunks: list[str] = []
        for item in notes:
            chunks.append(f"[note:{item.get('timestamp')}] {item.get('text', '')}")
        for item in signals:
            chunks.append(f"[signal:{item.get('timestamp')}] {item.get('text', '')[:1200]}")

        return "\n\n".join(chunks).strip()
