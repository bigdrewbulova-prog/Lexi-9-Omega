from __future__ import annotations

import json
import re
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from drewskii_engine.brain.experimental import create_experimental_concept, list_experimental_concepts


ROOT = Path(__file__).resolve().parent
ENGINE_DIR = ROOT / "drewskii_engine"
WORKSPACE_DIR = ENGINE_DIR / "workspace"

app = FastAPI(title="Drewskii.Engine Builder Kit", version="1.0.0")


class BlueprintRequest(BaseModel):
    name: str = "Custom AI Brand Blueprint Pack"


class ExperimentalRequest(BaseModel):
    concept: str
    title: str | None = None


def read_text(relative_path: str) -> str:
    return (ENGINE_DIR / relative_path).read_text(encoding="utf-8")


def read_json(relative_path: str) -> dict:
    return json.loads(read_text(relative_path))


def model_profile_path(model_name: str) -> str:
    normalized = model_name.strip().lower().replace("_", ".").replace("-", ".")
    if normalized in {"lexi", "lexi.phys"}:
        return "model_profiles/lexi_phys.json"
    if normalized in {"drewskii", "drewskii.engine"}:
        return "model_profiles/drewskii_engine.json"
    raise HTTPException(status_code=404, detail="unknown model profile")


def model_docs_path(model_name: str) -> str:
    normalized = model_name.strip().lower().replace("_", ".").replace("-", ".")
    if normalized in {"lexi", "lexi.phys"}:
        return "docs/models/Lexi_PHYS.md"
    if normalized in {"drewskii", "drewskii.engine"}:
        return "docs/models/Drewskii_Engine.md"
    raise HTTPException(status_code=404, detail="unknown model profile")


def slugify(text: str) -> str:
    clean = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip())
    return clean.strip("_") or "Lexi_AI_Brand"


def create_blueprint(name: str) -> Path:
    clean = name.strip() or "Custom AI Brand Blueprint Pack"
    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
    path = WORKSPACE_DIR / f"{slugify(clean)}_brand_blueprint.md"
    path.write_text(
        f"""# AI Brand Blueprint: {clean}

## Brand Identity
{clean} is a focused AI-powered concept built through Drewskii.Engine and Lexi.AI.

## Slogan
Built from signal. Designed for impact.

## Image Prompt
Create a cinematic brand poster for {clean}. Use dark technical lighting, white blueprint lines, clean typography, interface overlays, and a premium AI builder aesthetic.

## Ad Copy
Custom AI Brand Blueprint Packs start at $50. Message "BLUEPRINT" to start.
""",
        encoding="utf-8",
    )
    return path


@app.get("/health")
def health() -> dict:
    return {
        "ok": True,
        "system": "Drewskii.Engine",
        "mode": "safe user-space prototype",
    }


@app.get("/identity")
def identity() -> dict:
    return read_json("lexi_identity.json")


@app.get("/model")
def model() -> dict:
    return read_json("model_profiles/lexi_phys.json")


@app.get("/models")
def models() -> dict:
    return {
        "models": [
            read_json("model_profiles/lexi_phys.json"),
            read_json("model_profiles/drewskii_engine.json"),
        ]
    }


@app.get("/model/docs")
def model_docs() -> dict:
    return {"markdown": read_text("docs/models/Lexi_PHYS.md")}


@app.get("/model/{model_name}")
def named_model(model_name: str) -> dict:
    return read_json(model_profile_path(model_name))


@app.get("/model/{model_name}/docs")
def named_model_docs(model_name: str) -> dict:
    return {"markdown": read_text(model_docs_path(model_name))}


@app.get("/skills")
def skills() -> dict:
    return read_json("lexi_skills.json")


@app.get("/documentary")
def documentary() -> dict:
    return {"markdown": read_text("docs/lexi_documentary_map.md")}


@app.get("/top-layer")
def top_layer() -> dict:
    return {"markdown": read_text("docs/drewskii_engine_documentary_top_layer.md")}


@app.get("/experiments")
def experiments() -> dict:
    return {"experiments": list_experimental_concepts()}


@app.post("/experimental")
def experimental(request: ExperimentalRequest) -> dict:
    return create_experimental_concept(request.concept, title=request.title)


@app.post("/blueprint")
def blueprint(request: BlueprintRequest) -> dict:
    path = create_blueprint(request.name)
    return {
        "status": "success",
        "file": str(path),
        "markdown": path.read_text(encoding="utf-8"),
    }
