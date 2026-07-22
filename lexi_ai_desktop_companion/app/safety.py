from __future__ import annotations

import re
from pathlib import Path


RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "COM5",
    "COM6",
    "COM7",
    "COM8",
    "COM9",
    "LPT1",
    "LPT2",
    "LPT3",
    "LPT4",
    "LPT5",
    "LPT6",
    "LPT7",
    "LPT8",
    "LPT9",
}


def slugify_project_name(name: str) -> str:
    raw = (name or "").strip().lower()
    raw = re.sub(r"[^a-z0-9._ -]+", "", raw)
    raw = re.sub(r"[\s.]+", "-", raw)
    raw = re.sub(r"-+", "-", raw).strip("-_.")

    if not raw:
        raw = "untitled-project"

    if raw.upper() in RESERVED_NAMES:
        raw = f"{raw}-project"

    return raw[:80]


def validate_project_name(name: str) -> tuple[bool, str]:
    if not name or not name.strip():
        return False, "Project name is required."

    if len(name.strip()) > 120:
        return False, "Project name is too long. Keep it under 120 characters."

    dangerous = ["..", "/", "\\", ":", "*", "?", '"', "<", ">", "|"]
    for token in dangerous:
        if token in name:
            return False, f"Project name cannot contain: {token}"

    return True, "Project name accepted."


def safe_join(root: Path, *parts: str) -> Path:
    root = root.expanduser().resolve()
    candidate = root.joinpath(*parts).expanduser().resolve()

    if root != candidate and root not in candidate.parents:
        raise ValueError("Blocked unsafe path traversal outside the workspace root.")

    return candidate


def is_probably_destructive_instruction(text: str) -> bool:
    lowered = (text or "").lower()
    destructive_patterns = [
        r"\bdelete\b",
        r"\berase\b",
        r"\bwipe\b",
        r"\bformat\b",
        r"\brm\s+-rf\b",
        r"\bdrop\s+table\b",
        r"\boverwrite\b",
        r"\bdisable\s+security\b",
        r"\bbypass\b",
    ]

    return any(re.search(pattern, lowered) for pattern in destructive_patterns)
