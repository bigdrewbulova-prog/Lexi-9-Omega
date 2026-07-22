#!/user/bin/env bash
set -euo pipefail

APP_DIR="$HOME/LexiAI"
SRC_DIR="$APP_DIR/llama.cpp"
BUILD_DIR="$SRC_DIR/build"
MODEL_DIR="$APP_DIR/models"

need_cmd() { command -v "$1" >/dev/null 2>&1 || { echo "Missing: $1"; exit 1; }; }

need_cmd git
need_cmd cmake
need_cmd xcode-select

mkdir -p "$APP_DIR" "$MODEL_DIR"

if ! xcode-select -p >/dev/null 2>&1; then
  echo "Install Xcode Command Line Tools first: xcode-select --install"
  exit 1
fi

if [ ! -d "$SRC_DIR" ]; then
  git clone https://github.com/ggml-org/llama.cpp.git "$SRC_DIR"
else
  git -C "$SRC_DIR" pull --ff-only
fi

cmake -S "$SRC_DIR" -B "$BUILD_DIR"
cmake --build "$BUILD_DIR" --config Release

echo
echo "Built llama.cpp."
echo "Put a GGUF model file in: $MODEL_DIR"
echo "Then run: $HOME/LexiAI/bin/run_legacy_server.command"
