"""Evaluation logs for prompts, templates, and generated deliverables."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .artifacts import WORKSPACE, ensure_dirs, write_json
from .logger import log_event


def log_evaluation(
    memory,
    category: str,
    subject: str,
    notes: str,
    score: float | None = None,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Write eval to SQLite + JSONL + project log."""
    ensure_dirs()
    eval_id = memory.log_eval(category, subject, notes, score=score, payload=payload)
    record = {
        "id": eval_id,
        "category": category,
        "subject": subject,
        "score": score,
        "notes": notes,
        "payload": payload or {},
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }

    jsonl = WORKSPACE / "evals" / "evaluations.jsonl"
    jsonl.parent.mkdir(parents=True, exist_ok=True)
    with jsonl.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=True) + "\n")

    # Keep a rolling latest snapshot for the dashboard
    write_json(WORKSPACE / "evals" / "latest.json", record)
    log_event(f"eval[{category}] {subject}: {notes}" + (f" score={score}" if score is not None else ""))
    return record
