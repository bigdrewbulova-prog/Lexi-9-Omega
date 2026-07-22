from __future__ import annotations

import json
import re
from pathlib import Path

import streamlit as st

from drewskii_engine.brain.experimental import create_experimental_concept


ROOT = Path(__file__).resolve().parent
ENGINE_DIR = ROOT / "drewskii_engine"


def read_text(relative_path: str) -> str:
    return (ENGINE_DIR / relative_path).read_text(encoding="utf-8")


def read_json(relative_path: str) -> dict:
    return json.loads(read_text(relative_path))


def slugify(text: str) -> str:
    clean = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip())
    return clean.strip("_") or "Lexi_AI_Brand"


def create_blueprint(name: str) -> Path:
    clean = name.strip() or "Custom AI Brand Blueprint Pack"
    workspace = ENGINE_DIR / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)
    path = workspace / f"{slugify(clean)}_brand_blueprint.md"
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


st.set_page_config(page_title="Drewskii.Engine", page_icon="DE", layout="wide")
st.title("Drewskii.Engine")
st.caption("Top-layer documentary and builder kit for Lexi-9-Omega.")

identity = read_json("lexi_identity.json")
model_profile = read_json("model_profiles/lexi_phys.json")
drewskii_model_profile = read_json("model_profiles/drewskii_engine.json")
skills = read_json("lexi_skills.json")

left, middle, right = st.columns(3)
with left:
    st.subheader("Identity")
    st.json(identity)
with middle:
    st.subheader("Model")
    st.json({"profiles": [model_profile, drewskii_model_profile]})
with right:
    st.subheader("Skills")
    st.json(skills)

st.subheader("Generate Brand Blueprint")
name = st.text_input("Brand or project name", "Custom AI Brand Blueprint Pack")
if st.button("Generate Blueprint"):
    path = create_blueprint(name)
    st.success(f"Generated: {path}")
    st.markdown(path.read_text(encoding="utf-8"))

st.subheader("Archive Experimental Concept")
experiment_title = st.text_input("Experimental concept title", "Aethelweave")
experiment_text = st.text_area(
    "Concept text",
    "The Aethelweave represents a Lexi.PHYS structural-tailoring concept for simulation-only metamaterial visualization.",
)
if st.button("Archive Experimental Concept"):
    result = create_experimental_concept(experiment_text, title=experiment_title)
    st.success(f"Archived: {result['markdown']}")
    st.json(result)

st.subheader("Documentary Maps")
tab_one, tab_two = st.tabs(["Lexi-9-Omega", "Drewskii.Engine Top Layer"])
with tab_one:
    st.markdown(read_text("docs/lexi_documentary_map.md"))
with tab_two:
    st.markdown(read_text("docs/drewskii_engine_documentary_top_layer.md"))
