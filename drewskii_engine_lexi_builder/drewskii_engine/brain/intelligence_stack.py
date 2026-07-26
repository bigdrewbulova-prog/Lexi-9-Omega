"""
Local-First Intelligence Model Stack — Stage 1 automation façade.

Operating rule:
  Run Lexi.AI as a safe user-space prototype first. Promote to official app
  features only after useful, repeatable, permission-safe, and testable.

Stage 1 (this module):
  - CLI planning + SQLite project memory
  - AI Brand Blueprint Pack generator ($50 product path)
  - Documentary + offer mapping
  - MD / JSON / HTML / SQLite outputs
  - Web dashboard shell
  - Termux helpers (approval-gated drafts only)
  - Evaluation logs
  - CORTANA-PHYS local model stack + keys

Blocked:
  hidden accounts, passwords, bypass, surveillance, OS control outside APIs,
  speculative physics as finished hardware.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .artifacts import DASHBOARD_DATA, PROJECT_ROOT, WORKSPACE, ensure_dirs, write_json
from .blueprint_forge import forge_blueprint
from .code_generator import generate_ui_shell
from .documentary import export_documentary_map, export_offer_map
from .eval_log import log_evaluation
from .logger import log_event
from .memory import Memory
from .planner import save_plan
from .safety import is_blocked


STAGE1_FEATURES = [
    "local_cli_planning",
    "project_memory_sqlite",
    "brand_blueprint_pack",
    "documentary_map",
    "offer_map",
    "outputs_md_json_html_sqlite",
    "web_dashboard_shell",
    "termux_helpers_approved_only",
    "evaluation_logs",
    "cortana_phys_models_and_keys",
]

STAGE2_LATER = [
    "native_android_screens",
    "share_sheet_file_import",
    "notification_reminders",
    "sqlite_pack_library_ui",
    "oauth_account_sync",
    "permission_screens",
    "export_pdf_zip",
    "payment_and_customers",
    "test_evaluation_dashboard_native",
]

PROMOTION_GATE = [
    "clear_user_value",
    "explicit_permissions",
    "stable_io_format",
    "local_error_handling",
    "tests_or_manual_validation",
    "privacy_and_safety_notes",
    "rollback_path",
]


@dataclass
class BrandIntake:
    project_type: str = "personal brand"
    name: str = "Custom AI Brand Blueprint Pack"
    vibe: str = "dark, clean, futuristic"
    audience: str = "creators and small businesses"
    offer: str = "identity pack: name, bio, slogan, visuals, ads"
    colors: str = "void black · blueprint white · ultraviolet · acid green"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def validate(self) -> list[str]:
        """Return list of validation errors (empty = ok)."""
        errors: list[str] = []
        name = (self.name or "").strip()
        if not name:
            errors.append("name is required")
        elif len(name) > 120:
            errors.append("name must be 120 characters or fewer")
        if not (self.vibe or "").strip():
            errors.append("vibe is required")
        if not (self.audience or "").strip():
            errors.append("audience is required")
        if not (self.offer or "").strip():
            errors.append("offer is required")
        for field_name in ("vibe", "audience", "offer", "colors", "project_type"):
            val = getattr(self, field_name) or ""
            if len(val) > 500:
                errors.append(f"{field_name} must be 500 characters or fewer")
        return errors


@dataclass
class QualityChecklist:
    has_name: bool = False
    has_bio: bool = False
    has_slogan: bool = False
    has_image_prompts: bool = False
    has_ad_copy: bool = False
    has_concept_sheet: bool = False
    claim_boundary_ok: bool = True
    local_files_saved: bool = False
    notes: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(
            [
                self.has_name,
                self.has_bio,
                self.has_slogan,
                self.has_image_prompts,
                self.has_ad_copy,
                self.has_concept_sheet,
                self.claim_boundary_ok,
                self.local_files_saved,
            ]
        )

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["passed"] = self.passed
        return d


class LocalFirstIntelligenceStack:
    """Stage-1 automation orchestrator for the full local-first model stack."""

    STAGE = 1
    CLASSIFICATION = (
        "STAGE-1 USER-SPACE PROTOTYPE — not privileged OS control, not finished exotic hardware"
    )

    def __init__(self, memory: Memory | None = None) -> None:
        ensure_dirs()
        self.memory = memory or Memory(PROJECT_ROOT / "memory" / "drewskii_memory.db")
        self._cortana = None

    @property
    def cortana(self):
        if self._cortana is None:
            from .cortana_phys import CortanaPhysCore

            self._cortana = CortanaPhysCore()
        return self._cortana

    def operating_rules(self) -> dict[str, Any]:
        return {
            "operating_rule": (
                "Run Lexi.AI as a safe user-space prototype first. "
                "Build official app features only after useful, repeatable, permission-safe, and testable."
            ),
            "stage": self.STAGE,
            "classification": self.CLASSIFICATION,
            "stage1_build_now": STAGE1_FEATURES,
            "stage2_build_later": STAGE2_LATER,
            "promotion_gate": PROMOTION_GATE,
            "allowed": [
                "read/write user-selected local project files",
                "Termux:API / intents with explicit approval",
                "local memory",
                "drafts, plans, code for review",
            ],
            "blocked": [
                "hidden account access",
                "password collection",
                "security bypass",
                "background surveillance",
                "OS control outside official APIs",
                "speculative physics as finished hardware",
            ],
            "first_product": {
                "name": "Custom AI Brand Blueprint Packs",
                "price_starting_usd": 50,
                "cta": "BLUEPRINT",
            },
        }

    def brand_pack(
        self,
        intake: BrandIntake | dict[str, str] | None = None,
        include_code: bool = True,
    ) -> dict[str, Any]:
        """First product path: capture intake → forge pack → quality checklist → SQLite."""
        if intake is None:
            intake = BrandIntake()
        elif isinstance(intake, dict):
            intake = BrandIntake(**{k: intake[k] for k in BrandIntake.__dataclass_fields__ if k in intake})

        errors = intake.validate()
        if errors:
            raise ValueError("Invalid intake: " + "; ".join(errors))
        if is_blocked(json.dumps(intake.to_dict())):
            raise PermissionError("Intake crosses a blocked safety boundary.")

        result = forge_blueprint(
            intake.name,
            vibe=f"{intake.vibe}; colors={intake.colors}; type={intake.project_type}",
            audience=intake.audience,
            offer=intake.offer,
            include_code=include_code,
            memory=self.memory,
        )
        data = result["data"]
        paths = result["paths"]
        zip_ok = bool(paths.get("zip") and Path(paths["zip"]).is_file())
        checklist = QualityChecklist(
            has_name=bool(data.get("brand_name")),
            has_bio=bool(data.get("bio")),
            has_slogan=bool(data.get("slogan")),
            has_image_prompts=bool(data.get("image_prompts")),
            has_ad_copy=bool(data.get("ad_copy")),
            has_concept_sheet=bool(data.get("concept_sheet")),
            claim_boundary_ok=True,
            local_files_saved=bool(paths) and zip_ok,
            notes=[
                "Stage-1 prototype quality gate for $50 pack path",
                "ZIP package included for customer delivery",
            ],
        )
        self.memory.set(
            f"brand_intake_{data.get('brand_name', 'pack')}",
            json.dumps(
                {
                    "intake": intake.to_dict(),
                    "paths": paths,
                    "zip": paths.get("zip"),
                    "checklist": checklist.to_dict(),
                },
                ensure_ascii=True,
            ),
        )
        log_evaluation(
            self.memory,
            category="product",
            subject=f"brand_pack:{data.get('brand_name')}",
            notes="Stage-1 brand pack generated with quality checklist + ZIP",
            score=1.0 if checklist.passed else 0.6,
            payload={"checklist": checklist.to_dict(), "paths": paths, "zip": paths.get("zip")},
        )
        log_event(f"stack_brand_pack passed={checklist.passed} name={data.get('brand_name')} zip={zip_ok}")
        return {
            "intake": intake.to_dict(),
            "pack": result,
            "quality_checklist": checklist.to_dict(),
            "zip": paths.get("zip"),
            "promotion_ready": checklist.passed,  # still needs gate review for Stage 2
            "stage": 1,
            "delivery": {
                "format": "zip",
                "price_starting_usd": 50,
                "cta": "BLUEPRINT",
                "customer_files": ["README.md", "brand_pack.md", "brand_pack.html", "brand_pack.json"],
            },
        }

    def full_stage1_run(
        self,
        *,
        brand_name: str = "Lexi Local-First Intelligence",
        plan_idea: str = "Automate Stage-1 local-first intelligence model stack",
        mint_key: bool = True,
    ) -> dict[str, Any]:
        """
        Run the full Stage-1 automation pipeline once and write dashboard stats.
        """
        ensure_dirs()
        report: dict[str, Any] = {
            "classification": self.CLASSIFICATION,
            "started_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "steps": {},
        }

        # 1. Plan + memory
        plan = save_plan(self.memory, plan_idea)
        report["steps"]["plan"] = {"plan_id": plan["plan_id"], "paths": plan["paths"]}

        # 2. Brand blueprint product path
        pack = self.brand_pack(
            BrandIntake(
                project_type="AI product brand",
                name=brand_name,
                vibe="local-first, sovereign, inspectable",
                audience="developers and founders",
                offer="Custom AI Brand Blueprint Packs starting at $50",
                colors="void black · acid green · ultraviolet",
            )
        )
        report["steps"]["brand_pack"] = {
            "quality": pack["quality_checklist"],
            "paths": pack["pack"]["paths"],
            "zip": pack.get("zip"),
            "delivery": pack.get("delivery"),
        }

        # 3. Documentary + offer maps
        doc = export_documentary_map(memory=self.memory)
        offer = export_offer_map(memory=self.memory)
        report["steps"]["documentary_map"] = doc["paths"]
        report["steps"]["offer_map"] = offer["paths"]

        # 4. Dashboard shell
        ui = generate_ui_shell()
        report["steps"]["dashboard"] = str(ui)

        # 5. CORTANA-PHYS models + optional key
        cortana_status = self.cortana.status()
        report["steps"]["cortana"] = cortana_status
        if mint_key:
            key = self.cortana.mint_key(label="stage1-stack")
            report["steps"]["cortana_key"] = {
                "key_id": key["key_id"],
                "warning": key["warning"],
                "note": key["note"],
                # secret returned once for operator; not written to public dashboard
                "api_key_once": key["api_key"],
            }

        # 6. Termux helpers catalog (no auto-execute)
        from android.termux_helpers import list_helpers

        report["steps"]["termux_helpers"] = {
            "count": len(list_helpers()),
            "ids": [h["id"] for h in list_helpers()],
            "execution": "manual_approval_only",
        }

        # 7. Stats + dashboard index
        stats = self.memory.stats()
        report["stats"] = stats
        report["operating_rules"] = self.operating_rules()
        report["promotion_gate"] = {
            "required": PROMOTION_GATE,
            "brand_pack_checklist_passed": pack["quality_checklist"]["passed"],
            "stage2_blocked_until": "explicit promotion review",
        }

        self._refresh_dashboard(report)
        out_path = WORKSPACE / "stack" / "stage1_full_run.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        # strip one-time key from disk public report if present — keep in return only
        disk_report = json.loads(json.dumps(report))
        if "cortana_key" in disk_report.get("steps", {}):
            disk_report["steps"]["cortana_key"].pop("api_key_once", None)
        write_json(out_path, disk_report)
        report["artifact_path"] = str(out_path)
        report["finished_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        log_event("stack_stage1_full_run_complete")
        return report

    def _refresh_dashboard(self, report: dict[str, Any]) -> None:
        ensure_dirs()
        index: dict[str, Any] = {}
        if DASHBOARD_DATA.exists():
            try:
                index = json.loads(DASHBOARD_DATA.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                index = {}
        index["stats"] = report.get("stats", self.memory.stats())
        index["stack"] = {
            "stage": 1,
            "classification": self.CLASSIFICATION,
            "last_full_run": report.get("finished_at") or report.get("started_at"),
            "features": STAGE1_FEATURES,
        }
        index["updated_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        index["system"] = "Local-First Intelligence Model Stack"
        # keep recent deliverables if present
        write_json(DASHBOARD_DATA, index)

    def promotion_review(self, feature: str, evidence: dict[str, bool] | None = None) -> dict[str, Any]:
        """Check whether a Stage-1 feature meets the promotion gate (manual evidence)."""
        evidence = evidence or {}
        missing = [g for g in PROMOTION_GATE if not evidence.get(g)]
        return {
            "feature": feature,
            "can_promote_to_stage2": len(missing) == 0,
            "missing": missing,
            "gate": PROMOTION_GATE,
            "note": "No auto-promotion. Operator must supply evidence flags.",
        }


def demo() -> dict[str, Any]:
    stack = LocalFirstIntelligenceStack()
    return stack.full_stage1_run(mint_key=True)


if __name__ == "__main__":
    result = demo()
    # never print full API key in casual logs if present
    if "cortana_key" in result.get("steps", {}):
        key = result["steps"]["cortana_key"].get("api_key_once")
        if key:
            result["steps"]["cortana_key"]["api_key_once"] = key[:20] + "…"
    print(json.dumps({k: result[k] for k in result if k != "operating_rules"}, indent=2, default=str))
