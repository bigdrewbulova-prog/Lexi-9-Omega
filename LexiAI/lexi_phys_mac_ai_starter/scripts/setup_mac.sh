#!/bin/bash
set -e
cd "$(dirname "$0")/.."
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp -n config/example.env .env || true
echo "Setup complete."
echo "Edit .env and config/sources.json, then run:"
echo "python scripts/ingest_files.py"
echo "python lexi_terminal.py"
echo "uvicorn dashboard.app:app --reload --host 127.0.0.1 --port 8765"
