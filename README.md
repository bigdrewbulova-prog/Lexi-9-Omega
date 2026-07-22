# LEXI-9-OMEGA Stack

Public builder kit and simulation surface for **Lexi-9-Omega** / **Drewskii.Engine**.

Owner target: [Bigdrewbulova-prog](https://github.com/Bigdrewbulova-prog)

## Packages

| Path | Description |
|---|---|
| `drewskii_engine_lexi_builder/` | Drewskii.Engine CLI, Blueprint Forge, Mastermind sim cycle |
| `LEXI-9-OMEGA-Documentary/` | Documentary production package + trailer scripts |
| `CHRONOS-VII-The-Circlet/` | Cinematic spacetime sandbox (fiction/sim only) |
| `lexi_ai_desktop_companion/` | Local Tk desktop companion |
| `LEXI-9-OMEGA-HACKATHON/` | Evidence-to-action web demo (live-run engine) |
| `LexiAI/` | Lexi.AI creative engineering core (subset; secrets excluded) |

## Safety

- User-space first  
- No hidden persistence / exploit tooling  
- Speculative Lexi.PHYS = simulation, lore, or visualization only  
- Secrets (`.env.local`, API keys, memory DBs) are **not** in this repo  

## Quick start — Drewskii.Engine

```bash
cd drewskii_engine_lexi_builder/drewskii_engine
python3 main.py
# help
# forge My Brand
# mastermind 17.4 0.97
```

## Quick start — Hackathon demo

```bash
cd LEXI-9-OMEGA-HACKATHON
npm install
npm run dev
```

## Note on history

This monorepo was assembled as a clean publish snapshot. Individual package git histories (where they existed) were not rewritten into a single lineage; new history starts at the initial publish commit unless rebased later.
