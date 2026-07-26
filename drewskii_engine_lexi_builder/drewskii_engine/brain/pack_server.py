"""
Local Stage-2 slice: guided Brand Pack intake → generate → download ZIP
+ local pack library (history / re-download).

stdlib only. User-space. No cloud. No payments.
  stack serve  →  http://127.0.0.1:8787
  /            form
  /library     pack history
  /api/packs   JSON list
"""
from __future__ import annotations

import json
import mimetypes
import re
import traceback
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

from .artifacts import DELIVERABLES, PROJECT_ROOT, WORKSPACE, ensure_dirs
from .intelligence_stack import BrandIntake, LocalFirstIntelligenceStack
from .logger import log_event
from .memory import Memory
from .safety import is_blocked


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8787
FORM_HTML = PROJECT_ROOT / "workspace" / "dashboard" / "brand_intake.html"
PACKAGES_DIR = DELIVERABLES / "blueprints" / "packages"
_ZIP_NAME_RE = re.compile(
    r"^(?P<stamp>\d{8}-\d{6})-(?P<label>.+)-brand-pack\.zip$",
    re.IGNORECASE,
)


def _stack() -> LocalFirstIntelligenceStack:
    ensure_dirs()
    return LocalFirstIntelligenceStack(
        memory=Memory(PROJECT_ROOT / "memory" / "drewskii_memory.db")
    )


def _safe_deliverable_path(raw: str) -> Path | None:
    """Resolve a download path and ensure it stays under workspace/deliverables."""
    file_path = Path(unquote(raw)).expanduser()
    if not file_path.is_absolute():
        file_path = (WORKSPACE / file_path).resolve()
    else:
        file_path = file_path.resolve()
    allowed_root = (WORKSPACE / "deliverables").resolve()
    try:
        file_path.relative_to(allowed_root)
    except ValueError:
        return None
    return file_path


def list_brand_packs(limit: int = 50) -> list[dict[str, Any]]:
    """
    Local pack library: filesystem ZIPs under deliverables/blueprints/packages,
    enriched with SQLite deliverable rows when available.
    """
    ensure_dirs()
    PACKAGES_DIR.mkdir(parents=True, exist_ok=True)

    by_zip: dict[str, dict[str, Any]] = {}

    # Memory first so titles / meta win when present
    try:
        mem = Memory(PROJECT_ROOT / "memory" / "drewskii_memory.db")
        for row in mem.recent_deliverables(limit=100):
            if row.get("kind") not in {"brand_blueprint", "brand_pack", "blueprint"}:
                continue
            paths = row.get("paths") or {}
            zip_path = paths.get("zip") or ""
            if not zip_path:
                continue
            p = Path(zip_path)
            if not p.is_file():
                continue
            key = str(p.resolve())
            by_zip[key] = {
                "id": row.get("id"),
                "brand_name": row.get("title") or _brand_from_zip_name(p.name),
                "filename": p.name,
                "zip": str(p),
                "download_url": f"/download/{p}",
                "size_bytes": p.stat().st_size,
                "created_at": row.get("created_at"),
                "source": "sqlite+fs",
                "meta": row.get("meta") or {},
                "paths": paths,
            }
    except Exception as exc:
        log_event(f"pack_library_memory_skip: {exc}")

    # Filesystem scan fills gaps and pure ZIP deliveries
    for p in sorted(PACKAGES_DIR.glob("*-brand-pack.zip"), key=lambda x: x.stat().st_mtime, reverse=True):
        if not p.is_file():
            continue
        key = str(p.resolve())
        if key in by_zip:
            continue
        stamp, label = _parse_zip_name(p.name)
        mtime = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).replace(microsecond=0)
        by_zip[key] = {
            "id": None,
            "brand_name": label,
            "filename": p.name,
            "zip": str(p),
            "download_url": f"/download/{p}",
            "size_bytes": p.stat().st_size,
            "created_at": mtime.isoformat(),
            "source": "fs",
            "meta": {"stamp": stamp},
            "paths": {"zip": str(p)},
        }

    items = list(by_zip.values())
    items.sort(key=lambda r: r.get("created_at") or "", reverse=True)
    return items[: max(1, min(limit, 200))]


def _parse_zip_name(name: str) -> tuple[str | None, str]:
    m = _ZIP_NAME_RE.match(name)
    if not m:
        return None, name.removesuffix(".zip")
    label = m.group("label").replace("_", " ").strip() or name
    return m.group("stamp"), label


def _brand_from_zip_name(name: str) -> str:
    return _parse_zip_name(name)[1]


class PackHandler(BaseHTTPRequestHandler):
    server_version = "LexiPackServer/1.1"

    def log_message(self, fmt: str, *args: Any) -> None:
        # quieter than default stderr spam
        print(f"[pack-server] {self.address_string()} {fmt % args}")

    def _send(self, code: int, body: bytes, content_type: str = "text/html; charset=utf-8") -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, code: int, payload: dict[str, Any]) -> None:
        data = json.dumps(payload, indent=2, ensure_ascii=True).encode("utf-8")
        self._send(code, data, "application/json; charset=utf-8")

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path in {"/", "/index.html", "/intake"}:
            html = _render_form()
            self._send(200, html.encode("utf-8"))
            return

        if path in {"/library", "/packs", "/history"}:
            self._send(200, _render_library().encode("utf-8"))
            return

        if path == "/api/health":
            packs = list_brand_packs(limit=5)
            self._send_json(
                200,
                {
                    "ok": True,
                    "service": "lexi-brand-pack-intake",
                    "stage": 1,
                    "product": "Custom AI Brand Blueprint Packs",
                    "price_starting_usd": 50,
                    "library_count": len(list_brand_packs(limit=200)),
                    "recent_pack": packs[0]["brand_name"] if packs else None,
                    "endpoints": [
                        "GET /",
                        "GET /library",
                        "GET /api/health",
                        "GET /api/packs",
                        "POST /api/pack",
                        "GET /download/<path>",
                    ],
                },
            )
            return

        if path == "/api/packs":
            qs = parse_qs(parsed.query or "")
            try:
                limit = int((qs.get("limit") or ["50"])[0])
            except ValueError:
                limit = 50
            items = list_brand_packs(limit=limit)
            self._send_json(
                200,
                {
                    "ok": True,
                    "count": len(items),
                    "packs": items,
                    "packages_dir": str(PACKAGES_DIR),
                    "stage": 1,
                },
            )
            return

        if path.startswith("/download/"):
            raw = path[len("/download/") :]
            file_path = _safe_deliverable_path(raw)
            if file_path is None:
                self._send_json(403, {"error": "Download path outside deliverables workspace."})
                return
            if not file_path.is_file():
                self._send_json(404, {"error": "File not found."})
                return
            data = file_path.read_bytes()
            ctype = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.send_header(
                "Content-Disposition",
                f'attachment; filename="{file_path.name}"',
            )
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)
            return

        self._send_json(404, {"error": "Not found", "path": path})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/pack":
            self._send_json(404, {"error": "Not found"})
            return

        length = int(self.headers.get("Content-Length", "0") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        content_type = (self.headers.get("Content-Type") or "").lower()

        try:
            if "application/json" in content_type:
                payload = json.loads(raw.decode("utf-8") or "{}")
            else:
                # form-urlencoded
                form = parse_qs(raw.decode("utf-8"), keep_blank_values=True)
                payload = {k: (v[0] if v else "") for k, v in form.items()}
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            self._send_json(400, {"error": f"Bad request body: {exc}"})
            return

        intake = BrandIntake(
            project_type=(payload.get("project_type") or "personal brand").strip(),
            name=(payload.get("name") or "").strip(),
            vibe=(payload.get("vibe") or "").strip(),
            audience=(payload.get("audience") or "").strip(),
            offer=(payload.get("offer") or "").strip(),
            colors=(payload.get("colors") or "void black · blueprint white · ultraviolet").strip(),
        )

        if is_blocked(json.dumps(intake.to_dict())):
            self._send_json(403, {"error": "Intake blocked by safety rules."})
            return

        try:
            stack = _stack()
            out = stack.brand_pack(intake, include_code=True)
        except ValueError as exc:
            self._send_json(400, {"error": str(exc)})
            return
        except Exception as exc:
            log_event(f"pack_server_error: {exc}")
            self._send_json(
                500,
                {
                    "error": "Pack generation failed.",
                    "detail": str(exc),
                    "trace": traceback.format_exc().splitlines()[-3:],
                },
            )
            return

        zip_path = out.get("zip") or ""
        download = ""
        if zip_path:
            # Serve via absolute path under /download/
            download = f"/download/{zip_path}"

        # HTML form posts expect redirect-friendly HTML response optional
        accept = (self.headers.get("Accept") or "").lower()
        wants_html = "text/html" in accept and "application/json" not in accept

        result = {
            "ok": True,
            "brand_name": out["pack"]["data"].get("brand_name"),
            "slogan": out["pack"]["data"].get("slogan"),
            "quality_checklist": out["quality_checklist"],
            "zip": zip_path,
            "download_url": download,
            "paths": out["pack"]["paths"],
            "delivery": out.get("delivery"),
            "price_starting_usd": 50,
            "cta": "BLUEPRINT",
            "stage": 1,
        }

        if wants_html or payload.get("format") == "html":
            html = _render_result(result)
            self._send(200, html.encode("utf-8"))
            return

        self._send_json(200, result)


def _render_form() -> str:
    ensure_dirs()
    FORM_HTML.parent.mkdir(parents=True, exist_ok=True)
    if not FORM_HTML.exists():
        FORM_HTML.write_text(_default_form_html(), encoding="utf-8")
    return FORM_HTML.read_text(encoding="utf-8")


def _render_result(result: dict[str, Any]) -> str:
    checklist = result.get("quality_checklist") or {}
    zip_path = result.get("zip") or ""
    dl = result.get("download_url") or "#"
    passed = checklist.get("passed")
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Pack ready — {result.get('brand_name')}</title>
<style>
:root{{--ink:#080b0a;--paper:#e7e5dc;--acid:#c8ff35;--muted:#8e958d;--line:rgba(231,229,220,.16)}}
body{{margin:0;font-family:system-ui,sans-serif;background:var(--ink);color:var(--paper);padding:40px 20px}}
.card{{max-width:640px;margin:0 auto;border:1px solid var(--line);border-radius:16px;padding:28px;background:rgba(255,255,255,.03)}}
h1{{letter-spacing:-.04em}} .muted{{color:var(--muted)}} a.btn{{display:inline-block;margin-top:16px;background:var(--acid);color:#111;text-decoration:none;font:700 12px ui-monospace,monospace;padding:14px 18px;border-radius:10px}}
a.ghost{{display:inline-block;margin:16px 12px 0 0;color:var(--paper);border:1px solid var(--line);padding:12px 14px;border-radius:10px;text-decoration:none;font:11px ui-monospace,monospace}}
.ok{{color:var(--acid)}} .bad{{color:#ff5c35}} code{{color:var(--acid);font-size:12px;word-break:break-all}}
</style></head><body><div class="card">
<div class="muted" style="font:11px ui-monospace,monospace;letter-spacing:.14em">LEXI · BRAND PACK · STAGE 1</div>
<h1>{result.get('brand_name')}</h1>
<p class="muted">{result.get('slogan') or ''}</p>
<p>Quality checklist: <strong class="{'ok' if passed else 'bad'}">{'PASSED' if passed else 'FAILED'}</strong></p>
<p class="muted">Starting at $50 · CTA: BLUEPRINT</p>
{'<a class="btn" href="'+dl+'">Download ZIP package →</a>' if zip_path else '<p class="bad">ZIP missing</p>'}
<p style="margin-top:20px">
  <a class="ghost" href="/">← New pack</a>
  <a class="ghost" href="/library">Pack library</a>
</p>
<p class="muted" style="margin-top:24px;font-size:12px">Saved under workspace deliverables (local only).</p>
<p><code>{zip_path}</code></p>
</div></body></html>"""


def _render_library() -> str:
    items = list_brand_packs(limit=50)
    rows = []
    for it in items:
        size_kb = max(1, int((it.get("size_bytes") or 0) / 1024))
        name = (it.get("brand_name") or "Untitled").replace("<", "&lt;")
        created = (it.get("created_at") or "—").replace("T", " ").replace("+00:00", " UTC")
        src = it.get("source") or "fs"
        dl = it.get("download_url") or "#"
        fn = (it.get("filename") or "").replace("<", "&lt;")
        rows.append(
            f"""<tr>
  <td><strong>{name}</strong><div class="muted file">{fn}</div></td>
  <td class="muted">{created}</td>
  <td class="muted">{size_kb} KB</td>
  <td class="muted">{src}</td>
  <td><a class="dl" href="{dl}">Download</a></td>
</tr>"""
        )
    body_rows = "\n".join(rows) if rows else (
        '<tr><td colspan="5" class="muted">No packs yet. '
        '<a href="/" style="color:var(--acid)">Generate one →</a></td></tr>'
    )
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Pack library — Lexi</title>
<style>
:root{{--ink:#080b0a;--paper:#e7e5dc;--acid:#c8ff35;--muted:#8e958d;--line:rgba(231,229,220,.16);--mono:ui-monospace,SFMono-Regular,monospace}}
*{{box-sizing:border-box}}
body{{margin:0;font-family:system-ui,sans-serif;background:var(--ink);color:var(--paper);
background-image:linear-gradient(rgba(255,255,255,.02) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.02) 1px,transparent 1px);background-size:40px 40px}}
.wrap{{max-width:920px;margin:0 auto;padding:48px 20px 80px}}
.badge{{display:inline-block;font:11px var(--mono);letter-spacing:.16em;color:var(--acid);border:1px solid rgba(200,255,53,.4);padding:6px 10px;border-radius:999px}}
h1{{font-size:clamp(28px,4vw,40px);letter-spacing:-.04em;margin:16px 0 8px}}
h1 span{{color:var(--acid)}}
.lede{{color:var(--muted);line-height:1.55;margin-bottom:20px}}
.nav a{{color:var(--paper);text-decoration:none;border:1px solid var(--line);padding:10px 12px;border-radius:10px;font:11px var(--mono);margin-right:8px;display:inline-block}}
.nav a:hover,.nav a.active{{border-color:var(--acid);color:var(--acid)}}
.muted{{color:var(--muted)}} .file{{font:11px var(--mono);margin-top:4px;word-break:break-all}}
table{{width:100%;border-collapse:collapse;margin-top:24px;font-size:14px}}
th,td{{text-align:left;padding:12px 8px;border-top:1px solid var(--line);vertical-align:top}}
th{{font:10px var(--mono);letter-spacing:.12em;color:var(--muted)}}
a.dl{{color:#111;background:var(--acid);text-decoration:none;font:700 11px var(--mono);padding:8px 10px;border-radius:8px;display:inline-block}}
.meta{{margin-top:20px;font:11px var(--mono);color:var(--muted)}}
</style></head><body><div class="wrap">
<div class="badge">STAGE 1 · LOCAL LIBRARY · USER-SPACE</div>
<h1>Pack <span>library</span></h1>
<p class="lede">History of customer Brand Blueprint ZIPs on this machine. Re-download anytime. No cloud.</p>
<div class="nav">
  <a href="/">New pack</a>
  <a class="active" href="/library">Library</a>
  <a href="/api/packs">JSON API</a>
</div>
<table>
  <thead><tr><th>BRAND</th><th>CREATED</th><th>SIZE</th><th>SOURCE</th><th></th></tr></thead>
  <tbody>
{body_rows}
  </tbody>
</table>
<p class="meta">{len(items)} pack(s) · {PACKAGES_DIR} · GET /api/packs</p>
</div></body></html>"""


def _default_form_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Lexi · Brand Blueprint Intake</title>
  <style>
    :root {
      --ink: #080b0a; --paper: #e7e5dc; --acid: #c8ff35; --muted: #8e958d;
      --line: rgba(231,229,220,.16); --mono: ui-monospace, SFMono-Regular, monospace;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0; min-height: 100vh; font-family: system-ui, sans-serif;
      background: var(--ink); color: var(--paper);
      background-image:
        linear-gradient(rgba(255,255,255,.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,.02) 1px, transparent 1px);
      background-size: 40px 40px;
    }
    .wrap { max-width: 640px; margin: 0 auto; padding: 48px 20px 80px; }
    .badge {
      display: inline-block; font: 11px var(--mono); letter-spacing: .16em;
      color: var(--acid); border: 1px solid rgba(200,255,53,.4);
      padding: 6px 10px; border-radius: 999px;
    }
    h1 { font-size: clamp(32px, 5vw, 44px); letter-spacing: -.04em; margin: 16px 0 8px; }
    h1 span { color: var(--acid); }
    .lede { color: var(--muted); line-height: 1.55; margin-bottom: 28px; }
    label { display: block; font: 10px var(--mono); letter-spacing: .14em; color: var(--muted); margin: 16px 0 8px; }
    input, select, textarea {
      width: 100%; background: #0b0e0c; border: 1px solid var(--line); color: var(--paper);
      border-radius: 10px; padding: 12px 14px; font: 15px system-ui, sans-serif;
    }
    textarea { min-height: 72px; resize: vertical; }
    button {
      margin-top: 28px; width: 100%; border: 0; border-radius: 12px; padding: 16px;
      background: var(--acid); color: #111; font: 800 12px var(--mono); letter-spacing: .12em;
      cursor: pointer;
    }
    button:disabled { opacity: .55; cursor: wait; }
    .price { margin-top: 12px; font: 11px var(--mono); color: var(--muted); }
    .foot { margin-top: 32px; font: 11px var(--mono); color: var(--muted); line-height: 1.5; }
    .err { color: #ff5c35; font: 12px var(--mono); margin-top: 12px; display: none; }
    .nav { margin: 0 0 24px; }
    .nav a {
      color: var(--paper); text-decoration: none; border: 1px solid var(--line);
      padding: 10px 12px; border-radius: 10px; font: 11px var(--mono);
      margin-right: 8px; display: inline-block;
    }
    .nav a:hover, .nav a.active { border-color: var(--acid); color: var(--acid); }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="badge">STAGE 1 · LOCAL INTAKE · USER-SPACE</div>
    <h1>Brand Blueprint <span>Pack</span></h1>
    <p class="lede">
      Guided intake for Lexi-9-Omega Custom AI Brand Blueprint Packs.
      Generates local MD/JSON/HTML + a customer ZIP. No cloud required.
    </p>
    <div class="nav">
      <a class="active" href="/">New pack</a>
      <a href="/library">Pack library</a>
      <a href="/api/packs">JSON API</a>
    </div>

    <form id="pack-form" method="post" action="/api/pack" accept-charset="utf-8">
      <input type="hidden" name="format" value="html" />

      <label for="project_type">PROJECT TYPE</label>
      <select id="project_type" name="project_type">
        <option value="personal brand">Personal brand</option>
        <option value="music page">Music page</option>
        <option value="gaming brand">Gaming brand</option>
        <option value="clothing">Clothing</option>
        <option value="small business">Small business</option>
        <option value="AI character">AI character</option>
        <option value="AI product" selected>AI product</option>
      </select>

      <label for="name">BRAND / PROJECT NAME *</label>
      <input id="name" name="name" required maxlength="120" placeholder="e.g. Nova Thread" />

      <label for="vibe">VIBE *</label>
      <input id="vibe" name="vibe" required maxlength="500" placeholder="dark, clean, futuristic, premium" value="dark, clean, futuristic" />

      <label for="audience">AUDIENCE *</label>
      <input id="audience" name="audience" required maxlength="500" placeholder="who is this for?" value="creators and small businesses" />

      <label for="offer">OFFER *</label>
      <textarea id="offer" name="offer" required maxlength="500" placeholder="what do you sell or share?">Custom AI Brand Blueprint Packs starting at $50</textarea>

      <label for="colors">COLORS</label>
      <input id="colors" name="colors" maxlength="500" value="void black · blueprint white · ultraviolet · acid green" />

      <button type="submit" id="submit">GENERATE PACK →</button>
      <p class="price">Starting at $50 · CTA: BLUEPRINT · Local only · Quality checklist enforced</p>
      <p class="err" id="err"></p>
    </form>

    <p class="foot">
      Promotion gate still applies before native app / payments.
      Speculative physics claims are not product features.
      API: <code>POST /api/pack</code> · Library: <code>GET /library</code> ·
      List: <code>GET /api/packs</code> · Health: <code>GET /api/health</code>
    </p>
  </div>
  <script>
    const form = document.getElementById('pack-form');
    const btn = document.getElementById('submit');
    const err = document.getElementById('err');
    form.addEventListener('submit', () => {
      btn.disabled = true;
      btn.textContent = 'GENERATING…';
      err.style.display = 'none';
    });
  </script>
</body>
</html>
"""


def serve(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    ensure_dirs()
    PACKAGES_DIR.mkdir(parents=True, exist_ok=True)
    FORM_HTML.parent.mkdir(parents=True, exist_ok=True)
    if not FORM_HTML.exists():
        FORM_HTML.write_text(_default_form_html(), encoding="utf-8")
    httpd = ThreadingHTTPServer((host, port), PackHandler)
    print("Lexi Brand Pack intake + library server")
    print(f"  Guided form:  http://{host}:{port}/")
    print(f"  Pack library: http://{host}:{port}/library")
    print(f"  API health:   http://{host}:{port}/api/health")
    print(f"  List packs:   http://{host}:{port}/api/packs")
    print(f"  POST pack:    http://{host}:{port}/api/pack")
    print("  Ctrl+C to stop")
    log_event(f"pack_server_start {host}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nPack server stopped.")
        log_event("pack_server_stop")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    serve()
