import json
import urllib.error
import urllib.request
from typing import Iterator
from app.config import OLLAMA_API_URL, OLLAMA_MODEL

class OllamaError(RuntimeError):
    pass


def _payload(messages):
    return json.dumps({
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": True,
    }).encode("utf-8")


def chat(messages):
    req = urllib.request.Request(
        OLLAMA_API_URL,
        data=_payload(messages),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            for line in resp:
                yield line.decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        raise OllamaError(f"Ollama HTTP error: {exc.code} {body}") from exc
    except urllib.error.URLError as exc:
        raise OllamaError("Could not reach Ollama. Ensure the Ollama server is running.") from exc


def ping() -> bool:
    req = urllib.request.Request(
        OLLAMA_API_URL,
        data=json.dumps({
            "model": OLLAMA_MODEL,
            "messages": [{"role": "user", "content": "Reply with: online"}],
            "stream": False,
        }).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception:
        return False
