#!/bin/bash
set -euo pipefail

APP_HOME="${HOME}/LexiAI"
APP_DIR="${APP_HOME}/lexi_app"

if [[ ! -d "$APP_DIR" ]]; then
  echo "Lexi is not installed yet. Run install_lexi_mac.sh first."
  exit 1
fi

cd "$APP_DIR"

if python3 - <<'PY' >/dev/null 2>&1
import tkinter
PY
then
  exec python3 lexi_gui.py
else
  echo "Tkinter is not available. Starting Lexi in CLI mode..."
  exec python3 lexi_cli.py
fi
