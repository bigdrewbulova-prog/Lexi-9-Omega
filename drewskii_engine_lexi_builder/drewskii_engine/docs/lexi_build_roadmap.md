# Lexi-9-OMEGA Build Roadmap

## Phase 1 — Core Brain
Goal: Create a local command-line Drewskii.Engine that can plan, remember, log, and generate starter files.

Build:
- Local Python CLI
- SQLite memory
- Safety filter
- Project planner
- Code/template generator

## Phase 2 — Lexi Knowledge Core
Goal: Turn your Lexi project notes into structured files.

Build:
- `lexi_identity.md`
- `lexi_capabilities.json`
- `lexi_safety_rules.md`
- `lexi_roadmap.md`
- Importer for pasted notes

## Phase 3 — Android Companion
Goal: Use Termux and permission-based Android APIs.

Build:
- Voice output with `termux-tts-speak`
- Camera/photo helper with user permission
- Location helper with user permission
- Notification reminders
- No hidden control, no bypassing Android security

## Phase 4 — UI Shell
Goal: Build the visible Lexi interface.

Options:
- Web dashboard first
- Kivy Python prototype
- Jetpack Compose Android app later
- Desktop pet avatar later

## Phase 5 — Local AI Agent
Goal: Connect Drewskii.Engine to a local or cloud LLM.

Build:
- Prompt router
- Memory retrieval
- Tool permissions
- Evaluation logs
- Human approval gate

## Phase 6 — Engineering Tools
Goal: Add Lexi.PHYS tools.

Build:
- Blueprint generator prompts
- Structural checklist generator
- FEM simulation planner
- Micro-fracture heatmap concept module
- Materials database
- Safety documentation generator

## Phase 7 - Official App Features
Goal: Promote stable user-space prototype workflows into official platform features.

Build:
- Native app feature shell
- Guided AI Brand Blueprint intake
- Saved pack history
- Export/share actions
- App permission screens
- Privacy and safety notes
- Test/evaluation dashboard

Rule:
Prototype first in safe user space. Ship official app features only after the workflow has clear value, explicit permissions, stable data formats, validation notes, and a rollback path.
