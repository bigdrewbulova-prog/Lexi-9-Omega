#!/bin/bash
cd "$(dirname "$0")/.."
source .venv/bin/activate
uvicorn dashboard.app:app --reload --host 127.0.0.1 --port 8765
