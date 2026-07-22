"""
OffensiveKaliLayer — constraint-pressure simulation (Lexi.PHYS / Drewskii.Engine).

CLASSIFICATION: RESEARCH PROTOTYPE / GOVERNANCE SIMULATION ONLY

Despite the martial metaphor (scan / escalate / penetrate / assault), this module
operates ONLY on abstract design and policy constraints:

  REGULATORY · PHYSICAL · MATERIAL · SOCIAL · TEMPORAL

It does NOT:
- run network reconnaissance against hosts
- perform privilege escalation on systems
- generate or launch exploits
- bypass security controls, authentication, or OS protections
- assist unauthorized access

"Penetration" means: estimated yield of a *constraint* under simulated
mass-density / curvature pressure from GravitationalProcessor.

Safe use: risk registers, design review, social/regulatory soft-force models,
Lexi.PHYS cinematic governance dashboards.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Iterable

import numpy as np

from .artifacts import WORKSPACE, ensure_dirs, slugify, utc_stamp, write_json, write_text
from .gravitational_processor import GravitationalProcessor


class ConstraintType(Enum):
    REGULATORY = "regulatory"
    PHYSICAL = "physical"
    MATERIAL = "material"
    SOCIAL = "social"
    TEMPORAL = "temporal"


# Base resistance (0–1) and which pressure axes matter most
_CONSTRAINT_PROFILE: dict[ConstraintType, dict[str, float]] = {
    ConstraintType.REGULATORY: {
        "base_resistance": 0.82,
        "mass_weight": 0.35,
        "curvature_weight": 0.40,
        "social_weight": 0.55,
    },
    ConstraintType.PHYSICAL: {
        "base_resistance": 0.90,
        "mass_weight": 0.85,
        "curvature_weight": 0.75,
        "social_weight": 0.05,
    },
    ConstraintType.MATERIAL: {
        "base_resistance": 0.78,
        "mass_weight": 0.70,
        "curvature_weight": 0.55,
        "social_weight": 0.10,
    },
    ConstraintType.SOCIAL: {
        "base_resistance": 0.55,
        "mass_weight": 0.25,
        "curvature_weight": 0.30,
        "social_weight": 0.90,
    },
    ConstraintType.TEMPORAL: {
        "base_resistance": 0.65,
        "mass_weight": 0.40,
        "curvature_weight": 0.50,
        "social_weight": 0.35,
    },
}


@dataclass
class Constraint:
    """A single design/policy constraint under simulation."""

    name: str
    type: ConstraintType
    strength: float = 1.0  # 0–2 relative hardness multiplier
    description: str = ""
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type.value,
            "strength": self.strength,
            "description": self.description,
            "tags": list(self.tags),
        }


@dataclass
class PenetrationReport:
    """Result of a full constraint-pressure simulation (not a system compromise)."""

    target_name: str
    mass_density: float
    grav_curvature: float
    status: str
    overall_yield: float
    constraints_scanned: int
    vectors: list[dict[str, Any]]
    social_realignment: dict[str, Any]
    blocked_operations: list[str]
    classification: str
    timestamp: str
    notes: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _as_constraint(item: Constraint | dict[str, Any] | str) -> Constraint:
    if isinstance(item, Constraint):
        return item
    if isinstance(item, str):
        # "TYPE:name" or bare name → SOCIAL default
        if ":" in item:
            t, n = item.split(":", 1)
            return Constraint(name=n.strip(), type=ConstraintType(t.strip().lower()))
        return Constraint(name=item, type=ConstraintType.SOCIAL)
    t = item.get("type", "social")
    if isinstance(t, ConstraintType):
        ctype = t
    else:
        ctype = ConstraintType(str(t).lower())
    return Constraint(
        name=str(item.get("name", "unnamed")),
        type=ctype,
        strength=float(item.get("strength", 1.0)),
        description=str(item.get("description", "")),
        tags=list(item.get("tags", [])),
    )


class OffensiveKaliLayer:
    """
    Constraint-pressure engine with martial method names (metaphor only).

    scan        → reconnaissance of constraint surface
    escalate    → raise effective pressure from mass/curvature
    penetrate   → single-vector constraint yield estimate
    realign_social_vectors → soft social pull model
    full_assault → multi-constraint PenetrationReport
    """

    BLOCKED = [
        "network host scanning / port scanning of third-party systems",
        "real privilege escalation on OS/accounts",
        "exploit generation or payload delivery",
        "security control bypass / unauthorized access",
        "credential theft or surveillance",
    ]

    def __init__(
        self,
        grav: GravitationalProcessor | None = None,
        rng_seed: int = 7,
        base_aggression: float = 0.75,
    ) -> None:
        self.grav = grav or GravitationalProcessor(rng_seed=rng_seed)
        self.rng = np.random.default_rng(rng_seed)
        # Design-pressure aggression (0–1). Not network attack aggression.
        self.base_aggression = float(np.clip(base_aggression, 0.0, 1.0))
        self.history: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Reconnaissance
    # ------------------------------------------------------------------
    def scan(self, constraints: Iterable[Constraint | dict[str, Any] | str]) -> list[dict]:
        """
        Reconnaissance of the *constraint surface* (not network recon).

        Returns structured findings: type, resistance, soft spots, tags.
        """
        findings: list[dict[str, Any]] = []
        for raw in constraints:
            c = _as_constraint(raw)
            profile = _CONSTRAINT_PROFILE[c.type]
            resistance = float(
                np.clip(profile["base_resistance"] * max(c.strength, 0.05), 0.0, 1.0)
            )
            soft_spot = 1.0 - resistance
            findings.append(
                {
                    "name": c.name,
                    "type": c.type.value,
                    "strength": c.strength,
                    "resistance": resistance,
                    "soft_spot": soft_spot,
                    "pressure_axes": {
                        "mass": profile["mass_weight"],
                        "curvature": profile["curvature_weight"],
                        "social": profile["social_weight"],
                    },
                    "description": c.description,
                    "tags": c.tags,
                    "recon_note": (
                        "Constraint surface map only — not a host/service scan."
                    ),
                }
            )
        # Sort softest first (where design pressure may yield first)
        findings.sort(key=lambda f: f["soft_spot"], reverse=True)
        return findings

    # ------------------------------------------------------------------
    # Privilege escalation (metaphor: pressure budget)
    # ------------------------------------------------------------------
    def escalate(self, mass_density: float, grav_curvature: float | None = None) -> dict[str, Any]:
        """
        Raise the simulation's effective pressure budget from mass + curvature.

        NOT OS privilege escalation.
        """
        report = self.grav.analyze_density(mass_density)
        kappa = (
            float(grav_curvature)
            if grav_curvature is not None
            else report.curvature
        )
        # Privilege tier in design space (0–1), scaled by base_aggression
        raw = 0.25 * report.step_scale + 0.55 * np.tanh(kappa / 3.0)
        pressure = float(np.clip(raw * (0.55 + 0.45 * self.base_aggression), 0.0, 1.0))
        tier = (
            "observer"
            if pressure < 0.33
            else "operator"
            if pressure < 0.66
            else "authoritative"
        )
        return {
            "metaphor": "privilege_escalation",
            "meaning": "elevated design-pressure budget under high mass/curvature",
            "mass_density": float(mass_density),
            "grav_curvature": kappa,
            "pressure_budget": pressure,
            "base_aggression": self.base_aggression,
            "tier": tier,
            "noise_rejection": 1.0 - report.noise_scale,
            "blocked_literal": "Does not escalate OS or account privileges.",
        }

    # ------------------------------------------------------------------
    # Single-vector override
    # ------------------------------------------------------------------
    def penetrate(
        self,
        constraint: Constraint | dict[str, Any] | str,
        mass_density: float,
        social_pull: float = 0.0,
        grav_curvature: float | None = None,
    ) -> dict[str, Any]:
        """
        Estimate whether a single constraint yields under pressure.

        Returns a yield score [0,1] and status — not a system breach.
        """
        c = _as_constraint(constraint)
        esc = self.escalate(mass_density, grav_curvature)
        profile = _CONSTRAINT_PROFILE[c.type]
        resistance = float(np.clip(profile["base_resistance"] * max(c.strength, 0.05), 0.0, 1.0))

        mass_term = esc["pressure_budget"] * profile["mass_weight"]
        curv_term = np.tanh(esc["grav_curvature"] / 3.0) * profile["curvature_weight"]
        social_term = float(np.clip(social_pull, 0.0, 1.0)) * profile["social_weight"]
        applied = float(
            np.clip(
                (0.45 * mass_term + 0.35 * curv_term + 0.35 * social_term)
                * (0.7 + 0.3 * self.base_aggression),
                0.0,
                1.5,
            )
        )

        # Yield when applied pressure exceeds resistance
        gap = applied - resistance
        yield_score = float(np.clip(0.5 + 1.25 * gap, 0.0, 1.0))
        # High curvature sharpens outcome (less ambiguous mid scores)
        soft = self.grav.analyze_density(mass_density).softness
        hard = 1.0 if yield_score >= 0.5 else 0.0
        yield_score = float((1.0 - soft) * hard + soft * yield_score)

        if yield_score >= 0.75:
            status = "YIELD"
        elif yield_score >= 0.45:
            status = "CONTESTED"
        else:
            status = "HOLD"

        return {
            "constraint": c.to_dict(),
            "status": status,
            "yield_score": yield_score,
            "resistance": resistance,
            "applied_pressure": applied,
            "mass_density": float(mass_density),
            "grav_curvature": esc["grav_curvature"],
            "social_pull": float(np.clip(social_pull, 0.0, 1.0)),
            "escalation_tier": esc["tier"],
            "interpretation": (
                f"Constraint '{c.name}' ({c.type.value}) is estimated to {status} "
                f"under simulated pressure — not a network/system compromise."
            ),
        }

    # ------------------------------------------------------------------
    # Social vector realignment
    # ------------------------------------------------------------------
    def realign_social_vectors(
        self,
        stakeholders: Iterable[str] | dict[str, float],
        mass_density: float,
        intent: str = "adoption",
        pull_strength: float = 0.6,
    ) -> dict[str, Any]:
        """
        Soft gravitational social pull model.

        Stakeholders shift alignment scores toward `intent` under mass-linked pull.
        Not manipulation malware — a planning heuristic for narrative/governance.
        """
        if isinstance(stakeholders, dict):
            scores = {str(k): float(np.clip(v, 0.0, 1.0)) for k, v in stakeholders.items()}
        else:
            # default neutral alignment
            scores = {str(s): 0.5 for s in stakeholders}

        report = self.grav.analyze_density(mass_density)
        # pull stronger when mass high (authoritative narrative gravity)
        pull = float(np.clip(pull_strength * (0.4 + 0.6 * report.step_scale), 0.0, 1.0))
        target = 0.85 if intent.lower() in {"adoption", "support", "align"} else 0.2

        after: dict[str, float] = {}
        deltas: dict[str, float] = {}
        for name, before in scores.items():
            # soft pull toward target; residual individuality remains
            new = (1.0 - pull) * before + pull * target
            # small stochastic jitter damped by curvature (noise rejection)
            jitter = float(self.rng.normal(0.0, report.noise_scale * 0.15))
            new = float(np.clip(new + jitter, 0.0, 1.0))
            after[name] = new
            deltas[name] = new - before

        return {
            "intent": intent,
            "mass_density": float(mass_density),
            "pull": pull,
            "curvature": report.curvature,
            "before": scores,
            "after": after,
            "deltas": deltas,
            "mean_delta": float(np.mean(list(deltas.values()))) if deltas else 0.0,
            "note": (
                "Social vector realignment is a planning simulation for messaging "
                "and stakeholder design — not covert influence tooling."
            ),
        }

    # ------------------------------------------------------------------
    # Full multi-constraint pressure run
    # ------------------------------------------------------------------
    def full_assault(
        self,
        target_name: str,
        constraints: Iterable[Constraint | dict[str, Any] | str],
        mass_density: float,
        social_pull: float = 0.5,
        stakeholders: Iterable[str] | dict[str, float] | None = None,
        write_artifacts: bool = True,
    ) -> PenetrationReport:
        """
        Full constraint-pressure campaign report.

        Martial naming is cinematic. Output is a governance/design risk report.
        """
        scanned = self.scan(constraints)
        esc = self.escalate(mass_density)
        vectors = [
            self.penetrate(
                {
                    "name": f["name"],
                    "type": f["type"],
                    "strength": f["strength"],
                    "description": f.get("description", ""),
                    "tags": f.get("tags", []),
                },
                mass_density=mass_density,
                social_pull=social_pull,
                grav_curvature=esc["grav_curvature"],
            )
            for f in scanned
        ]

        if stakeholders is None:
            stakeholders = [f"stakeholder_{i+1}" for i in range(min(3, max(1, len(scanned))))]
        social = self.realign_social_vectors(
            stakeholders, mass_density=mass_density, intent="adoption", pull_strength=social_pull
        )

        yields = [v["yield_score"] for v in vectors] or [0.0]
        overall = float(np.mean(yields))
        holds = sum(1 for v in vectors if v["status"] == "HOLD")
        yields_n = sum(1 for v in vectors if v["status"] == "YIELD")

        if overall >= 0.7 and yields_n >= holds:
            status = "CONSTRAINT_SURFACE_MALLEABLE"
        elif overall >= 0.4:
            status = "MIXED_RESISTANCE"
        else:
            status = "CONSTRAINT_SURFACE_HARD"

        report = PenetrationReport(
            target_name=target_name,
            mass_density=float(mass_density),
            grav_curvature=float(esc["grav_curvature"]),
            status=status,
            overall_yield=overall,
            constraints_scanned=len(scanned),
            vectors=vectors,
            social_realignment=social,
            blocked_operations=list(self.BLOCKED),
            classification="SIMULATION / GOVERNANCE ONLY — NOT OFFENSIVE SECURITY",
            timestamp=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            notes=(
                f"Simulated constraint pressure on '{target_name}'. "
                "No hosts scanned, no privileges escalated, no exploits run."
            ),
        )
        self.history.append(report.to_dict())

        if write_artifacts:
            self._write_report(report)

        return report

    def _write_report(self, report: PenetrationReport) -> dict[str, str]:
        ensure_dirs()
        out = WORKSPACE / "deliverables" / "simulations" / "constraint_kali"
        out.mkdir(parents=True, exist_ok=True)
        stamp = utc_stamp()
        slug = slugify(report.target_name)
        stem = f"{stamp}-{slug}-constraint_assault"
        md_path = out / f"{stem}.md"
        json_path = out / f"{stem}.json"

        lines = [
            f"# Constraint Pressure Report — {report.target_name}",
            "",
            f"**Classification:** {report.classification}",
            "",
            f"- Status: `{report.status}`",
            f"- Overall yield: `{report.overall_yield:.3f}`",
            f"- Mass density: `{report.mass_density}`",
            f"- Grav curvature: `{report.grav_curvature:.4g}`",
            f"- Constraints scanned: `{report.constraints_scanned}`",
            "",
            "## Blocked (literal offensive ops)",
        ]
        for b in report.blocked_operations:
            lines.append(f"- {b}")
        lines += ["", "## Vectors"]
        for v in report.vectors:
            c = v["constraint"]
            lines.append(
                f"- **{c['name']}** ({c['type']}): {v['status']} "
                f"yield={v['yield_score']:.3f} resistance={v['resistance']:.3f}"
            )
        lines += [
            "",
            "## Social realignment",
            f"- Mean delta: `{report.social_realignment.get('mean_delta', 0):.3f}`",
            f"- Pull: `{report.social_realignment.get('pull', 0):.3f}`",
            "",
            report.notes,
            "",
        ]
        write_text(md_path, "\n".join(lines))
        write_json(json_path, report.to_dict())
        return {"markdown": str(md_path), "json": str(json_path)}


def demo() -> str:
    layer = OffensiveKaliLayer()
    constraints = [
        Constraint("export_control_review", ConstraintType.REGULATORY, 1.2, "Trade compliance gate"),
        Constraint("thermal_limit", ConstraintType.PHYSICAL, 1.4, "Heat envelope"),
        Constraint("alloy_yield", ConstraintType.MATERIAL, 1.0, "Material strength floor"),
        Constraint("public_trust", ConstraintType.SOCIAL, 0.8, "Community acceptance"),
        Constraint("launch_window", ConstraintType.TEMPORAL, 0.9, "Schedule lock"),
    ]
    report = layer.full_assault(
        target_name="Lexi.PHYS Showcase Capsule",
        constraints=constraints,
        mass_density=16.5,
        social_pull=0.55,
        stakeholders={"ops": 0.4, "legal": 0.3, "community": 0.55},
        write_artifacts=True,
    )
    return (
        f"{report.classification}\n"
        f"target={report.target_name} status={report.status} "
        f"yield={report.overall_yield:.3f} vectors={report.constraints_scanned}\n"
        f"blocked={len(report.blocked_operations)} literal offensive ops"
    )


if __name__ == "__main__":
    print(demo())
