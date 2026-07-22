#!/usr/bin/env python3
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from brain.memory import (
    latest_project_scan_snapshot,
    recent_project_monitor_checkins,
    save_project_monitor_checkin,
    save_project_scan_snapshot,
    upsert_project_files,
)

try:
    from .project_scanner import ProjectScanner
except ImportError:
    from project_scanner import ProjectScanner


SIGNATURE_FIELDS = ("kind", "size", "summary", "fingerprint")


class ProjectMonitor:
    """Snapshots project scans and reports meaningful changes over time."""

    def __init__(
        self,
        roots: Optional[Iterable[str]] = None,
        max_files: int = 500,
        query: str = "",
    ) -> None:
        self.scanner = ProjectScanner.from_config(roots=roots, max_files=max_files)
        self.query = query.strip()

    def check_in(self) -> Dict[str, Any]:
        records = (
            self.scanner.search(self.query, limit=self.scanner.max_files)
            if self.query
            else self.scanner.scan()
        )
        upsert_project_files(records)

        roots = [str(root) for root in self.scanner.roots]
        previous = latest_project_scan_snapshot(
            roots=roots,
            max_files=self.scanner.max_files,
            query=self.query,
        )
        snapshot_id = save_project_scan_snapshot(
            roots=roots,
            max_files=self.scanner.max_files,
            query=self.query,
            records=records,
        )

        changes = self.diff(previous["records"] if previous else None, records)
        summary = self.summarize(
            changes=changes,
            current_count=len(records),
            previous_count=previous["file_count"] if previous else 0,
            baseline=previous is None,
        )
        status = summary["status"]
        checkin_id = save_project_monitor_checkin(
            snapshot_id=snapshot_id,
            previous_snapshot_id=previous["id"] if previous else None,
            roots=roots,
            status=status,
            summary=summary,
            changes=changes,
        )

        return {
            "checkin_id": checkin_id,
            "snapshot_id": snapshot_id,
            "previous_snapshot_id": previous["id"] if previous else None,
            "roots": roots,
            "query": self.query,
            "status": status,
            "summary": summary,
            "changes": changes,
            "files": records[:100],
        }

    @staticmethod
    def diff(previous_records: Optional[List[dict]], current_records: List[dict]) -> Dict[str, List[dict]]:
        if previous_records is None:
            return {"added": [], "modified": [], "removed": []}

        previous_by_path = {record["path"]: record for record in previous_records}
        current_by_path = {record["path"]: record for record in current_records}

        added = [
            ProjectMonitor._present_record(current_by_path[path])
            for path in sorted(set(current_by_path) - set(previous_by_path))
        ]
        removed = [
            ProjectMonitor._present_record(previous_by_path[path])
            for path in sorted(set(previous_by_path) - set(current_by_path))
        ]
        modified = []
        for path in sorted(set(previous_by_path) & set(current_by_path)):
            previous = previous_by_path[path]
            current = current_by_path[path]
            fields = [
                field
                for field in SIGNATURE_FIELDS
                if previous.get(field) != current.get(field)
            ]
            if fields:
                modified.append(
                    {
                        "path": path,
                        "fields": fields,
                        "previous": ProjectMonitor._present_record(previous),
                        "current": ProjectMonitor._present_record(current),
                    }
                )

        return {"added": added, "modified": modified, "removed": removed}

    @staticmethod
    def summarize(
        changes: Dict[str, List[dict]],
        current_count: int,
        previous_count: int,
        baseline: bool,
    ) -> Dict[str, Any]:
        counts = {name: len(items) for name, items in changes.items()}
        total_changes = sum(counts.values())
        if baseline:
            status = "baseline"
            message = f"Baseline snapshot stored for {current_count} files."
        elif total_changes:
            status = "changed"
            message = (
                f"{total_changes} meaningful project changes: "
                f"{counts['added']} added, {counts['modified']} modified, "
                f"{counts['removed']} removed."
            )
        else:
            status = "unchanged"
            message = f"No meaningful project changes across {current_count} files."

        return {
            "status": status,
            "message": message,
            "baseline": baseline,
            "current_file_count": current_count,
            "previous_file_count": previous_count,
            "total_changes": total_changes,
            "added_count": counts["added"],
            "modified_count": counts["modified"],
            "removed_count": counts["removed"],
        }

    @staticmethod
    def recent_checkins(limit: int = 10) -> List[dict]:
        return recent_project_monitor_checkins(limit=limit)

    @staticmethod
    def _present_record(record: dict) -> dict:
        return {
            "root": record.get("root", ""),
            "path": record.get("path", ""),
            "kind": record.get("kind", ""),
            "size": record.get("size", 0),
            "modified_at": record.get("modified_at", ""),
            "summary": record.get("summary", ""),
        }
