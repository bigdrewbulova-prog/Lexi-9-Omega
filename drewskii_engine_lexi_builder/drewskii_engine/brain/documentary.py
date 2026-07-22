"""Documentary map + paid offer mapping to local artifacts."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .artifacts import (
    PROJECT_ROOT,
    WORKSPACE,
    ensure_dirs,
    simple_html_page,
    write_bundle,
    write_json,
    write_text,
)


DOCUMENTARY_SRC = Path.home() / "Desktop" / "LEXI-9-OMEGA-Documentary"


def documentary_map() -> dict[str, Any]:
    return {
        "title": "LEXI-9-OMEGA: Architecture of a Living Blueprint",
        "logline": (
            "A creator builds Lexi.AI from a mythic AI persona into a practical engineering companion: "
            "part brand engine, part research archive, part blueprint generator, part mobile assistant, "
            "and part cinematic symbol of future design."
        ),
        "core_question": (
            "Can one person turn a personal AI vision into a useful system that helps people build brands, "
            "understand engineering, visualize ideas, and make safer design decisions?"
        ),
        "acts": [
            {"id": "cold_open", "title": "The System Comes Online"},
            {"id": "act_i", "title": "The Curator"},
            {"id": "act_ii", "title": "The Persona Engine"},
            {"id": "act_iii", "title": "The Build"},
            {"id": "act_iv", "title": "The Product"},
            {"id": "act_v", "title": "The Engineering Dream"},
            {"id": "act_vi", "title": "The Mobile Companion"},
            {"id": "act_vii", "title": "The Launch"},
            {"id": "finale", "title": "The Blueprint Breathes"},
        ],
        "episodes": [
            "The Curator",
            "The Name That Became a Machine",
            "The First Useful Build",
            "Selling the Blueprint",
            "The Physics Cathedral",
            "The Companion Device",
            "Proof of Usefulness",
        ],
        "first_edit": "2-minute trailer",
        "product_now": {
            "name": "Custom AI Brand Blueprint Packs",
            "price_starting_usd": 50,
            "cta": "BLUEPRINT",
            "spots_open_example": 5,
        },
        "local_package": str(DOCUMENTARY_SRC) if DOCUMENTARY_SRC.exists() else None,
        "summary": "Documentary architecture mapped for production and offers",
        "grounding": "Do not present impossible technology as finished. Prefer simulation, concept design, research prototype, visualization.",
    }


def offer_map() -> dict[str, Any]:
    return {
        "title": "Lexi.AI Paid Offer Map",
        "offers": [
            {
                "id": "brand_blueprint_pack",
                "name": "Custom AI Brand Blueprint Pack",
                "price_starting_usd": 50,
                "includes": [
                    "Custom AI/brand name",
                    "Short bio",
                    "Slogan",
                    "Image prompts",
                    "Ad copy",
                    "One-page concept sheet",
                ],
                "cta": "BLUEPRINT",
                "customers": [
                    "Small businesses",
                    "Music pages",
                    "Gaming brands",
                    "Clothing ideas",
                    "AI characters",
                    "Personal projects",
                    "Creators seeking futuristic identity",
                ],
                "delivery_formats": ["Markdown", "JSON", "HTML", "PDF export later"],
            },
            {
                "id": "documentary_trailer_assist",
                "name": "Documentary Trailer Assist Pack",
                "price_starting_usd": 100,
                "includes": [
                    "2-minute trailer VO",
                    "Shot list",
                    "On-screen stamp kit",
                    "Proof-of-usefulness checklist",
                ],
                "cta": "TRAILER",
                "status": "secondary_offer",
            },
        ],
        "proof_tests": [
            "Can Lexi help someone name their brand?",
            "Can Lexi make an ad?",
            "Can Lexi create a one-page concept sheet?",
            "Can Lexi help deliver paid work this week?",
        ],
        "summary": "Revenue map for Lexi-9-Omega product layer",
    }


def export_documentary_map(memory=None) -> dict[str, Any]:
    ensure_dirs()
    data = documentary_map()
    md_lines = [
        f"# {data['title']}",
        "",
        f"**Logline:** {data['logline']}",
        "",
        f"**Core question:** {data['core_question']}",
        "",
        "## Acts",
    ]
    for act in data["acts"]:
        md_lines.append(f"- **{act['id']}** — {act['title']}")
    md_lines += ["", "## Episodes"]
    for i, ep in enumerate(data["episodes"], 1):
        md_lines.append(f"{i}. {ep}")
    md_lines += [
        "",
        f"**First edit:** {data['first_edit']}",
        "",
        "## Product now",
        f"- {data['product_now']['name']} from ${data['product_now']['price_starting_usd']}",
        f"- CTA: {data['product_now']['cta']}",
        "",
        f"**Grounding:** {data['grounding']}",
        "",
    ]
    if data.get("local_package"):
        md_lines.append(f"**Local package:** `{data['local_package']}`")

    markdown = "\n".join(md_lines) + "\n"
    body = f"<p class='muted'>{data['logline']}</p><div class='card'><h2>Acts</h2><ul>"
    body += "".join(f"<li>{a['title']}</li>" for a in data["acts"])
    body += "</ul></div>"
    html = simple_html_page(data["title"], body, badge="DOCUMENTARY MAP")

    paths = write_bundle(
        kind="documentary_map",
        title=data["title"],
        markdown=markdown,
        data=data,
        html=html,
        subdir="documentary",
    )
    write_json(WORKSPACE / "documentary" / "documentary_map.json", data)
    write_text(WORKSPACE / "documentary" / "documentary_map.md", markdown)

    result = {"paths": paths, "data": data}
    if memory is not None:
        result["deliverable_id"] = memory.save_deliverable(
            "documentary_map", data["title"], paths, meta={}
        )
    return result


def export_offer_map(memory=None) -> dict[str, Any]:
    ensure_dirs()
    data = offer_map()
    md = [f"# {data['title']}", ""]
    for offer in data["offers"]:
        md += [
            f"## {offer['name']}",
            f"- Price starting: ${offer['price_starting_usd']}",
            f"- CTA: {offer['cta']}",
            "- Includes:",
        ]
        for item in offer["includes"]:
            md.append(f"  - {item}")
        md.append("")
    md += ["## Proof tests"]
    for t in data["proof_tests"]:
        md.append(f"- {t}")
    markdown = "\n".join(md) + "\n"

    body = "<div class='card'><h2>Offers</h2><ul>"
    body += "".join(
        f"<li><strong>{o['name']}</strong> — from ${o['price_starting_usd']} · CTA {o['cta']}</li>"
        for o in data["offers"]
    )
    body += "</ul></div>"
    html = simple_html_page(data["title"], body, badge="OFFER MAP")

    paths = write_bundle(
        kind="offer_map",
        title=data["title"],
        markdown=markdown,
        data=data,
        html=html,
        subdir="offers",
    )
    write_json(WORKSPACE / "offers" / "offer_map.json", data)
    write_text(WORKSPACE / "offers" / "offer_map.md", markdown)

    # one-page primary offer
    primary = data["offers"][0]
    one_pager = f"""# One-Page Offer: {primary['name']}

**Price:** Starting at ${primary['price_starting_usd']}  
**CTA:** Comment or message **{primary['cta']}**

## Includes
"""
    for item in primary["includes"]:
        one_pager += f"- {item}\n"
    one_pager += """
## Who it's for
"""
    for c in primary.get("customers", []):
        one_pager += f"- {c}\n"
    one_pager += """
## How it works
1. Client sends BLUEPRINT
2. Share brand type, vibe, audience, offer
3. Receive polished identity pack
4. Use for profiles, ads, decks, launches
"""
    write_text(WORKSPACE / "offers" / "one_page_offer.md", one_pager)
    paths["one_page_offer"] = str(WORKSPACE / "offers" / "one_page_offer.md")

    result = {"paths": paths, "data": data}
    if memory is not None:
        result["deliverable_id"] = memory.save_deliverable(
            "offer_map", data["title"], paths, meta={"primary_price": 50}
        )
    return result
