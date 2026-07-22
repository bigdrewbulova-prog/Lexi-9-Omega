"""Write local project artifacts: Markdown, JSON, HTML + dashboard index."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = PROJECT_ROOT / "workspace"
DELIVERABLES = WORKSPACE / "deliverables"
DASHBOARD_DATA = WORKSPACE / "dashboard_data.json"


def slugify(text: str) -> str:
    clean = re.sub(r"[^a-zA-Z0-9]+", "_", (text or "").strip())
    return clean.strip("_")[:80] or "artifact"


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def ensure_dirs() -> None:
    DELIVERABLES.mkdir(parents=True, exist_ok=True)
    (WORKSPACE / "offers").mkdir(parents=True, exist_ok=True)
    (WORKSPACE / "plans").mkdir(parents=True, exist_ok=True)
    (WORKSPACE / "documentary").mkdir(parents=True, exist_ok=True)
    (WORKSPACE / "evals").mkdir(parents=True, exist_ok=True)
    (WORKSPACE / "termux").mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def write_json(path: Path, data: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=True), encoding="utf-8")
    return path


def write_bundle(
    kind: str,
    title: str,
    markdown: str,
    data: dict[str, Any],
    html: str | None = None,
    subdir: str | None = None,
) -> dict[str, str]:
    """Write MD + JSON (+ optional HTML) under workspace/deliverables."""
    ensure_dirs()
    stamp = utc_stamp()
    slug = slugify(title)
    base_dir = DELIVERABLES / (subdir or kind)
    base_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{stamp}-{slug}"

    paths: dict[str, str] = {}
    md_path = write_text(base_dir / f"{stem}.md", markdown)
    json_path = write_json(base_dir / f"{stem}.json", data)
    paths["markdown"] = str(md_path)
    paths["json"] = str(json_path)

    if html is not None:
        html_path = write_text(base_dir / f"{stem}.html", html)
        paths["html"] = str(html_path)

    _refresh_dashboard_index(kind=kind, title=title, paths=paths, data=data)
    return paths


def _refresh_dashboard_index(
    kind: str,
    title: str,
    paths: dict[str, str],
    data: dict[str, Any],
) -> None:
    ensure_dirs()
    index: dict[str, Any]
    if DASHBOARD_DATA.exists():
        try:
            index = json.loads(DASHBOARD_DATA.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            index = {}
    else:
        index = {}

    items = index.get("recent_deliverables", [])
    items.insert(
        0,
        {
            "kind": kind,
            "title": title,
            "paths": paths,
            "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "summary": data.get("summary") or data.get("slogan") or title,
        },
    )
    index["recent_deliverables"] = items[:30]
    index["updated_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    index["system"] = "Drewskii.Engine / Lexi-9-Omega"
    write_json(DASHBOARD_DATA, index)


def simple_html_page(title: str, body_html: str, badge: str = "DREWSKII.ENGINE") -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <style>
    :root {{ --bg:#050607; --paper:#e8e6dc; --acid:#c8ff35; --uv:#7b5cff; --muted:#8b948c; --line:rgba(232,230,220,.14); }}
    body {{ margin:0; background:var(--bg); color:var(--paper); font-family: system-ui,sans-serif; }}
    .wrap {{ max-width:880px; margin:0 auto; padding:32px 20px 60px; }}
    .badge {{ display:inline-block; font:11px ui-monospace,monospace; letter-spacing:.14em; color:var(--acid); border:1px solid rgba(200,255,53,.35); padding:6px 10px; border-radius:999px; }}
    h1 {{ letter-spacing:-.03em; margin:16px 0 8px; }}
    .muted {{ color:var(--muted); }}
    .card {{ border:1px solid var(--line); border-radius:14px; padding:18px; margin:14px 0; background:rgba(255,255,255,.03); }}
    h2 {{ font-size:14px; letter-spacing:.12em; text-transform:uppercase; color:var(--uv); }}
    pre, code {{ font-family: ui-monospace, monospace; }}
    ul {{ line-height:1.55; }}
    footer {{ margin-top:28px; font:11px ui-monospace,monospace; color:var(--muted); border-top:1px solid var(--line); padding-top:12px; }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="badge">{badge}</div>
    <h1>{title}</h1>
    {body_html}
    <footer>Local deliverable · inspectable · user-space only · not finished exotic hardware</footer>
  </div>
</body>
</html>
"""
