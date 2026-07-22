from pathlib import Path

from app.models import GeneratedBundle
from app.workspace_manager import WorkspaceManager


def test_workspace_manager_creates_files(tmp_path: Path):
    manager = WorkspaceManager(tmp_path)
    bundle = GeneratedBundle(
        project_name="core",
        slug="core",
        note="# Note",
        signal="# Signal",
        brief="# Brief",
        tasks=[{"id": "T-001", "title": "Task", "priority": "high", "details": "Test"}],
        metadata={"domain": "desktop companion"},
    )

    result = manager.create_workspace(bundle)

    assert Path(result.workspace_path).exists()
    assert (Path(result.workspace_path) / "README.md").exists()
    assert (Path(result.workspace_path) / "notes" / "project_brief.md").exists()
