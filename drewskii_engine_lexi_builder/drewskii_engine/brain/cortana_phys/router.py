"""Route prompts to CORTANA-PHYS model modules."""
from __future__ import annotations

import importlib
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from .keys import CortanaKeyVault
from .models import ModelRegistry, ModelSpec


@dataclass
class ModelRequest:
    prompt: str
    model_id: str | None = None
    api_key: str | None = None
    temperature: float | None = None
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelResponse:
    model_id: str
    output: str
    routed_by: str
    template: bool
    timestamp: str
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CortanaPhysRouter:
    def __init__(
        self,
        registry: ModelRegistry | None = None,
        vault: CortanaKeyVault | None = None,
    ) -> None:
        self.registry = registry or ModelRegistry()
        self.vault = vault or CortanaKeyVault()

    def classify(self, prompt: str) -> str:
        p = (prompt or "").lower()
        rules = [
            (r"\b(brand|blueprint|slogan|ad copy|offer)\b", "cortana-blueprint-forge"),
            (r"\b(mastermind|retro|curvature|constraint|kali|grav)\b", "cortana-mastermind-sim"),
            (r"\b(route|which model|pick model)\b", "cortana-router-omega"),
            (r"\b(physics|structure|geometry|simulate|stress|material)\b", "cortana-phys-core"),
            (r"\b(status|help|checklist|remind)\b", "cortana-companion"),
        ]
        for pattern, model_id in rules:
            if re.search(pattern, p):
                return model_id
        return "cortana-phys-core"

    def route(self, request: ModelRequest) -> ModelResponse:
        if request.api_key:
            if not self.vault.verify(request.api_key):
                raise PermissionError("Invalid or revoked CORTANA-PHYS API key.")
            if not (
                self.vault.has_scope(request.api_key, "models:route")
                or self.vault.has_scope(request.api_key, "models:read")
            ):
                raise PermissionError("API key missing models:route or models:read scope.")

        model_id = request.model_id or self.classify(request.prompt)
        spec = self.registry.get(model_id) or self.registry.get("cortana-phys-core")
        assert spec is not None
        model_id = spec.model_id
        output, template, meta = self._complete(spec, request)
        return ModelResponse(
            model_id=model_id,
            output=output,
            routed_by="classify" if not request.model_id else "explicit",
            template=template,
            timestamp=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            meta=meta,
        )

    def _complete(self, spec: ModelSpec, request: ModelRequest) -> tuple[str, bool, dict[str, Any]]:
        if spec.invented or spec.source_module.startswith("brain.cortana_phys.generated"):
            mod_name = spec.model_id.replace("-", "_")
            try:
                mod = importlib.import_module(f"brain.cortana_phys.generated.{mod_name}")
                result = mod.complete(request.prompt, temperature=request.temperature)
                return str(result.get("output", "")), bool(result.get("template", True)), {
                    "provider_binding": result.get("provider_binding"),
                    "generated": True,
                }
            except Exception as exc:
                meta_err = {"generated_import_error": str(exc)}
        else:
            meta_err = {}

        temp = request.temperature if request.temperature is not None else spec.temperature_default
        text = (
            f"[{spec.display_name} · {spec.model_id} v{spec.version}]\n"
            f"Family: {spec.family.value} · binding: {spec.provider_binding} · T={temp}\n\n"
            f"System: {spec.system_prompt}\n\n"
            f"User: {request.prompt}\n\n"
            f"Assistant: Template response from CORTANA-PHYS. "
            f"Capabilities={spec.capabilities}. Safety={spec.safety_profile}."
        )
        return text, True, {"provider_binding": spec.provider_binding, **meta_err}
