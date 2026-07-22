"""Termux / Android helpers — user-approved commands only.

Never auto-executes on device from this module. Generates reviewable scripts
and command cards the user can run inside Termux after explicit approval.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from brain.artifacts import WORKSPACE, ensure_dirs, utc_stamp, write_json, write_text


# Catalog of safe, permission-based helpers. No root, no surveillance, no bypass.
APPROVED_HELPERS: dict[str, dict[str, Any]] = {
    "tts": {
        "title": "Speak text (TTS)",
        "requires": ["termux-api", "user approval"],
        "command": 'termux-tts-speak "Lexi online. Architecture locked."',
        "notes": "Uses Termux:API text-to-speech after user install/permission.",
    },
    "vibrate": {
        "title": "Vibrate device",
        "requires": ["termux-api", "user approval"],
        "command": "termux-vibrate -d 200",
        "notes": "Short haptic confirmation only.",
    },
    "notify": {
        "title": "Local notification",
        "requires": ["termux-api", "notification permission", "user approval"],
        "command": 'termux-notification --title "Lexi.AI" --content "Blueprint ready for review."',
        "notes": "Local notification; not background surveillance.",
    },
    "battery": {
        "title": "Battery status",
        "requires": ["termux-api", "user approval"],
        "command": "termux-battery-status",
        "notes": "Public diagnostic via Termux:API.",
    },
    "clipboard_get": {
        "title": "Read clipboard (explicit)",
        "requires": ["termux-api", "user approval"],
        "command": "termux-clipboard-get",
        "notes": "Only when user runs it; do not poll in background.",
    },
    "share_file": {
        "title": "Share a local file via Android intent",
        "requires": ["termux-api", "user approval", "existing file path"],
        "command": 'termux-share -a send "/data/data/com.termux/files/home/blueprint.md"',
        "notes": "Replace path with a user-selected file. Official share sheet only.",
    },
    "open_url": {
        "title": "Open URL in browser",
        "requires": ["user approval"],
        "command": 'termux-open-url "https://example.com"',
        "notes": "User-space intent to default browser.",
    },
}


BLOCKED_PATTERNS = [
    "hidden surveillance",
    "password collection",
    "security bypass",
    "root",
    "systemui implant",
    "background spy",
    "keylogger",
    "account takeover",
]


def list_helpers() -> list[dict[str, Any]]:
    return [
        {"id": key, **value}
        for key, value in APPROVED_HELPERS.items()
    ]


def prepare_helper(helper_id: str, *, approved: bool = False) -> dict[str, Any]:
    """Prepare a helper script for review. Does not execute on device."""
    key = helper_id.strip().lower()
    if key not in APPROVED_HELPERS:
        raise ValueError(
            f"Unknown helper '{helper_id}'. Available: {', '.join(sorted(APPROVED_HELPERS))}"
        )
    if not approved:
        raise PermissionError(
            "Owner approval required. Re-run with approved=True after reviewing the command."
        )

    ensure_dirs()
    helper = APPROVED_HELPERS[key]
    stamp = utc_stamp()
    script_path = WORKSPACE / "termux" / f"{stamp}-{key}.sh"
    meta_path = WORKSPACE / "termux" / f"{stamp}-{key}.json"

    script = f"""#!/data/data/com.termux/files/usr/bin/bash
# Drewskii.Engine Termux helper — USER APPROVED DRAFT
# Helper: {helper['title']}
# Review before running. This file was generated on the Mac builder; it is not auto-executed.

set -euo pipefail
echo "[Lexi] Preparing: {helper['title']}"
echo "[Lexi] Requires: {', '.join(helper['requires'])}"
{helper['command']}
echo "[Lexi] Done."
"""
    write_text(script_path, script)
    meta = {
        "id": key,
        "title": helper["title"],
        "command": helper["command"],
        "requires": helper["requires"],
        "notes": helper["notes"],
        "script_path": str(script_path),
        "execution": "manual_in_termux_only",
        "auto_execute_from_mac": False,
        "blocked": BLOCKED_PATTERNS,
    }
    write_json(meta_path, meta)
    return meta


def helpers_markdown() -> str:
    lines = [
        "# Termux Helpers (User-Approved Only)",
        "",
        "These commands are drafts for Termux on-device execution after explicit user approval.",
        "The Mac builder never auto-runs them against a phone.",
        "",
    ]
    for item in list_helpers():
        lines += [
            f"## `{item['id']}` — {item['title']}",
            f"- Command: `{item['command']}`",
            f"- Requires: {', '.join(item['requires'])}",
            f"- Notes: {item['notes']}",
            "",
        ]
    lines += [
        "## Blocked",
        "- Hidden surveillance, password collection, security bypass",
        "- Root / SystemUI implants / OS control outside official APIs",
        "",
    ]
    return "\n".join(lines)
