from __future__ import annotations

from pathlib import Path
from typing import Any

from .brief_generator import TemplateBriefGenerator
from .memory import LocalMemory
from .models import GeneratedBundle, WorkspaceResult
from .safety import slugify_project_name, validate_project_name
from .signal_engine import TemplateSignalEngine
from .workspace_manager import WorkspaceManager


class LexiController:
    def __init__(self, base_dir: Path | None = None) -> None:
        self.memory = LocalMemory(base_dir=base_dir)
        self.signal_engine = TemplateSignalEngine()
        self.brief_generator = TemplateBriefGenerator()
        self.workspace_manager = WorkspaceManager(self.memory.workspaces_dir)
        self.last_bundle: GeneratedBundle | None = None

    def save_note(self, project_name: str, note_text: str) -> str:
        ok, message = validate_project_name(project_name)
        if not ok:
            raise ValueError(message)

        entry = self.memory.add_note(project_name, note_text, source="manual")
        return f"Saved note at {entry['timestamp']}."

    def generate_project_note(self, project_name: str, note_text: str) -> str:
        ok, message = validate_project_name(project_name)
        if not ok:
            raise ValueError(message)

        context = self.memory.recent_context(project_name)
        generated = self.signal_engine.generate_project_note(project_name, note_text, context)
        self.memory.add_note(project_name, generated, source="generated")
        return generated

    def generate_bundle(self, project_name: str, note_text: str) -> GeneratedBundle:
        ok, message = validate_project_name(project_name)
        if not ok:
            raise ValueError(message)

        project = self.memory.ensure_project(project_name)
        context = self.memory.recent_context(project_name)

        generated_note = self.signal_engine.generate_project_note(project_name, note_text, context)
        signal, metadata = self.signal_engine.generate_design_signal(project_name, note_text, context)
        tasks = metadata.get("tasks", [])
        brief = self.brief_generator.generate_brief(project_name, note_text, signal, metadata, tasks)

        bundle = GeneratedBundle(
            project_name=project_name.strip(),
            slug=project["slug"],
            note=generated_note,
            signal=signal,
            brief=brief,
            tasks=tasks,
            metadata=metadata,
        )

        self.memory.add_note(project_name, generated_note, source="generated")
        self.memory.add_signal(project_name, signal, metadata)
        self.memory.add_brief(project_name, brief, tasks)
        self.last_bundle = bundle
        return bundle

    def generate_auto_draft(self, project_name: str, note_text: str) -> str:
        ok, message = validate_project_name(project_name)
        if not ok:
            raise ValueError(message)

        context = self.memory.recent_context(project_name)
        signal, metadata = self.signal_engine.generate_design_signal(project_name, note_text, context)
        draft = f"{signal}\n\n---\nAuto draft only. No workspace files were changed."
        self.memory.add_draft(project_name, draft, draft_type="auto_design_signal")
        return draft

    def preview_workspace(self, project_name: str) -> list[str]:
        ok, message = validate_project_name(project_name)
        if not ok:
            raise ValueError(message)

        return self.workspace_manager.preview_workspace(project_name)

    def create_workspace(self, bundle: GeneratedBundle | None = None) -> WorkspaceResult:
        active_bundle = bundle or self.last_bundle
        if active_bundle is None:
            raise ValueError("Generate a brief before creating a workspace.")

        result = self.workspace_manager.create_workspace(active_bundle)
        self.memory.add_workspace_record(
            active_bundle.project_name,
            result.workspace_path,
            result.written_files,
        )
        return result

    def project_slug(self, project_name: str) -> str:
        return slugify_project_name(project_name)

    def app_paths(self) -> dict[str, str]:
        return {
            "base_dir": str(self.memory.base_dir),
            "data_dir": str(self.memory.data_dir),
            "workspaces_dir": str(self.memory.workspaces_dir),
            "projects_path": str(self.memory.projects_path),
            "logs_path": str(self.memory.logs_path),
        }

    def project_summary(self, project_name: str) -> dict[str, Any]:
        project = self.memory.ensure_project(project_name)
        return {
            "project_name": project.get("project_name", project_name),
            "slug": project.get("slug", self.project_slug(project_name)),
            "notes": len(project.get("notes", [])),
            "signals": len(project.get("signals", [])),
            "briefs": len(project.get("briefs", [])),
            "drafts": len(project.get("drafts", [])),
            "workspaces": len(project.get("workspaces", [])),
            "updated_at": project.get("updated_at", ""),
        }
