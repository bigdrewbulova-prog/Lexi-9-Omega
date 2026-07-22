import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.environ.get("LEXI_MEMORY_DB", ROOT / "memory" / "lexi_memory.db"))


def _now():
    return datetime.now().isoformat(timespec="seconds")


def _connect():
    DB_PATH.parent.mkdir(exist_ok=True)
    return sqlite3.connect(DB_PATH)


def _json(data):
    return json.dumps(data, ensure_ascii=True, sort_keys=True)


def _roots_key(roots):
    return _json(sorted(str(root) for root in roots))


def _ensure_column(cur, table, column, definition):
    cur.execute(f"PRAGMA table_info({table})")
    columns = {row[1] for row in cur.fetchall()}
    if column not in columns:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def init_memory():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = _connect()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS memories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_input TEXT NOT NULL,
        lexi_response TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS autonomous_runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        goal TEXT NOT NULL,
        mode TEXT NOT NULL,
        autonomy TEXT NOT NULL,
        status TEXT NOT NULL,
        plan_json TEXT NOT NULL,
        result_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS project_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        root TEXT NOT NULL,
        path TEXT NOT NULL UNIQUE,
        kind TEXT NOT NULL,
        size INTEGER NOT NULL,
        modified_at TEXT NOT NULL,
        fingerprint TEXT NOT NULL DEFAULT '',
        summary TEXT NOT NULL,
        indexed_at TEXT NOT NULL
    )
    """)
    _ensure_column(cur, "project_files", "fingerprint", "TEXT NOT NULL DEFAULT ''")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS project_scan_snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        roots_key TEXT NOT NULL,
        roots_json TEXT NOT NULL,
        max_files INTEGER NOT NULL,
        query TEXT NOT NULL,
        file_count INTEGER NOT NULL,
        records_json TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS project_monitor_checkins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        snapshot_id INTEGER NOT NULL,
        previous_snapshot_id INTEGER,
        roots_key TEXT NOT NULL,
        roots_json TEXT NOT NULL,
        status TEXT NOT NULL,
        summary_json TEXT NOT NULL,
        changes_json TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS artifacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER,
        path TEXT NOT NULL,
        kind TEXT NOT NULL,
        description TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

def save_memory(user_input, lexi_response):
    init_memory()
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO memories (user_input, lexi_response, created_at) VALUES (?, ?, ?)",
        (user_input, lexi_response, _now())
    )
    conn.commit()
    conn.close()

def recent_memories(limit=10):
    init_memory()
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT user_input, lexi_response, created_at FROM memories ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def save_autonomous_run(goal, mode, autonomy, status, plan, result):
    init_memory()
    created_at = _now()
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO autonomous_runs
            (goal, mode, autonomy, status, plan_json, result_json, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            goal,
            mode,
            autonomy,
            status,
            json.dumps(plan, ensure_ascii=True, sort_keys=True),
            json.dumps(result, ensure_ascii=True, sort_keys=True),
            created_at,
            created_at,
        ),
    )
    run_id = cur.lastrowid
    conn.commit()
    conn.close()
    return run_id


def recent_autonomous_runs(limit=10):
    init_memory()
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, goal, mode, autonomy, status, plan_json, result_json, created_at, updated_at
        FROM autonomous_runs
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = []
    for row in cur.fetchall():
        rows.append(
            {
                "id": row[0],
                "goal": row[1],
                "mode": row[2],
                "autonomy": row[3],
                "status": row[4],
                "plan": json.loads(row[5]),
                "result": json.loads(row[6]),
                "created_at": row[7],
                "updated_at": row[8],
            }
        )
    conn.close()
    return rows


def upsert_project_files(records):
    init_memory()
    indexed_at = _now()
    conn = _connect()
    cur = conn.cursor()
    for record in records:
        cur.execute(
            """
            INSERT INTO project_files
                (root, path, kind, size, modified_at, fingerprint, summary, indexed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(path) DO UPDATE SET
                root=excluded.root,
                kind=excluded.kind,
                size=excluded.size,
                modified_at=excluded.modified_at,
                fingerprint=excluded.fingerprint,
                summary=excluded.summary,
                indexed_at=excluded.indexed_at
            """,
            (
                record["root"],
                record["path"],
                record["kind"],
                int(record["size"]),
                record["modified_at"],
                record.get("fingerprint", ""),
                record["summary"],
                indexed_at,
            ),
        )
    conn.commit()
    conn.close()
    return len(records)


def search_indexed_files(query, limit=25):
    init_memory()
    terms = [part.lower() for part in query.split() if part.strip()]
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT root, path, kind, size, modified_at, fingerprint, summary, indexed_at
        FROM project_files
        ORDER BY indexed_at DESC, path ASC
        LIMIT 1000
        """
    )
    results = []
    for row in cur.fetchall():
        haystack = " ".join(str(value).lower() for value in row)
        if not terms or all(term in haystack for term in terms):
            results.append(
                {
                    "root": row[0],
                    "path": row[1],
                    "kind": row[2],
                    "size": row[3],
                    "modified_at": row[4],
                    "fingerprint": row[5],
                    "summary": row[6],
                    "indexed_at": row[7],
                }
            )
        if len(results) >= limit:
            break
    conn.close()
    return results


def project_inventory(limit=100):
    init_memory()
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT root, path, kind, size, modified_at, fingerprint, summary, indexed_at
        FROM project_files
        ORDER BY indexed_at DESC, path ASC
        LIMIT ?
        """,
        (limit,),
    )
    rows = [
        {
            "root": row[0],
            "path": row[1],
            "kind": row[2],
            "size": row[3],
            "modified_at": row[4],
            "fingerprint": row[5],
            "summary": row[6],
            "indexed_at": row[7],
        }
        for row in cur.fetchall()
    ]
    conn.close()
    return rows


def save_project_scan_snapshot(roots, max_files, query, records):
    init_memory()
    roots_list = [str(root) for root in roots]
    created_at = _now()
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO project_scan_snapshots
            (roots_key, roots_json, max_files, query, file_count, records_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            _roots_key(roots_list),
            _json(roots_list),
            int(max_files),
            query or "",
            len(records),
            _json(records),
            created_at,
        ),
    )
    snapshot_id = cur.lastrowid
    conn.commit()
    conn.close()
    return snapshot_id


def latest_project_scan_snapshot(roots, max_files, query=""):
    init_memory()
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, roots_json, max_files, query, file_count, records_json, created_at
        FROM project_scan_snapshots
        WHERE roots_key = ? AND max_files = ? AND query = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (_roots_key(roots), int(max_files), query or ""),
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row[0],
        "roots": json.loads(row[1]),
        "max_files": row[2],
        "query": row[3],
        "file_count": row[4],
        "records": json.loads(row[5]),
        "created_at": row[6],
    }


def save_project_monitor_checkin(
    snapshot_id,
    previous_snapshot_id,
    roots,
    status,
    summary,
    changes,
):
    init_memory()
    roots_list = [str(root) for root in roots]
    created_at = _now()
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO project_monitor_checkins
            (
                snapshot_id,
                previous_snapshot_id,
                roots_key,
                roots_json,
                status,
                summary_json,
                changes_json,
                created_at
            )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            int(snapshot_id),
            previous_snapshot_id,
            _roots_key(roots_list),
            _json(roots_list),
            status,
            _json(summary),
            _json(changes),
            created_at,
        ),
    )
    checkin_id = cur.lastrowid
    conn.commit()
    conn.close()
    return checkin_id


def recent_project_monitor_checkins(limit=10):
    init_memory()
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            id,
            snapshot_id,
            previous_snapshot_id,
            roots_json,
            status,
            summary_json,
            changes_json,
            created_at
        FROM project_monitor_checkins
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = [
        {
            "id": row[0],
            "snapshot_id": row[1],
            "previous_snapshot_id": row[2],
            "roots": json.loads(row[3]),
            "status": row[4],
            "summary": json.loads(row[5]),
            "changes": json.loads(row[6]),
            "created_at": row[7],
        }
        for row in cur.fetchall()
    ]
    conn.close()
    return rows
