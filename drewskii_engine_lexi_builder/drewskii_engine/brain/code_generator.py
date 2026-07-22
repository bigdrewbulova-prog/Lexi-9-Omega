"""AI Brand Blueprint Pack generator + web dashboard shell."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .artifacts import (
    PROJECT_ROOT,
    WORKSPACE,
    ensure_dirs,
    simple_html_page,
    slugify,
    write_bundle,
    write_text,
)


def generate_ui_shell() -> Path:
    """Write / refresh the live web dashboard shell."""
    ensure_dirs()
    path = WORKSPACE / "lexi_dashboard.html"
    html = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Lexi-9-OMEGA · Drewskii.Engine Dashboard</title>
  <style>
    :root {
      --bg:#050607; --paper:#e8e6dc; --muted:#8b948c; --acid:#c8ff35; --uv:#7b5cff;
      --line:rgba(232,230,220,.14); --mono:ui-monospace,SFMono-Regular,monospace;
    }
    * { box-sizing:border-box; }
    body {
      margin:0; color:var(--paper); font-family:system-ui,sans-serif;
      background:
        radial-gradient(circle at 12% 0%, rgba(123,92,255,.16), transparent 40%),
        radial-gradient(circle at 90% 90%, rgba(200,255,53,.08), transparent 35%),
        var(--bg);
      min-height:100vh;
    }
    header, main { max-width:1100px; margin:0 auto; padding:24px 18px; }
    .eyebrow { font:11px var(--mono); letter-spacing:.18em; color:var(--acid); }
    h1 { margin:8px 0; letter-spacing:-.04em; font-size:clamp(28px,4vw,42px); }
    h1 span { color:var(--uv); }
    .lede { color:var(--muted); max-width:60ch; line-height:1.5; }
    .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:12px; margin:22px 0; }
    .card, .panel {
      border:1px solid var(--line); border-radius:16px; padding:16px;
      background:rgba(255,255,255,.03);
    }
    .card strong { display:block; margin-bottom:6px; }
    .card span, .muted { color:var(--muted); font-size:13px; line-height:1.45; }
    .panel h2 { margin:0 0 12px; font:11px var(--mono); letter-spacing:.14em; color:var(--muted); text-transform:uppercase; }
    table { width:100%; border-collapse:collapse; font-size:13px; }
    th, td { text-align:left; padding:8px 6px; border-top:1px solid var(--line); vertical-align:top; }
    th { color:var(--muted); font:10px var(--mono); letter-spacing:.1em; }
    .stamp {
      display:inline-block; margin-top:8px; font:9px var(--mono); letter-spacing:.12em;
      border:1px solid rgba(200,255,53,.35); color:var(--acid); padding:4px 8px; border-radius:999px;
    }
    button {
      border:1px solid var(--line); background:transparent; color:var(--paper);
      border-radius:10px; padding:10px 12px; font:10px var(--mono); letter-spacing:.12em; cursor:pointer;
    }
    button:hover { border-color:var(--acid); color:var(--acid); }
    .row { display:flex; flex-wrap:wrap; gap:8px; margin-top:12px; }
    footer { max-width:1100px; margin:0 auto; padding:8px 18px 40px; font:11px var(--mono); color:var(--muted); }
    code { color:var(--acid); }
  </style>
</head>
<body>
  <header>
    <div class="eyebrow">DREWSKII.ENGINE · LOCAL DASHBOARD SHELL</div>
    <h1>Lexi-9-<span>OMEGA</span></h1>
    <p class="lede">Inspectable builder surface for plans, brand blueprints, documentary/offer maps, eval logs, and Termux helper drafts. User-space only.</p>
    <div class="row">
      <button type="button" id="reload">RELOAD DATA</button>
      <button type="button" id="open-data">OPEN DATA PATH HINT</button>
    </div>
  </header>
  <main>
    <div class="grid" id="stats">
      <div class="card"><strong>Memory</strong><span id="s-memory">—</span></div>
      <div class="card"><strong>Plans</strong><span id="s-plans">—</span></div>
      <div class="card"><strong>Deliverables</strong><span id="s-deliverables">—</span></div>
      <div class="card"><strong>Eval logs</strong><span id="s-evals">—</span></div>
    </div>
    <section class="panel">
      <h2>Recent deliverables</h2>
      <div id="deliverables" class="muted">Load <code>workspace/dashboard_data.json</code> via local server or CLI refresh.</div>
    </section>
    <section class="panel" style="margin-top:14px">
      <h2>Safety stamps</h2>
      <div class="stamp">USER-SPACE FIRST</div>
      <div class="stamp">NO HIDDEN ACCESS</div>
      <div class="stamp">TERMUX = APPROVED ONLY</div>
      <div class="stamp">PHYSICS = SIM / LORE / VIZ</div>
    </section>
  </main>
  <footer>
    Serve this folder locally for live JSON load, e.g.
    <code>python3 -m http.server 8766</code> from <code>drewskii_engine/</code>
    then open <code>/workspace/lexi_dashboard.html</code>.
    Updated: <span id="updated">—</span>
  </footer>
  <script>
    async function loadData() {
      try {
        const res = await fetch('./dashboard_data.json', { cache: 'no-store' });
        if (!res.ok) throw new Error('missing dashboard_data.json');
        const data = await res.json();
        const items = data.recent_deliverables || [];
        document.getElementById('updated').textContent = data.updated_at || '—';
        document.getElementById('s-deliverables').textContent = String(items.length) + ' recent';
        document.getElementById('s-memory').textContent = (data.stats && data.stats.memory_keys) ?? 'see CLI stats';
        document.getElementById('s-plans').textContent = (data.stats && data.stats.plans) ?? 'see CLI stats';
        document.getElementById('s-evals').textContent = (data.stats && data.stats.eval_logs) ?? 'see CLI stats';
        if (!items.length) {
          document.getElementById('deliverables').textContent = 'No deliverables yet. Run: blueprint, plan, offer, documentary-map';
          return;
        }
        const rows = items.map(item => `
          <tr>
            <td>${item.kind || ''}</td>
            <td><strong>${item.title || ''}</strong><div class="muted">${item.summary || ''}</div></td>
            <td class="muted">${item.created_at || ''}</td>
          </tr>`).join('');
        document.getElementById('deliverables').innerHTML = `
          <table>
            <thead><tr><th>KIND</th><th>TITLE</th><th>CREATED</th></tr></thead>
            <tbody>${rows}</tbody>
          </table>`;
      } catch (err) {
        document.getElementById('deliverables').innerHTML =
          '<p class="muted">Could not load <code>dashboard_data.json</code>. Generate a deliverable via CLI, or open this page through a local static server from the <code>drewskii_engine</code> directory.</p>';
      }
    }
    document.getElementById('reload').onclick = loadData;
    document.getElementById('open-data').onclick = () => alert('Data file: workspace/dashboard_data.json (relative to this HTML).');
    loadData();
  </script>
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")
    return path


def _brand_pack_data(name: str, vibe: str = "", audience: str = "", offer: str = "") -> dict[str, Any]:
    clean = (name or "").strip() or "Custom AI Brand Blueprint Pack"
    vibe = vibe.strip() or "dark, clean, futuristic, premium"
    audience = audience.strip() or "creators, small businesses, and personal brands"
    offer = offer.strip() or "identity system: name, bio, slogan, visuals, ads"
    short = re.sub(r"[^A-Za-z0-9 ]+", "", clean).strip() or "Nova Signal"
    slogan = "Built from signal. Designed for impact."
    return {
        "kind": "brand_blueprint_pack",
        "title": clean,
        "brand_name": short if short.lower() != "custom ai brand blueprint pack" else "NOVA THREAD",
        "slogan": slogan,
        "bio": (
            f"{clean} turns a raw idea into a professional identity with brand direction, "
            f"visual language, ad copy, and launch-ready positioning for {audience}."
        ),
        "vibe": vibe,
        "audience": audience,
        "offer": offer,
        "price_starting_usd": 50,
        "cta": "BLUEPRINT",
        "image_prompts": [
            f"Cinematic brand poster for {clean}, black void, white blueprint lines, ultraviolet glow, glass UI cards, premium AI builder aesthetic, no text",
            f"Minimal logo mark concept for {clean}, geometric, high contrast, blueprint grid, ultraviolet accent",
            f"Social ad still for {clean}, split before/after brand chaos to clean system, documentary lighting",
        ],
        "ad_copy": {
            "primary": (
                f"Your idea deserves to look official. Custom AI Brand Blueprint Packs for "
                f"businesses, music pages, gaming brands, clothing ideas, AI characters, and personal projects.\n\n"
                f"Starting at $50. Message BLUEPRINT to start."
            ),
            "headlines": [
                slogan,
                "Stop looking unfinished.",
                "Your brand, one page, delivered.",
            ],
        },
        "concept_sheet": {
            "project_type": "brand identity pack",
            "audience": audience,
            "offer": offer,
            "vibe": vibe,
            "colors": "void black · blueprint white · ultraviolet · acid green accents",
            "next_action": "Review draft, adjust audience/offer, export PDF/PNG for customer.",
        },
        "summary": f"$50 Brand Blueprint Pack draft for {clean}",
        "boundaries": [
            "Customer-facing identity pack only",
            "Not a claim of finished AGI or exotic hardware",
        ],
    }


def generate_brand_blueprint(
    name: str = "Lexi.AI Brand Blueprint Pack",
    vibe: str = "",
    audience: str = "",
    offer: str = "",
    memory=None,
) -> dict[str, Any]:
    """Generate multi-format Brand Blueprint Pack (MD, JSON, HTML)."""
    ensure_dirs()
    data = _brand_pack_data(name, vibe=vibe, audience=audience, offer=offer)

    md = f"""# AI Brand Blueprint Pack: {data['title']}

**Price point:** Starting at ${data['price_starting_usd']}  
**CTA:** {data['cta']}

## Brand name
{data['brand_name']}

## Slogan
{data['slogan']}

## Short bio
{data['bio']}

## Vibe
{data['vibe']}

## Audience
{data['audience']}

## Offer
{data['offer']}

## Image prompts
"""
    for i, prompt in enumerate(data["image_prompts"], 1):
        md += f"{i}. `{prompt}`\n"

    md += f"""
## Ad copy

### Primary
{data['ad_copy']['primary']}

### Headlines
"""
    for h in data["ad_copy"]["headlines"]:
        md += f"- {h}\n"

    cs = data["concept_sheet"]
    md += f"""
## One-page concept sheet
- Project type: {cs['project_type']}
- Audience: {cs['audience']}
- Offer: {cs['offer']}
- Vibe: {cs['vibe']}
- Colors: {cs['colors']}
- Next action: {cs['next_action']}

## Delivery notes
Review this draft, adjust audience and offer, then export as PDF/image for the customer.

## Boundaries
"""
    for b in data["boundaries"]:
        md += f"- {b}\n"

    body = f"""
    <p class="muted">{data['bio']}</p>
    <div class="card"><h2>Slogan</h2><p>{data['slogan']}</p></div>
    <div class="card"><h2>Audience</h2><p>{data['audience']}</p></div>
    <div class="card"><h2>Offer</h2><p>{data['offer']}</p></div>
    <div class="card"><h2>CTA</h2><p>Message <strong>{data['cta']}</strong> · from ${data['price_starting_usd']}</p></div>
    <div class="card"><h2>Image prompts</h2><ul>{''.join(f'<li>{p}</li>' for p in data['image_prompts'])}</ul></div>
    """
    html = simple_html_page(f"Brand Blueprint · {data['brand_name']}", body, badge="BRAND BLUEPRINT PACK")

    paths = write_bundle(
        kind="brand_blueprint",
        title=data["title"],
        markdown=md,
        data=data,
        html=html,
        subdir="blueprints",
    )

    result = {"title": data["title"], "paths": paths, "data": data}
    if memory is not None:
        did = memory.save_deliverable("brand_blueprint", data["title"], paths, meta={"price": 50})
        result["deliverable_id"] = did
    return result


# Back-compat for callers expecting a Path
def generate_brand_blueprint_path(name: str = "Lexi.AI Brand Blueprint Pack") -> Path:
    result = generate_brand_blueprint(name)
    return Path(result["paths"]["markdown"])
