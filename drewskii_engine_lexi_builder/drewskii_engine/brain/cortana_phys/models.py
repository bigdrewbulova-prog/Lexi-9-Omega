"""CORTANA-PHYS model registry — inventable, inspectable model specs."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from ..artifacts import PROJECT_ROOT, ensure_dirs, slugify, utc_stamp, write_json, write_text

REGISTRY_PATH = PROJECT_ROOT / "workspace" / "cortana_phys" / "model_registry.json"


class ModelFamily(str, Enum):
    COMPANION = "companion"
    PHYS = "phys"
    BLUEPRINT = "blueprint"
    SIM = "sim"
    ROUTER = "router"
    CUSTOM = "custom"


@dataclass
class ModelSpec:
    model_id: str
    display_name: str
    family: ModelFamily
    version: str = "0.1.0"
    description: str = ""
    system_prompt: str = ""
    capabilities: list[str] = field(default_factory=list)
    input_modalities: list[str] = field(default_factory=lambda: ["text"])
    output_modalities: list[str] = field(default_factory=lambda: ["text", "json"])
    context_window: int = 8192
    temperature_default: float = 0.4
    provider_binding: str = "local-template"
    endpoint_hint: str = ""
    safety_profile: str = "drewskii_default"
    invented: bool = False
    source_module: str = "brain.cortana_phys.models"
    created_at: str = ""
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["family"] = self.family.value if isinstance(self.family, ModelFamily) else str(self.family)
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ModelSpec":
        fam = data.get("family", "custom")
        if not isinstance(fam, ModelFamily):
            fam = ModelFamily(str(fam))
        return cls(
            model_id=data["model_id"],
            display_name=data.get("display_name", data["model_id"]),
            family=fam,
            version=data.get("version", "0.1.0"),
            description=data.get("description", ""),
            system_prompt=data.get("system_prompt", ""),
            capabilities=list(data.get("capabilities", [])),
            input_modalities=list(data.get("input_modalities", ["text"])),
            output_modalities=list(data.get("output_modalities", ["text", "json"])),
            context_window=int(data.get("context_window", 8192)),
            temperature_default=float(data.get("temperature_default", 0.4)),
            provider_binding=data.get("provider_binding", "local-template"),
            endpoint_hint=data.get("endpoint_hint", ""),
            safety_profile=data.get("safety_profile", "drewskii_default"),
            invented=bool(data.get("invented", False)),
            source_module=data.get("source_module", "brain.cortana_phys.models"),
            created_at=data.get("created_at", ""),
            meta=dict(data.get("meta", {})),
        )


def _builtin_models() -> dict[str, ModelSpec]:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    specs = [
        ModelSpec(
            model_id="cortana-phys-core",
            display_name="CORTANA-PHYS Core",
            family=ModelFamily.PHYS,
            version="1.0.0",
            description="Geometry-first engineering companion; simulation-honest physics language.",
            system_prompt=(
                "You are CORTANA-PHYS. Prefer architecture, constraints, validation, and inspectable plans. "
                "Label speculative physics as simulation or concept design."
            ),
            capabilities=["plan", "simulate", "blueprint", "safety-check"],
            created_at=now,
        ),
        ModelSpec(
            model_id="cortana-companion",
            display_name="CORTANA Companion",
            family=ModelFamily.COMPANION,
            version="1.0.0",
            description="Operational assistant voice: clear, calm, command-ready.",
            system_prompt="You are CORTANA Companion for Drewskii.Engine. Be concise and actionable.",
            capabilities=["chat", "status", "checklist"],
            created_at=now,
        ),
        ModelSpec(
            model_id="cortana-blueprint-forge",
            display_name="CORTANA Blueprint Forge",
            family=ModelFamily.BLUEPRINT,
            version="1.0.0",
            description="Brand and product pack generator for $50 Blueprint offers.",
            system_prompt=(
                "Generate Custom AI Brand Blueprint Packs: name, bio, slogan, image prompts, "
                "ad copy, one-page concept sheet."
            ),
            capabilities=["brand-pack", "ad-copy", "concept-sheet"],
            created_at=now,
        ),
        ModelSpec(
            model_id="cortana-mastermind-sim",
            display_name="CORTANA Mastermind Sim",
            family=ModelFamily.SIM,
            version="1.0.0",
            description="Simulation cycle language only.",
            system_prompt="Narrate Mastermind simulation cycles only. Never claim real network attacks.",
            capabilities=["retro", "grav", "constraint-pressure", "report"],
            created_at=now,
        ),
        ModelSpec(
            model_id="cortana-router-omega",
            display_name="CORTANA Router Ω",
            family=ModelFamily.ROUTER,
            version="1.0.0",
            description="Selects which CORTANA-PHYS module handles a request.",
            system_prompt="Classify intent and pick the best cortana-* model_id.",
            capabilities=["route", "classify"],
            created_at=now,
        ),
    ]
    return {s.model_id: s for s in specs}


class ModelRegistry:
    def __init__(self, path: Path | None = None) -> None:
        ensure_dirs()
        self.path = Path(path or REGISTRY_PATH)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._models: dict[str, ModelSpec] = {}
        self._load()

    def _load(self) -> None:
        self._models = _builtin_models()
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                for item in data.get("models", []):
                    spec = ModelSpec.from_dict(item)
                    self._models[spec.model_id] = spec
            except (json.JSONDecodeError, KeyError, ValueError):
                pass

    def save(self) -> Path:
        payload = {
            "version": 1,
            "updated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "models": [m.to_dict() for m in sorted(self._models.values(), key=lambda x: x.model_id)],
        }
        write_json(self.path, payload)
        return self.path

    def list_models(self) -> list[ModelSpec]:
        return sorted(self._models.values(), key=lambda m: m.model_id)

    def get(self, model_id: str) -> ModelSpec | None:
        return self._models.get(model_id)

    def invent(
        self,
        name: str,
        family: str | ModelFamily = ModelFamily.CUSTOM,
        description: str = "",
        capabilities: list[str] | None = None,
        system_prompt: str | None = None,
        provider_binding: str = "local-template",
    ) -> ModelSpec:
        base = slugify(name).lower().replace("_", "-")
        model_id = f"cortana-{base}" if not base.startswith("cortana-") else base
        if model_id in self._models:
            model_id = f"{model_id}-{utc_stamp()[-6:]}"
        if not isinstance(family, ModelFamily):
            try:
                family = ModelFamily(str(family).lower())
            except ValueError:
                family = ModelFamily.CUSTOM
        caps = capabilities or ["chat", "plan", "json-out"]
        prompt = system_prompt or (
            f"You are {name}, a CORTANA-PHYS module. Family={family.value}. "
            f"Be practical and safety-bounded. Capabilities: {', '.join(caps)}."
        )
        now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        spec = ModelSpec(
            model_id=model_id,
            display_name=name,
            family=family,
            description=description or f"Invented module: {name}",
            system_prompt=prompt,
            capabilities=caps,
            provider_binding=provider_binding,
            invented=True,
            source_module=f"brain.cortana_phys.generated.{slugify(model_id)}",
            created_at=now,
            meta={"invented_by": "ModelRegistry.invent"},
        )
        self._models[model_id] = spec
        self._write_source_stub(spec)
        self.save()
        return spec

    def _write_source_stub(self, spec: ModelSpec) -> Path:
        gen_dir = PROJECT_ROOT / "brain" / "cortana_phys" / "generated"
        gen_dir.mkdir(parents=True, exist_ok=True)
        init = gen_dir / "__init__.py"
        if not init.exists():
            init.write_text('"""Auto-generated CORTANA-PHYS model modules."""\n', encoding="utf-8")
        mod_name = slugify(spec.model_id)
        path = gen_dir / f"{mod_name}.py"
        code = f'''"""Auto-generated CORTANA-PHYS model: {spec.model_id}"""
from __future__ import annotations
from typing import Any

MODEL_ID = {spec.model_id!r}
DISPLAY_NAME = {spec.display_name!r}
SYSTEM_PROMPT = {spec.system_prompt!r}
CAPABILITIES = {spec.capabilities!r}


def describe() -> dict[str, Any]:
    return {{"model_id": MODEL_ID, "display_name": DISPLAY_NAME, "capabilities": CAPABILITIES}}


def complete(prompt: str, **kwargs: Any) -> dict[str, Any]:
    text = f"[{{DISPLAY_NAME}}] {{SYSTEM_PROMPT[:120]}}...\\nUser: {{prompt}}\\nAssistant: (template) acknowledged."
    return {{"model_id": MODEL_ID, "output": text, "template": True, "kwargs": kwargs}}
'''
        write_text(path, code)
        write_json(gen_dir / f"{mod_name}.json", spec.to_dict())
        return path
