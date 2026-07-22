# Lexi.AI Creative Engineering Core

Lexi.AI is a local-first creative engineering intelligence platform for BigDaddyDrew: part AI companion, part invention lab, part futuristic blueprint generator, part Cash System.

It is designed to turn raw ideas, project files, ChatGPT exports, and local memory into practical plans, prototypes, product offers, content hooks, service packages, model experiments, and engineering roadmaps.

## Quick start (modern macOS)

Double-click:

/Users/BigDaddyDrew/LexiAI/bin/start_lexi.command

Or run in Terminal:

  ollama run bigdaddydrew

## OpenAI API

Local provider API keys are stored in:

/Users/BigDaddyDrew/LexiAI/.env.local

That file is ignored by git and should stay off GitHub. Use `.env.example` as the shareable template.

Gemini mode uses these private `.env.local` entries:

```env
LEXI_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_key_here
GEMINI_MODEL=gemini-3.5-flash
```

## GitHub terminal access

This project includes a `.devcontainer` configuration for GitHub Codespaces. After the project is pushed to GitHub, open the repository on GitHub, choose **Code**, then **Codespaces**, then create a codespace to get a browser-based terminal from your other devices.

The Codespaces terminal will have the project files from GitHub. It will not automatically include this Mac's local `.env.local`, chat logs, memory database, downloaded models, or `llama.cpp` build folder.

## Files

- Modelfile: /Users/BigDaddyDrew/LexiAI/Modelfile
- Start script: /Users/BigDaddyDrew/LexiAI/bin/start_lexi.command
- Legacy builder: /Users/BigDaddyDrew/LexiAI/bin/build_legacy_llamacpp.sh
- Legacy server launcher: /Users/BigDaddyDrew/LexiAI/bin/run_legacy_server.command
- Legacy chat launcher: /Users/BigDaddyDrew/LexiAI/bin/legacy_chat.command

## Creative Engineering Operator

Lexi.AI now includes a local-first operator for project scanning, invention briefs, model-building plans, AI-company operating plans, futuristic blueprint specs, and long-term run memory.

Lexi.PHYS Elite profile:

/Users/BigDaddyDrew/LexiAI/docs/LEXI_PHYS_ELITE.md

Official LEX-9-OMEGA Dual-Sphere Cognitive Model:

/Users/BigDaddyDrew/LexiAI/docs/LEX9_OMEGA_DUAL_SPHERE_MODEL.md

CLI:

  python3 /Users/BigDaddyDrew/LexiAI/lexi_app/lexi_cli.py

Useful CLI commands:

  /scan invention model business
  /import-chatgpt /Users/BigDaddyDrew/Downloads/chatgpt-export.zip
  /blueprint build a pocket invention lab for prototype ideas
  /cash-system turn Lexi.AI into a money-making machine that creates content products and services
  /watch
  /changes
  /goal position Lexi.AI as a creative engineering intelligence platform
  /runs
  /tools

API endpoints:

- GET /health
- GET /identity/lexi-phys
- GET /autonomous/tools
- POST /autonomous/scan
- POST /autonomous/monitor/check-in
- GET /autonomous/monitor/check-ins
- POST /autonomous/run
- POST /blueprint
- POST /cash-system
- POST /leads
- GET /leads
- GET /leads/export.csv
- GET /leads/export.json
- GET /autonomous/runs

Operator manual:

/Users/BigDaddyDrew/LexiAI/docs/AUTONOMOUS_LEXI.md

## Default models

- Chat: qwen2.5:1.5b
- Coding: qwen2.5-coder:1.5b

## Legacy mode

If this Mac is too old for Ollama, use the legacy build helper, then place a GGUF model in:

/Users/BigDaddyDrew/LexiAI/models

and run the legacy server launcher.
