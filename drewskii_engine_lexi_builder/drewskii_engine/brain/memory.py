"""Local project memory — SQLite, user-space only."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class Memory:
    """SQLite memory for notes, plans, deliverables, and eval logs."""

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        cur = self.conn.cursor()
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS memory (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                idea TEXT NOT NULL,
                plan_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS deliverables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL,
                title TEXT NOT NULL,
                paths_json TEXT NOT NULL,
                meta_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS eval_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                subject TEXT NOT NULL,
                score REAL,
                notes TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        self.conn.commit()

    def set(self, key: str, value: str) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO memory (key, value, updated_at) VALUES (?, ?, ?)",
            (key, value, _utc_now()),
        )
        self.conn.commit()

    def get(self, key: str) -> str | None:
        row = self.conn.execute(
            "SELECT value FROM memory WHERE key = ?", (key,)
        ).fetchone()
        return row["value"] if row else None

    def all(self) -> list[tuple[str, str]]:
        rows = self.conn.execute(
            "SELECT key, value FROM memory ORDER BY key"
        ).fetchall()
        return [(r["key"], r["value"]) for r in rows]

    def save_plan(self, idea: str, plan: dict[str, Any]) -> int:
        cur = self.conn.execute(
            "INSERT INTO plans (idea, plan_json, created_at) VALUES (?, ?, ?)",
            (idea, json.dumps(plan, ensure_ascii=True), _utc_now()),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def recent_plans(self, limit: int = 10) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT id, idea, plan_json, created_at FROM plans ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        out = []
        for r in rows:
            out.append(
                {
                    "id": r["id"],
                    "idea": r["idea"],
                    "plan": json.loads(r["plan_json"]),
                    "created_at": r["created_at"],
                }
            )
        return out

    def save_deliverable(
        self,
        kind: str,
        title: str,
        paths: dict[str, str],
        meta: dict[str, Any] | None = None,
    ) -> int:
        cur = self.conn.execute(
            """
            INSERT INTO deliverables (kind, title, paths_json, meta_json, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                kind,
                title,
                json.dumps(paths, ensure_ascii=True),
                json.dumps(meta or {}, ensure_ascii=True),
                _utc_now(),
            ),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def recent_deliverables(self, limit: int = 20) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT id, kind, title, paths_json, meta_json, created_at
            FROM deliverables ORDER BY id DESC LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [
            {
                "id": r["id"],
                "kind": r["kind"],
                "title": r["title"],
                "paths": json.loads(r["paths_json"]),
                "meta": json.loads(r["meta_json"]),
                "created_at": r["created_at"],
            }
            for r in rows
        ]

    def log_eval(
        self,
        category: str,
        subject: str,
        notes: str,
        score: float | None = None,
        payload: dict[str, Any] | None = None,
    ) -> int:
        cur = self.conn.execute(
            """
            INSERT INTO eval_logs (category, subject, score, notes, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                category,
                subject,
                score,
                notes,
                json.dumps(payload or {}, ensure_ascii=True),
                _utc_now(),
            ),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def recent_evals(self, limit: int = 20) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT id, category, subject, score, notes, payload_json, created_at
            FROM eval_logs ORDER BY id DESC LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [
            {
                "id": r["id"],
                "category": r["category"],
                "subject": r["subject"],
                "score": r["score"],
                "notes": r["notes"],
                "payload": json.loads(r["payload_json"]),
                "created_at": r["created_at"],
            }
            for r in rows
        ]

    def stats(self) -> dict[str, int]:
        def count(table: str) -> int:
            row = self.conn.execute(f"SELECT COUNT(*) AS c FROM {table}").fetchone()
            return int(row["c"])

        return {
            "memory_keys": count("memory"),
            "plans": count("plans"),
            "deliverables": count("deliverables"),
            "eval_logs": count("eval_logs"),
        }
