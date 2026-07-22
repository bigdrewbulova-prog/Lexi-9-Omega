from __future__ import annotations

import re
import uuid
from typing import Any

from .memory import LocalMemory
from .models import utc_now_iso
from .safety import slugify_project_name, validate_project_name


class OpenVASManager:
    """Owner-approved security scan planner.

    This first build deliberately does **not** launch Docker, OpenVAS, or any
    network scanner. It validates inputs, produces a reviewable plan, and logs
    owner-approved scan *requests* for later manual execution.
    """

    ALLOWED_TEMPLATES = {
        "Full and fast",
        "Discovery",
        "Host Discovery",
        "System Discovery",
        "Full and very deep ultimate",
    }

    def __init__(self, memory: LocalMemory) -> None:
        self.memory = memory

    def preview_scan(self, project_name: str, target: str, template: str) -> dict[str, Any]:
        return self._build_plan(project_name, target, template, stage="preview")

    def prepare_scan(self, project_name: str, target: str, template: str) -> dict[str, Any]:
        plan = self._build_plan(project_name, target, template, stage="prepared")
        self.memory.log_event(
            "scan_prepared",
            {
                "project": plan["project_name"],
                "target": plan["target"],
                "template": plan["template"],
            },
        )
        return plan

    def request_scan(
        self,
        project_name: str,
        target: str,
        template: str,
        owner_approved: bool = False,
    ) -> dict[str, Any]:
        if not owner_approved:
            raise PermissionError("Owner approval is required before a scan can be requested.")

        plan = self._build_plan(project_name, target, template, stage="requested")
        scan_id = f"LEXI-SCAN-{uuid.uuid4().hex[:10].upper()}"

        result = {
            **plan,
            "scan_id": scan_id,
            "status": "requested_not_started",
            "execution_mode": "manual_only",
            "message": (
                "Scan request logged. This build does not start OpenVAS/Docker. "
                "Use the plan below for an owner-run scan outside Lexi."
            ),
            "next_steps": [
                "Review target ownership and legal authorization.",
                "If approved, run your scanner manually against the listed target.",
                "Store export artifacts under the project workspace when complete.",
            ],
            "requested_at": utc_now_iso(),
        }

        self.memory.log_event(
            "scan_requested",
            {
                "project": result["project_name"],
                "scan_id": scan_id,
                "target": result["target"],
                "template": result["template"],
                "owner_approved": True,
            },
        )
        return result

    def _build_plan(
        self,
        project_name: str,
        target: str,
        template: str,
        stage: str,
    ) -> dict[str, Any]:
        ok, message = validate_project_name(project_name)
        if not ok:
            raise ValueError(message)

        clean_target = self._validate_target(target)
        clean_template = self._validate_template(template)
        slug = slugify_project_name(project_name)

        return {
            "stage": stage,
            "project_name": project_name.strip(),
            "project_slug": slug,
            "target": clean_target,
            "template": clean_template,
            "scanner": "OpenVAS (planned / not auto-executed)",
            "runtime": "docker (optional, owner-operated)",
            "requires_owner_approval": True,
            "auto_execute": False,
            "safety": {
                "shell_execution": False,
                "network_scan_from_lexi": False,
                "destructive_actions": False,
                "note": "Lexi only plans and logs. It never launches scanners itself.",
            },
            "created_at": utc_now_iso(),
        }

    def _validate_target(self, target: str) -> str:
        value = (target or "").strip()
        if not value:
            raise ValueError("Scan target is required.")

        if len(value) > 253:
            raise ValueError("Scan target is too long.")

        # Block shell metacharacters and path-style payloads.
        if re.search(r"[;&|`$<>\\\s]", value):
            raise ValueError("Scan target contains blocked characters.")

        if ".." in value or "/" in value or "\\" in value:
            raise ValueError("Scan target must be a host or IP, not a path.")

        # IPv4
        if re.fullmatch(r"(?:\d{1,3}\.){3}\d{1,3}", value):
            octets = [int(part) for part in value.split(".")]
            if any(octet > 255 for octet in octets):
                raise ValueError("Invalid IPv4 address.")
            return value

        # Hostname / localhost
        if re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)*", value):
            return value

        raise ValueError("Scan target must be a valid hostname or IPv4 address.")

    def _validate_template(self, template: str) -> str:
        value = (template or "").strip() or "Full and fast"
        if len(value) > 80:
            raise ValueError("Scan template name is too long.")

        # Accept known templates and reasonable free-text labels.
        if value in self.ALLOWED_TEMPLATES:
            return value

        if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 ._-]{0,78}", value):
            return value

        raise ValueError("Scan template contains invalid characters.")
