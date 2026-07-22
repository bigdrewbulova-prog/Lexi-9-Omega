#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$HOME/LexiAI"
BUILD_DIR="$APP_DIR/llama.cpp/build/bin"
MODEL_DIR="$APP_DIR/models"
MODEL_FILE="${1:-$MODEL_DIR/model.gguf}"
PORT="${PORT:-8080}"

if [ ! -x "$BUILD_DIR/llama-server" ]; then
  echo "llama-server not found. Run build_legacy_llamacpp.sh first."
  exit 1
fi

if [ ! -f "$MODEL_FILE" ]; then
  echo "Model not found: $MODEL_FILE"
  echo "Put your GGUF model in $MODEL_DIR and pass its path as the first argument if needed."
  exit 1
fi

exec "$BUILD_DIR/llama-server" -m "$MODEL_FILE" --host 127.0.0.1 --port "$PORT"
