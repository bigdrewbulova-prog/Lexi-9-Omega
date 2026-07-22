from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass
class GeneratedBundle:
    project_name: str
    slug: str
    note: str
    signal: str
    brief: str
    tasks: list[dict[str, Any]]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkspaceResult:
    workspace_path: str
    written_files: list[str]
    skipped_files: list[str]
    message: str
