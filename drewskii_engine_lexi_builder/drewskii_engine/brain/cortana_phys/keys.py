"""
Local API key minting for CORTANA-PHYS.

These are *project-local* keys (HMAC-signed tokens), NOT stolen provider keys
and NOT real OpenAI/Anthropic/Google credentials.

Use:
- Authenticate local CORTANA-PHYS HTTP/CLI callers
- Scope model access (read / invent / admin)
- Rotate and revoke without touching cloud vendors
"""
from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..artifacts import PROJECT_ROOT, ensure_dirs, write_json


DEFAULT_VAULT = PROJECT_ROOT / "workspace" / "cortana_phys" / "key_vault.json"
SCOPES = ("models:read", "models:invent", "models:route", "admin:keys")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass
class ApiKeyRecord:
    key_id: str
    prefix: str
    label: str
    scopes: list[str]
    created_at: str
    expires_at: str | None = None
    revoked: bool = False
    meta: dict[str, Any] = field(default_factory=dict)
    # secret is only returned once at mint time; vault stores hash only
    secret_once: str | None = None

    def public_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d.pop("secret_once", None)
        return d


class CortanaKeyVault:
    """Mint, verify, list, and revoke CORTANA-PHYS API keys."""

    def __init__(
        self,
        vault_path: Path | None = None,
        master_secret: str | None = None,
    ) -> None:
        ensure_dirs()
        self.vault_path = Path(vault_path or DEFAULT_VAULT)
        self.vault_path.parent.mkdir(parents=True, exist_ok=True)
        self._master = master_secret or self._load_or_create_master()
        self._data = self._load()

    def _master_path(self) -> Path:
        return self.vault_path.parent / "master.secret"

    def _load_or_create_master(self) -> str:
        path = self._master_path()
        if path.exists():
            return path.read_text(encoding="utf-8").strip()
        secret = secrets.token_urlsafe(48)
        path.write_text(secret + "\n", encoding="utf-8")
        try:
            path.chmod(0o600)
        except OSError:
            pass
        return secret

    def _load(self) -> dict[str, Any]:
        if not self.vault_path.exists():
            return {"version": 1, "keys": {}}
        try:
            return json.loads(self.vault_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"version": 1, "keys": {}}

    def _save(self) -> None:
        write_json(self.vault_path, self._data)

    def _hash_secret(self, secret: str) -> str:
        return hmac.new(
            self._master.encode("utf-8"),
            secret.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def mint(
        self,
        label: str = "default",
        scopes: list[str] | None = None,
        ttl_seconds: int | None = None,
        meta: dict[str, Any] | None = None,
    ) -> ApiKeyRecord:
        """Create a new local API key. Secret is returned only once."""
        scopes = scopes or ["models:read", "models:route"]
        for s in scopes:
            if s not in SCOPES:
                raise ValueError(f"Unknown scope '{s}'. Allowed: {SCOPES}")

        key_id = "cph_" + secrets.token_hex(4)
        body = secrets.token_urlsafe(32)
        # Public format: cph_<id>.<secret>
        full = f"{key_id}.{body}"
        prefix = full[:18] + "…"
        expires_at = None
        if ttl_seconds:
            expires_at = datetime.fromtimestamp(
                time.time() + ttl_seconds, tz=timezone.utc
            ).replace(microsecond=0).isoformat()

        record = ApiKeyRecord(
            key_id=key_id,
            prefix=prefix,
            label=label,
            scopes=list(scopes),
            created_at=_utc_now(),
            expires_at=expires_at,
            revoked=False,
            meta=meta or {},
            secret_once=full,
        )
        self._data.setdefault("keys", {})[key_id] = {
            **record.public_dict(),
            "secret_hash": self._hash_secret(full),
        }
        self._save()
        return record

    def verify(self, api_key: str) -> dict[str, Any] | None:
        """Return key record if valid; else None."""
        api_key = (api_key or "").strip()
        if "." not in api_key or not api_key.startswith("cph_"):
            return None
        key_id = api_key.split(".", 1)[0]
        entry = self._data.get("keys", {}).get(key_id)
        if not entry or entry.get("revoked"):
            return None
        if entry.get("expires_at"):
            try:
                exp = datetime.fromisoformat(entry["expires_at"].replace("Z", "+00:00"))
                if datetime.now(timezone.utc) > exp:
                    return None
            except ValueError:
                return None
        expected = entry.get("secret_hash", "")
        actual = self._hash_secret(api_key)
        if not hmac.compare_digest(expected, actual):
            return None
        return {k: v for k, v in entry.items() if k != "secret_hash"}

    def revoke(self, key_id: str) -> bool:
        entry = self._data.get("keys", {}).get(key_id)
        if not entry:
            return False
        entry["revoked"] = True
        entry["revoked_at"] = _utc_now()
        self._save()
        return True

    def list_keys(self) -> list[dict[str, Any]]:
        out = []
        for entry in self._data.get("keys", {}).values():
            out.append({k: v for k, v in entry.items() if k != "secret_hash"})
        return sorted(out, key=lambda e: e.get("created_at", ""), reverse=True)

    def has_scope(self, api_key: str, scope: str) -> bool:
        rec = self.verify(api_key)
        if not rec:
            return False
        scopes = rec.get("scopes") or []
        return scope in scopes or "admin:keys" in scopes
