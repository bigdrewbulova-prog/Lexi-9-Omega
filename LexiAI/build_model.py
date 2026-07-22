#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "lexi_app" / "config.json"
PROMPT_PATH = ROOT / "lexi_system_prompt.txt"
TEMPLATE_PATH = ROOT / "Modelfile.template"
MODelfILE_PATH = ROOT / "Modelfile"


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {"model": "lexi", "base_model": "gemma3"}
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def main() -> int:
    if shutil.which("ollama") is None:
        print("Error: 'ollama' was not found in PATH.", file=sys.stderr)
        return 1

    cfg = load_config()
    model_name = cfg.get("model", "lexi")
    base_model = cfg.get("base_model", "gemma3")

    system_prompt = PROMPT_PATH.read_text(encoding="utf-8").strip()
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    modelfile = template.replace("{{BASE_MODEL}}", base_model).replace("{{SYSTEM_PROMPT}}", system_prompt)
    MODelfILE_PATH.write_text(modelfile, encoding="utf-8")

    print(f"Pulling base model: {base_model}")
    pull = subprocess.run(["ollama", "pull", base_model])
    if pull.returncode != 0:
        return pull.returncode

    print(f"Creating custom model: {model_name}")
    create = subprocess.run(["ollama", "create", model_name, "-f", str(MODelfILE_PATH)])
    return create.returncode


if __name__ == "__main__":
    raise SystemExit(main())
