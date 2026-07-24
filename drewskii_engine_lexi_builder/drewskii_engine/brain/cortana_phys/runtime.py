"""
CORTANA-PHYS core runtime — keys + models + router in one façade.
"""
from __future__ import annotations

from typing import Any

from .keys import CortanaKeyVault, SCOPES
from .models import ModelFamily, ModelRegistry, ModelSpec
from .router import CortanaPhysRouter, ModelRequest, ModelResponse


class CortanaPhysCore:
    """
    Top-level CORTANA-PHYS interface for Drewskii.Engine CLI and apps.
    """

    def __init__(self) -> None:
        self.vault = CortanaKeyVault()
        self.registry = ModelRegistry()
        self.router = CortanaPhysRouter(registry=self.registry, vault=self.vault)

    # ---- keys ----
    def mint_key(
        self,
        label: str = "cortana-local",
        scopes: list[str] | None = None,
        ttl_seconds: int | None = None,
    ) -> dict[str, Any]:
        scopes = scopes or ["models:read", "models:route", "models:invent"]
        rec = self.vault.mint(label=label, scopes=scopes, ttl_seconds=ttl_seconds)
        return {
            "key_id": rec.key_id,
            "api_key": rec.secret_once,  # show once
            "prefix": rec.prefix,
            "scopes": rec.scopes,
            "created_at": rec.created_at,
            "expires_at": rec.expires_at,
            "warning": "Store this API key now. It will not be shown again.",
            "note": "Local CORTANA-PHYS key — not an OpenAI/Google/Anthropic cloud key.",
        }

    def list_keys(self) -> list[dict[str, Any]]:
        return self.vault.list_keys()

    def revoke_key(self, key_id: str) -> bool:
        return self.vault.revoke(key_id)

    # ---- models ----
    def list_models(self) -> list[dict[str, Any]]:
        return [m.to_dict() for m in self.registry.list_models()]

    def invent_model(
        self,
        name: str,
        family: str = "custom",
        description: str = "",
        capabilities: list[str] | None = None,
    ) -> dict[str, Any]:
        spec = self.registry.invent(
            name=name,
            family=family,
            description=description,
            capabilities=capabilities,
        )
        return spec.to_dict()

    def get_model(self, model_id: str) -> dict[str, Any] | None:
        m = self.registry.get(model_id)
        return m.to_dict() if m else None

    # ---- route ----
    def complete(
        self,
        prompt: str,
        model_id: str | None = None,
        api_key: str | None = None,
    ) -> dict[str, Any]:
        resp: ModelResponse = self.router.route(
            ModelRequest(prompt=prompt, model_id=model_id, api_key=api_key)
        )
        return resp.to_dict()

    def status(self) -> dict[str, Any]:
        return {
            "system": "CORTANA-PHYS",
            "models": len(self.registry.list_models()),
            "keys": len(self.vault.list_keys()),
            "scopes_available": list(SCOPES),
            "families": [f.value for f in ModelFamily],
            "registry_path": str(self.registry.path),
            "vault_path": str(self.vault.vault_path),
        }
