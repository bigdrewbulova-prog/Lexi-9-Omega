# Lexi.AI Mac Creative Engineering Starter

A local-first creative engineering intelligence stack for macOS:

- Terminal AI companion
- Futuristic invention-lab dashboard
- Local Ollama model support
- Optional OpenAI API support
- Project-file ingestion from your Mac folders
- Local project search
- Memory store
- 3D avatar placeholder using Three.js
- Blueprint-generation workflow surface
- Connector stubs for Firebase, Google Cloud, GitHub, Linear, Google Drive, and Google AI Studio exports

## 1. Install basics

```bash
cd ~/LexiAI
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Install Ollama separately, then pull a model:

```bash
ollama pull llama3.2:3b
# or keep using your existing lexi:latest
```

## 2. Configure

Copy the example config:

```bash
cp config/example.env .env
```

Edit `.env`:

```bash
nano .env
```

Recommended local-only start:

```env
LEXI_PROVIDER=ollama
OLLAMA_MODEL=lexi:latest
```

Optional OpenAI mode:

```env
LEXI_PROVIDER=openai
OPENAI_MODEL=gpt-4.1-mini
OPENAI_API_KEY=your_key_here
```

Optional Gemini mode:

```env
LEXI_PROVIDER=gemini
GEMINI_MODEL=gemini-3.5-flash
GEMINI_API_KEY=your_key_here
```

## 3. Add your Mac project folders

Edit `config/sources.json` and add folders you want Lexi to learn from.

Example:

```json
{
  "folders": [
    "/Users/YOURNAME/LexiAI",
    "/Users/YOURNAME/Documents",
    "/Users/YOURNAME/Downloads"
  ],
  "extensions": [".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".java", ".kt", ".xml"]
}
```

## 4. Ingest your files

```bash
python scripts/ingest_files.py
```

## 5. Run terminal chat

```bash
python lexi_terminal.py
```

## 6. Run dashboard

```bash
uvicorn dashboard.app:app --reload --host 127.0.0.1 --port 8765
```

Open:

```text
http://127.0.0.1:8765
```

## 7. Add 3D character avatar

Put a `.glb` or `.gltf` model into:

```text
avatars/models/avatar.glb
```

Then reload the dashboard.

## Notes

This starter does not hack accounts, bypass locks, clone device IDs, or exfiltrate data. It is built for your own files, your own apps, and authorized APIs only.
