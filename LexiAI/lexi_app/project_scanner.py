#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import hashlib
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "lexi_app" / "config.json"

TEXT_SUFFIXES = {
    ".bash",
    ".cfg",
    ".command",
    ".conf",
    ".css",
    ".csv",
    ".env.example",
    ".gitignore",
    ".html",
    ".ini",
    ".ipynb",
    ".js",
    ".json",
    ".jsonl",
    ".md",
    ".py",
    ".rb",
    ".rs",
    ".sh",
    ".sql",
    ".swift",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}

EXCLUDED_DIRS = {
    ".cache",
    ".git",
    ".idea",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "target",
    "vendor",
}

EXCLUDED_FILE_NAMES = {
    ".DS_Store",
    ".env",
    ".env.local",
    ".env.development",
    ".env.production",
}

MAX_SUMMARY_BYTES = 128_000


@dataclass
class ProjectFile:
    root: str
    path: str
    kind: str
    size: int
    modified_at: str
    fingerprint: str
    summary: str


class ProjectScanner:
    def __init__(self, roots: Optional[Iterable[str]] = None, max_files: int = 500) -> None:
        self.roots = self._resolve_roots(roots)
        self.max_files = max(1, int(max_files))

    @classmethod
    def from_config(cls, roots: Optional[Iterable[str]] = None, max_files: int = 500) -> "ProjectScanner":
        if roots:
            return cls(roots=roots, max_files=max_files)

        configured_roots: List[str] = []
        if CONFIG_PATH.exists():
            try:
                cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
                configured_roots = cfg.get("workspace_roots") or cfg.get("mac_file_roots") or []
            except (json.JSONDecodeError, OSError):
                configured_roots = []

        return cls(roots=configured_roots or default_roots(), max_files=max_files)

    def scan(self) -> List[dict]:
        records: List[ProjectFile] = []
        seen: set[Path] = set()

        for root in self.roots:
            if len(records) >= self.max_files:
                break
            for path in self._iter_files(root):
                if len(records) >= self.max_files:
                    break
                try:
                    resolved = path.resolve()
                except OSError:
                    continue
                if resolved in seen:
                    continue
                seen.add(resolved)
                record = self._record_for(root, resolved)
                if record:
                    records.append(record)

        return [asdict(record) for record in records]

    def search(self, query: str, limit: int = 25) -> List[dict]:
        terms = [part.lower() for part in query.split() if part.strip()]
        matches = []
        for record in self.scan():
            haystack = " ".join(
                [record["path"], record["kind"], record["summary"]]
            ).lower()
            if not terms or all(term in haystack for term in terms):
                matches.append(record)
            if len(matches) >= limit:
                break
        return matches

    def _resolve_roots(self, roots: Optional[Iterable[str]]) -> List[Path]:
        resolved_roots: List[Path] = []
        for root in roots or default_roots():
            candidate = Path(root).expanduser()
            try:
                candidate = candidate.resolve()
            except OSError:
                continue
            if candidate.exists() and candidate.is_dir() and candidate not in resolved_roots:
                resolved_roots.append(candidate)
        return resolved_roots

    def _iter_files(self, root: Path) -> Iterable[Path]:
        for current, dirs, files in os.walk(root):
            current_path = Path(current)
            dirs[:] = [
                name
                for name in sorted(dirs)
                if name not in EXCLUDED_DIRS and not name.startswith(".")
            ]
            for name in sorted(files):
                if name in EXCLUDED_FILE_NAMES:
                    continue
                path = current_path / name
                if path.is_symlink() or not path.is_file():
                    continue
                if not self._is_relevant(path):
                    continue
                yield path

    def _record_for(self, root: Path, path: Path) -> Optional[ProjectFile]:
        try:
            stat = path.stat()
        except OSError:
            return None

        if stat.st_size <= 0:
            return None

        modified_at = datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds")
        return ProjectFile(
            root=str(root),
            path=str(path),
            kind=self._kind(path),
            size=stat.st_size,
            modified_at=modified_at,
            fingerprint=self._fingerprint(path, stat),
            summary=self._summary(path, stat.st_size),
        )

    def _is_relevant(self, path: Path) -> bool:
        if path.name == ".env.example":
            return True
        if path.name.startswith(".") and path.name != ".env.example":
            return False
        if path.suffix.lower() in TEXT_SUFFIXES:
            return True
        if path.name in {"README", "Makefile", "Dockerfile", "Modelfile"}:
            return True
        return False

    def _kind(self, path: Path) -> str:
        if path.name == "Modelfile":
            return "model-config"
        suffix = path.suffix.lower().lstrip(".")
        if suffix in {"md", "txt"}:
            return "docs"
        if suffix in {"py", "js", "ts", "tsx", "sh", "command", "swift"}:
            return "code"
        if suffix in {"json", "yaml", "yml", "toml", "ini", "cfg"}:
            return "config"
        if suffix in {"csv", "jsonl"}:
            return "data"
        return suffix or "file"

    def _summary(self, path: Path, size: int) -> str:
        if size > MAX_SUMMARY_BYTES:
            return f"{path.name} ({size} bytes)"
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return path.name
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            return path.name
        first = lines[0]
        if len(first) > 180:
            first = first[:177] + "..."
        return first

    def _fingerprint(self, path: Path, stat: os.stat_result) -> str:
        if stat.st_size > MAX_SUMMARY_BYTES:
            return f"meta:{stat.st_size}:{stat.st_mtime_ns}"

        digest = hashlib.sha256()
        try:
            with path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(65536), b""):
                    digest.update(chunk)
        except OSError:
            return f"meta:{stat.st_size}:{stat.st_mtime_ns}"
        return digest.hexdigest()


def default_roots() -> List[str]:
    runtime_home = Path.home()
    workspace_owner_home = ROOT.parent
    owner_work_roots = [
        workspace_owner_home / "Desktop",
        workspace_owner_home / "Documents",
        workspace_owner_home / "Downloads",
    ]
    runtime_work_roots = [
        runtime_home / "Desktop",
        runtime_home / "Documents",
        runtime_home / "Downloads",
    ]
    extra_roots = owner_work_roots
    if runtime_home == workspace_owner_home or not any(path.exists() for path in owner_work_roots):
        extra_roots = runtime_work_roots

    candidates = [
        ROOT,
        ROOT / "workspace",
        ROOT / "chat_logs",
        *extra_roots,
    ]
    return [str(path) for path in candidates if path.exists() and path.is_dir()]
