# Drewskii.Engine - Top Layer Documentary + Builder Kit

Drewskii.Engine is the top-layer public documentary and command interface for the Lexi-9-Omega project.

Think of it like this:
- **Drewskii.Engine** = the human-facing story, documentary, brand builder, client offer, and command center.
- **Lexi.AI** = the assistant layer that talks, writes, remembers, and builds documents.
- **Lexi.PHYS** = the engineering/physics persona layer for blueprints, simulations, materials, and structural imagination.
- **Lexi-9-Omega** = the full mythology/architecture layer: the master project identity, governance, roadmap, and future product ecosystem.

This kit gives you a safe Python prototype that runs in normal user space. It does not root Android, bypass security, wipe apps, or implant into SystemUI.

## Start in 3 Steps

### 1. Install Python
Use Python 3 from python.org, Termux, or your package manager.

### 2. Open terminal / CMD
Go into this folder:

```bash
cd drewskii_engine_lexi_builder/drewskii_engine
```

### 3. Run it

```bash
python main.py
```

Type:

```text
help
identity
model Lexi.PHYS
model Drewskii.Engine
documentary
top-layer
software
experimental The Aethelweave represents a simulation-only metamaterial concept.
blueprint
remember First paid offer: AI Brand Blueprint Packs starting at $50.
list
memory
quit
```

## Optional Web App

From the project root:

```bash
pip install -r requirements.txt
streamlit run app_streamlit.py
```

## Optional API

From the project root:

```bash
pip install -r requirements.txt
uvicorn api_fastapi:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

## Important Files

- `drewskii_engine/main.py` - local CLI command center
- `drewskii_engine/lexi_identity.json` - Lexi identity contract
- `drewskii_engine/model_profiles/lexi_phys.json` - active Lexi.PHYS model profile
- `drewskii_engine/model_profiles/drewskii_engine.json` - top-layer Drewskii.Engine model profile
- `drewskii_engine/docs/models/Lexi_PHYS.md` - readable model contract
- `drewskii_engine/docs/models/Drewskii_Engine.md` - readable top-layer builder contract
- `drewskii_engine/lexi_skills.json` - skill catalog
- `drewskii_engine/docs/lexi_documentary_map.md` - Lexi-9-Omega documentary map
- `drewskii_engine/docs/drewskii_engine_documentary_top_layer.md` - Drewskii.Engine documentary map
- `drewskii_engine/docs/user_space_to_official_app.md` - safe prototype-to-app path
- `drewskii_engine/docs/experiments/` - Lexi.PHYS experimental concept docs
- `drewskii_engine/docs/skills/` - safe capability and hardware-profile docs
- `drewskii_engine/workspace/experiments/` - structured experiment metadata
- `drewskii_engine/workspace/skills/` - structured skill metadata
- `drewskii_engine/workspace/` - generated UI and blueprint files
- `drewskii_engine/memory/` - local SQLite memory and project log

## Scope

Drewskii.Engine is a user-space builder kit. It can plan, remember, generate files, and document the project. It does not perform hidden control, account bypassing, privileged Android modification, or unsafe automation.
