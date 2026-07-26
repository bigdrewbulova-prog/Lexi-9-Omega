# Local-First Intelligence Model Stack

## Operating Rule
Run Lexi.AI as a **safe user-space prototype** first.  
Promote to official app features only after the workflow is **useful, repeatable, permission-safe, and testable**.

## Stage 1 — User-Space Prototype (BUILD NOW)

| Capability | Module / command |
|---|---|
| CLI planning + project memory | `plan`, `remember`, `memory`, SQLite |
| Brand Blueprint Pack ($50 path) | `forge`, `stack brand`, `stack run` |
| Documentary + offer mapping | `documentary-map`, `offer` |
| MD / JSON / HTML / SQLite outputs | `brain/artifacts.py`, memory DB |
| Web dashboard shell | `generate-ui` → `workspace/lexi_dashboard.html` |
| Termux helpers (approved only) | `termux`, `termux <id> --yes` |
| Evaluation logs | `eval`, `evals`, `workspace/evals/` |
| Model stack + local keys | `cortana status|mint|models|invent|ask` |

### Full automation run
```bash
cd drewskii_engine
python3 main.py
# stack
# stack run
# stack brand My Brand | vibe | audience | offer
# stack rules
# stack promote brand_pack
```

Or one-shot:
```bash
python3 -c "from brain.intelligence_stack import demo; import json; print(json.dumps(demo()['stats'], indent=2))"
```

## Stage 2 — Official App Features (BUILD LATER)
- Native Android screens (packs, memory, status)
- Share sheet / file import
- Notification reminders
- Local SQLite library UI
- Optional OAuth sync only
- Permission screens
- Export Markdown / PDF / ZIP
- Payment + customers only after reliability

## Promotion Gate
A feature promotes only with:
1. Clear user value  
2. Explicit permissions  
3. Stable I/O format  
4. Local error handling  
5. Tests or manual validation notes  
6. Privacy and safety notes  
7. Rollback path  

Use: `stack promote <feature>` with evidence checklist.

## First Product Path — $50 Brand Blueprint Packs
**Prototype:** intake → generate → save local → quality checklist → **ZIP package**  
**CLI:**
```text
stack pack Nova Thread | midnight ultraviolet | late-night creators | identity + ads
# → Customer ZIP ready: workspace/deliverables/blueprints/packages/...-brand-pack.zip
```
**Guided HTML intake + local library (Stage-2 slice, local-only):**
```text
stack serve
# → http://127.0.0.1:8787/         form → generate → Download ZIP
# → http://127.0.0.1:8787/library  pack history + re-download
# → GET /api/packs                 JSON list of local ZIPs
```
**ZIP contents:** README, brand_pack.md/html/json, optional starter code  
**Library:** scans `workspace/deliverables/blueprints/packages/*-brand-pack.zip` + SQLite deliverables  
**Official app later:** native intake UI → history → export/share → payments  

## Blocked
Hidden accounts · password collection · security bypass · background surveillance · OS control outside official APIs · speculative physics as finished hardware
