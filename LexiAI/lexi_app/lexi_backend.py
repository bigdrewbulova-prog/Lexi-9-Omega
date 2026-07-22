#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "lexi_app" / "config.json"
PROMPT_PATH = ROOT / "lexi_system_prompt.txt"


class BigDaddyDrewBackendError(RuntimeError):
    pass


@dataclass
class BigDaddyDrewConfig:
    model: str
    base_model: str
    ollama_api: str
    window_title: str
    provider: str = "ollama"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash"
    gemini_api_base: str = "https://generativelanguage.googleapis.com/v1beta"


def load_local_env(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


class OllamaBigDaddyDrewClient:
    def __init__(self, config: BigDaddyDrewConfig, system_prompt: str) -> None:
        self.config = config
        self.system_prompt = system_prompt.strip()

    @classmethod
    def from_disk(cls) -> "OllamaBigDaddyDrewClient":
        load_local_env(ROOT / ".env.local")
        load_local_env(ROOT / ".env")
        cfg_data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        cfg = BigDaddyDrewConfig(
            model=cfg_data.get("model", "lexi"),
            base_model=cfg_data.get("base_model", "gemma3"),
            ollama_api=cfg_data.get("ollama_api", "http://127.0.0.1:11434/api/chat"),
            window_title=cfg_data.get("window_title", "BigDaddyDrew AI"),
            provider=os.getenv("LEXI_PROVIDER", cfg_data.get("provider", "ollama")).strip().lower(),
            gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
            gemini_model=os.getenv("GEMINI_MODEL", cfg_data.get("gemini_model", "gemini-3.5-flash")),
            gemini_api_base=os.getenv(
                "GEMINI_API_BASE",
                cfg_data.get("gemini_api_base", "https://generativelanguage.googleapis.com/v1beta"),
            ),
        )
        system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
        return cls(cfg, system_prompt)

    def _payload(self, messages: List[Dict[str, str]]) -> bytes:
        full_messages = [{"role": "system", "content": self.system_prompt}, *messages]
        body = {
            "model": self.config.model,
            "messages": full_messages,
            "stream": False,
        }
        return json.dumps(body).encode("utf-8")

    def ping(self) -> None:
        if self.config.provider == "gemini":
            self.chat([{"role": "user", "content": "Reply with: online"}])
            return
        try:
            req = urllib.request.Request(
                self.config.ollama_api,
                data=self._payload([{"role": "user", "content": "Reply with: online"}]),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status != 200:
                    raise BigDaddyDrewBackendError(f"Ollama returned HTTP {resp.status}")
        except urllib.error.URLError as exc:
            raise BigDaddyDrewBackendError(
                "Could not reach Ollama at 127.0.0.1:11434. Open Ollama first, then try again."
            ) from exc

    def _gemini_payload(self, messages: List[Dict[str, str]]) -> bytes:
        contents = []
        for message in messages:
            role = message.get("role", "user")
            text = message.get("content", "")
            if not text:
                continue
            contents.append(
                {
                    "role": "model" if role == "assistant" else "user",
                    "parts": [{"text": text}],
                }
            )
        body = {
            "systemInstruction": {"parts": [{"text": self.system_prompt}]},
            "contents": contents or [{"role": "user", "parts": [{"text": ""}]}],
            "generationConfig": {"temperature": 0.4},
        }
        return json.dumps(body).encode("utf-8")

    def _chat_with_gemini(self, messages: List[Dict[str, str]]) -> str:
        if not self.config.gemini_api_key:
            raise BigDaddyDrewBackendError(
                "GEMINI_API_KEY is missing. Add it to /Users/BigDaddyDrew/LexiAI/.env.local."
            )

        model = self.config.gemini_model
        model_path = model if model.startswith("models/") else f"models/{model}"
        url = (
            f"{self.config.gemini_api_base.rstrip('/')}/{model_path}:generateContent"
            f"?key={urllib.parse.quote(self.config.gemini_api_key)}"
        )
        try:
            req = urllib.request.Request(
                url,
                data=self._gemini_payload(messages),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=180) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="ignore")
            raise BigDaddyDrewBackendError(f"Gemini HTTP error: {exc.code}\n{body}") from exc
        except urllib.error.URLError as exc:
            raise BigDaddyDrewBackendError("Could not connect to Gemini.") from exc
        except json.JSONDecodeError as exc:
            raise BigDaddyDrewBackendError("Received invalid JSON from Gemini.") from exc

        parts = (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [])
        )
        content = "".join(part.get("text", "") for part in parts).strip()
        if not content:
            feedback = data.get("promptFeedback") or data.get("prompt_feedback") or {}
            raise BigDaddyDrewBackendError(f"Gemini returned an empty response. Prompt feedback: {feedback}")
        return content

    def chat(self, messages: List[Dict[str, str]]) -> str:
        if self.config.provider == "gemini":
            return self._chat_with_gemini(messages)

        try:
            req = urllib.request.Request(
                self.config.ollama_api,
                data=self._payload(messages),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=180) as resp:
                raw = resp.read().decode("utf-8")
                data = json.loads(raw)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="ignore")
            raise BigDaddyDrewBackendError(f"Ollama HTTP error: {exc.code}\n{body}") from exc
        except urllib.error.URLError as exc:
            raise BigDaddyDrewBackendError(
                "Could not connect to Ollama. Make sure the Ollama app is running."
            ) from exc
        except json.JSONDecodeError as exc:
            raise BigDaddyDrewBackendError("Received invalid JSON from Ollama.") from exc

        message = data.get("message", {})
        content = message.get("content", "").strip()
        if not content:
            raise BigDaddyDrewBackendError("Ollama returned an empty response.")
        return content
