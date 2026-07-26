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
                updated_at TEXT NOT NULL DEFAULT ''
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
            CREATE TABLE IF NOT EXISTS pack_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand_name TEXT NOT NULL,
                customer_name TEXT NOT NULL DEFAULT '',
                customer_note TEXT NOT NULL DEFAULT '',
                amount_usd REAL NOT NULL DEFAULT 50,
                status TEXT NOT NULL DEFAULT 'generated',
                zip_path TEXT NOT NULL DEFAULT '',
                deliverable_id INTEGER,
                meta_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )
        # Migrate legacy memory table (key,value only)
        cols = {row[1] for row in cur.execute("PRAGMA table_info(memory)").fetchall()}
        if "updated_at" not in cols:
            cur.execute("ALTER TABLE memory ADD COLUMN updated_at TEXT NOT NULL DEFAULT ''")
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

    # --- Stage-1 pack order ledger (manual $50 path; no payment processor) ---

    VALID_ORDER_STATUSES = frozenset(
        {
            "draft",
            "generated",
            "delivered",
            "paid_manual",
            "refunded_manual",
            "cancelled",
        }
    )

    def save_pack_order(
        self,
        brand_name: str,
        *,
        customer_name: str = "",
        customer_note: str = "",
        amount_usd: float = 50.0,
        status: str = "generated",
        zip_path: str = "",
        deliverable_id: int | None = None,
        meta: dict[str, Any] | None = None,
    ) -> int:
        status = (status or "generated").strip().lower()
        if status not in self.VALID_ORDER_STATUSES:
            raise ValueError(
                f"Invalid order status {status!r}; allowed: {sorted(self.VALID_ORDER_STATUSES)}"
            )
        try:
            amount = float(amount_usd)
        except (TypeError, ValueError) as exc:
            raise ValueError("amount_usd must be a number") from exc
        if amount < 0 or amount > 100_000:
            raise ValueError("amount_usd out of range")
        now = _utc_now()
        cur = self.conn.execute(
            """
            INSERT INTO pack_orders (
                brand_name, customer_name, customer_note, amount_usd, status,
                zip_path, deliverable_id, meta_json, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                (brand_name or "").strip() or "Untitled pack",
                (customer_name or "").strip()[:200],
                (customer_note or "").strip()[:2000],
                amount,
                status,
                zip_path or "",
                deliverable_id,
                json.dumps(meta or {}, ensure_ascii=True),
                now,
                now,
            ),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def update_pack_order_status(
        self,
        order_id: int,
        status: str,
        *,
        note_append: str = "",
    ) -> dict[str, Any] | None:
        status = (status or "").strip().lower()
        if status not in self.VALID_ORDER_STATUSES:
            raise ValueError(
                f"Invalid order status {status!r}; allowed: {sorted(self.VALID_ORDER_STATUSES)}"
            )
        row = self.conn.execute(
            "SELECT id, meta_json FROM pack_orders WHERE id = ?",
            (int(order_id),),
        ).fetchone()
        if not row:
            return None
        meta = json.loads(row["meta_json"] or "{}")
        if note_append.strip():
            trail = list(meta.get("status_notes") or [])
            trail.append({"at": _utc_now(), "status": status, "note": note_append.strip()[:500]})
            meta["status_notes"] = trail[-20:]
        self.conn.execute(
            """
            UPDATE pack_orders
            SET status = ?, meta_json = ?, updated_at = ?
            WHERE id = ?
            """,
            (status, json.dumps(meta, ensure_ascii=True), _utc_now(), int(order_id)),
        )
        self.conn.commit()
        return self.get_pack_order(int(order_id))

    def get_pack_order(self, order_id: int) -> dict[str, Any] | None:
        row = self.conn.execute(
            """
            SELECT id, brand_name, customer_name, customer_note, amount_usd, status,
                   zip_path, deliverable_id, meta_json, created_at, updated_at
            FROM pack_orders WHERE id = ?
            """,
            (int(order_id),),
        ).fetchone()
        return self._order_row(row) if row else None

    def recent_pack_orders(self, limit: int = 50) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT id, brand_name, customer_name, customer_note, amount_usd, status,
                   zip_path, deliverable_id, meta_json, created_at, updated_at
            FROM pack_orders ORDER BY id DESC LIMIT ?
            """,
            (max(1, min(int(limit), 500)),),
        ).fetchall()
        return [self._order_row(r) for r in rows]

    def pack_order_stats(self) -> dict[str, Any]:
        total = self.conn.execute("SELECT COUNT(*) AS c FROM pack_orders").fetchone()["c"]
        by_status: dict[str, int] = {}
        for r in self.conn.execute(
            "SELECT status, COUNT(*) AS c FROM pack_orders GROUP BY status"
        ).fetchall():
            by_status[r["status"]] = int(r["c"])
        paid = self.conn.execute(
            """
            SELECT COALESCE(SUM(amount_usd), 0) AS s FROM pack_orders
            WHERE status = 'paid_manual'
            """
        ).fetchone()["s"]
        pipeline = self.conn.execute(
            """
            SELECT COALESCE(SUM(amount_usd), 0) AS s FROM pack_orders
            WHERE status IN ('generated', 'delivered', 'draft')
            """
        ).fetchone()["s"]
        return {
            "orders": int(total),
            "by_status": by_status,
            "paid_manual_usd": float(paid or 0),
            "pipeline_usd": float(pipeline or 0),
            "price_starting_usd": 50,
        }

    @staticmethod
    def _order_row(r: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": r["id"],
            "brand_name": r["brand_name"],
            "customer_name": r["customer_name"],
            "customer_note": r["customer_note"],
            "amount_usd": r["amount_usd"],
            "status": r["status"],
            "zip_path": r["zip_path"],
            "deliverable_id": r["deliverable_id"],
            "meta": json.loads(r["meta_json"] or "{}"),
            "created_at": r["created_at"],
            "updated_at": r["updated_at"],
        }

    def stats(self) -> dict[str, int]:
        def count(table: str) -> int:
            row = self.conn.execute(f"SELECT COUNT(*) AS c FROM {table}").fetchone()
            return int(row["c"])

        out = {
            "memory_keys": count("memory"),
            "plans": count("plans"),
            "deliverables": count("deliverables"),
            "eval_logs": count("eval_logs"),
        }
        try:
            out["pack_orders"] = count("pack_orders")
        except sqlite3.OperationalError:
            out["pack_orders"] = 0
        return out
