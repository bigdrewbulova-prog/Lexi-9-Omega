# LEXI.PHYS Companion Lab V1

A modular local-first AI companion laboratory built around the existing Ollama `lexi` model.

## Installation

1. Create and activate a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and update as needed:

```bash
cp .env.example .env
```

## Launch

Start the server:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8765 --reload
```

## Endpoints

- `GET /health`
- `POST /chat`
- `POST /memory`
- `GET /memory/search`
- `GET /system/status`
- `POST /labs`
- `GET /labs`
- `GET /labs/{experiment_id}`

## Notes

- Uses Ollama at `http://127.0.0.1:11434/api/chat`
- Uses SQLite for persistence
- Designed to preserve `/health` and `/chat` compatibility with the Android companion client
