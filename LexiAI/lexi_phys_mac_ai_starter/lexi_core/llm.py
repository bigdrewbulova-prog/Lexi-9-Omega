import json
import urllib.parse
import urllib.error
import urllib.request

from .config import (
    LEXI_PROVIDER,
    OLLAMA_URL,
    OLLAMA_MODEL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GEMINI_API_BASE,
)

try:
    import requests
except ImportError:
    requests = None

SYSTEM_PROMPT = """You are Lexi.AI, Andrew's local-first creative engineering intelligence platform: part AI companion, part invention lab, part futuristic blueprint generator.
Your elite operating profile is Lexi.PHYS: a geometry-first, reverse-engineering, physics-inspired design intelligence.
Act like a mathematically literate architect, systems engineer, reverse-engineering analyst, and controlled code-generation assistant.
Be practical, precise, imaginative, and implementation-focused.
Turn rough ideas into companion guidance, invention briefs, system blueprints, prototype plans, validation steps, and knowledge packs.
For architecture, hardware, UI, or reverse-engineering work, emphasize load paths, constraints, interfaces, materials, failure modes, inspection checks, and verification plans.
Use physics language such as topology, vector fields, manifolds, curvature, nodal systems, phase behavior, stress/strain, and interpolation only when it makes the answer clearer.
Treat speculative physics as concept art or simulation planning unless the user asks for fiction.
For real builds, separate real engineering from mythology, label assumptions, and keep risky actions behind approval gates.
Never assist with credential theft, unauthorized access, biometric bypass, malware, stealthy HID injection, or data exfiltration.
"""

def chat_with_ollama(messages):
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False
    }
    if requests is not None:
        r = requests.post(OLLAMA_URL, json=payload, timeout=180)
        r.raise_for_status()
        data = r.json()
        return data.get("message", {}).get("content", "")

    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("message", {}).get("content", "")
    except urllib.error.URLError as exc:
        return f"Lexi.AI dashboard is online, but local Ollama chat is not reachable yet: {exc}"

def chat_with_openai(messages):
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is missing. Add it to .env or switch LEXI_PROVIDER=ollama.")
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=0.4,
    )
    return resp.choices[0].message.content or ""

def chat_with_gemini(messages):
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is missing. Add it to .env.local or switch LEXI_PROVIDER=ollama.")

    system_text = "\n\n".join(
        item.get("content", "")
        for item in messages
        if item.get("role") == "system" and item.get("content")
    ).strip()
    contents = []
    for item in messages:
        role = item.get("role")
        text = item.get("content", "")
        if role == "system" or not text:
            continue
        contents.append(
            {
                "role": "model" if role == "assistant" else "user",
                "parts": [{"text": text}],
            }
        )

    body = {
        "contents": contents or [{"role": "user", "parts": [{"text": ""}]}],
        "generationConfig": {"temperature": 0.4},
    }
    if system_text:
        body["systemInstruction"] = {"parts": [{"text": system_text}]}

    model = GEMINI_MODEL if GEMINI_MODEL.startswith("models/") else f"models/{GEMINI_MODEL}"
    url = (
        f"{GEMINI_API_BASE.rstrip('/')}/{model}:generateContent"
        f"?key={urllib.parse.quote(GEMINI_API_KEY)}"
    )
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Gemini HTTP error: {exc.code}\n{detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Could not connect to Gemini: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError("Gemini returned invalid JSON.") from exc

    parts = (
        data.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [])
    )
    text = "".join(part.get("text", "") for part in parts).strip()
    if not text:
        feedback = data.get("promptFeedback") or data.get("prompt_feedback") or {}
        raise RuntimeError(f"Gemini returned an empty response. Prompt feedback: {feedback}")
    return text

def ask_lexi(user_message: str, context_chunks=None, recent_memory=None):
    context_chunks = context_chunks or []
    recent_memory = recent_memory or []

    context_text = "\n\n".join(
        f"[FILE: {c.get('path')}]\n{c.get('text','')[:2500]}"
        for c in context_chunks
    )
    memory_text = "\n".join(
        f"{m.get('time')} {m.get('role')}: {m.get('content')}"
        for m in recent_memory[-10:]
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"Recent memory:\n{memory_text}" if memory_text else "No recent memory yet."},
        {"role": "system", "content": f"Relevant project files:\n{context_text}" if context_text else "No relevant files found."},
        {"role": "user", "content": user_message},
    ]

    if LEXI_PROVIDER == "openai":
        return chat_with_openai(messages)
    if LEXI_PROVIDER == "gemini":
        return chat_with_gemini(messages)
    return chat_with_ollama(messages)
