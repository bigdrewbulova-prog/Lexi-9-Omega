# Lexi.AI Creative Engineering Operator

Lexi.AI is structured as a local-first creative engineering intelligence platform for building models, software, prototypes, Cash System packs, and an AI business around your own files.

Its positioning is deliberate: part AI companion, part invention lab, part futuristic blueprint generator, part Cash System. It should help BigDaddyDrew turn scattered ideas and local context into grounded concepts, system specs, validation plans, demos, content hooks, product ideas, service packages, and shippable offers.

## Cognitive Architecture

Lexi.AI uses the official LEX-9-OMEGA Dual-Sphere Cognitive Model as its product-level reasoning frame.

- Sphere Omega1, the World Model, maps what exists: files, memory, systems, constraints, proof, and external context.
- Sphere Omega2, the Generative Core, produces what could exist: blueprints, simulations, offers, product plans, and new configurations.
- The Omega-Gap compares the current state against the possible state and becomes the invention layer where practical artifacts are generated.

See:

```text
/Users/BigDaddyDrew/LexiAI/docs/LEX9_OMEGA_DUAL_SPHERE_MODEL.md
```

## What It Can Do

- Index LexiAI project files, `chat_logs/`, `workspace/`, and common Mac work folders.
- Snapshot project scans, detect meaningful changes, and store monitor check-ins in SQLite.
- Store chat memory, project inventory, autonomous runs, monitor history, and generated plans in SQLite.
- Turn a goal into an invention brief, blueprint spec, model-building plan, business operating plan, approval gates, and next actions.
- Generate saved blueprint artifacts under `workspace/blueprints/` with component specs, prototype sprints, validation checks, and a ranked build queue.
- Generate saved Cash System artifacts under `workspace/cash-systems/` with content hooks, productized offers, service packages, launch assets, fulfillment steps, and validation metrics.
- Expose the Lexi.PHYS Elite capability profile for geometry-first reverse engineering, structural foresight, simulation planning, and blueprint documentation.
- Use Ollama for richer local reasoning when your local model is running.
- Expose the same capabilities through FastAPI and the terminal CLI.

## Safety Model

Lexi.AI is intentionally approval-gated.

- Read-only scans are allowed inside configured roots.
- Secrets such as `.env.local` are excluded from indexing.
- File writes outside this workspace require explicit approval.
- Commands that install packages, delete files, publish data, spend money, or call paid APIs require approval.
- Plans are saved locally before any risky execution happens.

## Add ChatGPT And Mac Files

ChatGPT does not expose a direct consumer API for pulling every project chat and
file into LexiAI. Request a ChatGPT data export from ChatGPT settings, download
the ZIP when OpenAI sends it, then import it locally:

```bash
python3 /Users/BigDaddyDrew/LexiAI/lexi_app/chatgpt_importer.py /Users/BigDaddyDrew/Downloads/chatgpt-export.zip
```

Or from the LexiAI CLI:

```text
/import-chatgpt /Users/BigDaddyDrew/Downloads/chatgpt-export.zip
```

The importer writes readable conversation transcripts and JSONL files into
`chat_logs/`, copies exported file assets into `workspace/chatgpt_files/`, and
updates LexiAI's local project index.

Put exported ChatGPT files, notes, transcripts, or copied project material in:

```text
/Users/BigDaddyDrew/LexiAI/chat_logs
```

Put working project artifacts in:

```text
/Users/BigDaddyDrew/LexiAI/workspace
```

LexiAI also scans common Mac work folders such as Desktop, Documents, and Downloads with a file limit. To control roots explicitly, add this to `lexi_app/config.json`:

```json
{
  "workspace_roots": [
    "/Users/BigDaddyDrew/LexiAI",
    "/Users/BigDaddyDrew/Documents"
  ]
}
```

Keep `.env.local` and private model files out of scan roots unless you really mean to expose them to local indexing. The scanner already skips common secret files.

## CLI

Run:

```bash
python3 /Users/BigDaddyDrew/LexiAI/lexi_app/lexi_cli.py
```

Useful commands:

```text
/scan ai model
/blueprint build a pocket invention lab for prototype ideas
/cash-system turn Lexi.AI into a money-making machine that creates content products and services
/watch
/changes
/goal build Lexi.AI into a creative engineering platform with companion memory and blueprint generation
/runs
/memory
/tools
/profile
```

## API

Start the server:

```bash
/Users/BigDaddyDrew/LexiAI/run_lexi.sh
```

Scan projects:

```bash
curl -s http://127.0.0.1:8000/autonomous/scan \
  -H 'Content-Type: application/json' \
  -d '{"query":"model business","max_files":100}'
```

Create a monitor check-in for configured roots:

```bash
curl -s http://127.0.0.1:8000/autonomous/monitor/check-in \
  -H 'Content-Type: application/json' \
  -d '{"max_files":250}'
```

Create a monitor check-in for selected roots:

```bash
curl -s http://127.0.0.1:8000/autonomous/monitor/check-in \
  -H 'Content-Type: application/json' \
  -d '{"roots":["/Users/BigDaddyDrew/LexiAI"],"max_files":250}'
```

Review recent monitor check-ins:

```bash
curl -s 'http://127.0.0.1:8000/autonomous/monitor/check-ins?limit=5'
```

Show the Lexi.PHYS Elite profile:

```bash
curl -s http://127.0.0.1:8000/identity/lexi-phys
```

Run an autonomous planning goal:

```bash
curl -s http://127.0.0.1:8000/autonomous/run \
  -H 'Content-Type: application/json' \
  -d '{"goal":"Position Lexi.AI as a creative engineering intelligence platform","mode":"auto"}'
```

Generate a buildable blueprint and save artifacts:

```bash
curl -s http://127.0.0.1:8000/blueprint \
  -H 'Content-Type: application/json' \
  -d '{"idea":"Build a pocket invention lab for prototype ideas","depth":"prototype","write_artifacts":true}'
```

Generate a Cash System pack and save artifacts:

```bash
curl -s http://127.0.0.1:8000/cash-system \
  -H 'Content-Type: application/json' \
  -d '{"idea":"Turn Lexi.AI into a money-making machine that creates content products and services","write_artifacts":true}'
```

Capture a proof-page waitlist lead and update local JSON/CSV exports:

```bash
curl -s http://127.0.0.1:8000/leads \
  -H 'Content-Type: application/json' \
  -d '{"email":"buyer@example.com","source":"proof-page-waitlist","offer":"Lexi.AI Cash System early access"}'
```

Review or export the lead pipeline:

```bash
curl -s 'http://127.0.0.1:8000/leads?limit=50'
curl -s http://127.0.0.1:8000/leads/export.csv
curl -s http://127.0.0.1:8000/leads/export.json
```

## First Platform Build Loop

1. Drop your ChatGPT exports, notes, and project files into `chat_logs/` or `workspace/`.
2. Run `/scan`.
3. Run `/goal position Lexi.AI as a creative engineering intelligence platform`.
4. Pick one first platform demo: companion memory, invention-lab planning, blueprint generation, or Cash System packaging.
5. Build a 20-case eval set before fine-tuning or selling a workflow as reliable.
6. Ship one proof asset each week: demo, case study, blueprint, prompt pack, workflow, or model card.

## OpenAI API

`.env.local` is the local place for provider API keys such as `OPENAI_API_KEY` and `GEMINI_API_KEY`. It is ignored by git. The current autonomous core is local-first and does not need to call a hosted model to scan, plan, or save runs.

Gemini-backed chat can be enabled locally with:

```env
LEXI_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_key_here
GEMINI_MODEL=gemini-3.5-flash
```
