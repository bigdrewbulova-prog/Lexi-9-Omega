"""
MastermindCore — full Lexi.PHYS simulation cycle orchestrator.

Pipeline:
  1. RetroCausalEngine     → goal-conditioned parameter optimize
  2. GravitationalProcessor → density→curvature, logic, opt dynamics
  3. OffensiveKaliLayer    → constraint-pressure report (governance sim)

CLASSIFICATION: SIMULATION / GOVERNANCE / RESEARCH PROTOTYPE ONLY

Does not:
- perform real network attacks
- claim physical retrocausality or gravity hardware
- bypass security controls
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

import numpy as np

from .artifacts import WORKSPACE, ensure_dirs, slugify, utc_stamp, write_json, write_text
from .gravitational_processor import GravitationalProcessor
from .offensive_kali_layer import (
    Constraint,
    ConstraintType,
    OffensiveKaliLayer,
    PenetrationReport,
)
from .retro_causal import CurrentParams, FutureState, RetroCausalEngine


DEFAULT_CONSTRAINTS: list[Constraint] = [
    Constraint("export_control_review", ConstraintType.REGULATORY, 1.2, "Trade / claims compliance"),
    Constraint("thermal_envelope", ConstraintType.PHYSICAL, 1.35, "Heat / energy envelope"),
    Constraint("material_yield_floor", ConstraintType.MATERIAL, 1.05, "Material strength floor"),
    Constraint("public_trust", ConstraintType.SOCIAL, 0.85, "Audience / community acceptance"),
    Constraint("launch_window", ConstraintType.TEMPORAL, 0.95, "Schedule lock"),
]


@dataclass
class MastermindCycleReport:
    target_name: str
    target_mass: float
    target_authority: float
    status: str
    retro: dict[str, Any]
    grav: dict[str, Any]
    kali: dict[str, Any]
    optimized_params: dict[str, Any]
    classification: str
    timestamp: str
    artifact_paths: dict[str, str] = field(default_factory=dict)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class MastermindCore:
    """
    Top-level simulation conductor for Drewskii.Engine / Lexi.PHYS.

    full_cycle():
      1. Retro-Causal → optimized parameters from future targets
      2. Gravitational Processing → curvature logic + density dynamics
      3. Offensive Kali → full constraint-pressure assault (metaphor)
    """

    def __init__(
        self,
        *,
        micro_window: float = 1e-12,
        consistency_threshold: float = 0.08,
        max_iters: int = 120,
        base_aggression: float = 0.93,
        rng_seed: int = 9,
    ) -> None:
        self.retro = RetroCausalEngine(
            micro_window=micro_window,
            consistency_threshold=consistency_threshold,
            max_iters=max_iters,
            rng_seed=rng_seed,
        )
        self.grav = GravitationalProcessor(rng_seed=rng_seed)
        self.kali = OffensiveKaliLayer(
            grav=self.grav,
            rng_seed=rng_seed,
            base_aggression=base_aggression,
        )
        self.history: list[dict[str, Any]] = []

    def full_cycle(
        self,
        target_mass: float = 17.4,
        target_authority: float = 0.97,
        target_name: str = "Lexi-9-Omega Mastermind Cycle",
        *,
        current: CurrentParams | dict[str, float] | None = None,
        constraints: list[Constraint] | None = None,
        stakeholders: dict[str, float] | None = None,
        social_pull: float = 0.55,
        write_artifacts: bool = True,
    ) -> MastermindCycleReport:
        """
        Run the three-phase simulation and return a unified report.
        """
        # ------------------------------------------------------------------
        # 1. Retro-Causal → optimized parameters
        # ------------------------------------------------------------------
        future = FutureState(
            target_mass_density=float(target_mass),
            target_fold_strength=min(0.48, float(target_authority)),
            target_authority=float(target_authority),
            target_entropy_efficiency=1.04,
            description=(
                f"Mastermind future envelope for '{target_name}'. "
                "Goal metrics only — not physical time travel."
            ),
        )
        if current is None:
            current = CurrentParams(
                mass_density=max(8.0, target_mass * 0.72),
                fold_strength=0.22,
                authority=max(0.55, target_authority * 0.72),
                entropy_efficiency=0.88,
                notes="mastermind baseline",
            )

        retro_report = self.retro.optimize(future, current_params=current)
        opt = retro_report["optimized_params"]
        mass = float(opt["mass_density"])
        authority = float(opt["authority"])

        # ------------------------------------------------------------------
        # 2. Gravitational Processing → curvature + logic + local opt
        # ------------------------------------------------------------------
        curv = self.grav.analyze_density(mass)
        # Authority-gated logic sample (simulation narrative)
        logic_and = self.grav.logic_gate(authority, min(1.0, authority * 0.92), mass, gate="AND")
        logic_or = self.grav.logic_gate(authority, 0.55, mass, gate="OR")

        def cost(x: np.ndarray) -> float:
            # Pull abstract control vector toward [authority, fold, entropy_norm]
            target = np.array(
                [
                    authority,
                    float(opt["fold_strength"]),
                    float(opt["entropy_efficiency"]) / 2.0,
                ],
                dtype=float,
            )
            return float(np.sum((x - target) ** 2))

        grav_opt = self.grav.optimize_under_curvature(
            cost,
            x0=np.array([0.5, 0.2, 0.4], dtype=float),
            density=mass,
            steps=60,
            bounds=(0.0, 1.5),
        )

        grav_bundle = {
            "curvature_report": curv.to_dict(),
            "logic": {"AND": logic_and, "OR": logic_or},
            "optimize_under_curvature": {
                "x_best": grav_opt["x_best"],
                "f_best": grav_opt["f_best"],
                "steps_run": grav_opt["steps_run"],
                "step_scale": grav_opt["step_scale"],
                "noise_scale": grav_opt["noise_scale"],
            },
        }

        # ------------------------------------------------------------------
        # 3. Offensive Kali → full constraint assault (governance sim)
        # ------------------------------------------------------------------
        cons = constraints if constraints is not None else list(DEFAULT_CONSTRAINTS)
        stake = stakeholders or {
            "ops": 0.42,
            "legal": 0.35,
            "community": 0.55,
            "engineering": 0.48,
        }
        # Social pull scales lightly with aggression + authority
        pull = float(
            np.clip(social_pull * (0.7 + 0.3 * self.kali.base_aggression) * authority, 0.0, 1.0)
        )
        kali_report: PenetrationReport = self.kali.full_assault(
            target_name=target_name,
            constraints=cons,
            mass_density=mass,
            social_pull=pull,
            stakeholders=stake,
            write_artifacts=False,  # mastermind writes one unified pack
        )

        # ------------------------------------------------------------------
        # Aggregate status
        # ------------------------------------------------------------------
        residual = float(retro_report["residual_to_target"]["l2_normalized"])
        kali_yield = float(kali_report.overall_yield)
        if residual < 0.05 and kali_report.status != "CONSTRAINT_SURFACE_HARD":
            status = "MASTERMIND_NOMINAL"
        elif residual < 0.12 or kali_yield >= 0.35:
            status = "MASTERMIND_STRESSED"
        else:
            status = "MASTERMIND_HARD_CONSTRAINTS"

        report = MastermindCycleReport(
            target_name=target_name,
            target_mass=float(target_mass),
            target_authority=float(target_authority),
            status=status,
            retro={
                "optimizer": retro_report["optimizer"],
                "consistency_filter": retro_report["consistency_filter"],
                "residual_to_target": retro_report["residual_to_target"],
                "future_state": retro_report["future_state"],
                "initial_params": retro_report["initial_params"],
            },
            grav=grav_bundle,
            kali=kali_report.to_dict(),
            optimized_params=opt,
            classification=(
                "SIMULATION CYCLE ONLY — retro+grav+constraint pressure; "
                "not physical time travel, gravity hardware, or offensive security"
            ),
            timestamp=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            notes=(
                f"Cycle complete for '{target_name}'. "
                f"Optimized mass={mass:.4g}, authority={authority:.4g}, "
                f"κ={curv.curvature:.4g}, kali_status={kali_report.status}."
            ),
        )

        if write_artifacts:
            report.artifact_paths = self._write_cycle(report)

        self.history.append(report.to_dict())
        return report

    def format_report(self, report: MastermindCycleReport) -> str:
        opt = report.optimized_params
        curv = report.grav["curvature_report"]
        kali = report.kali
        lines = [
            "══════════════════════════════════════════════════",
            " MASTERMIND CORE · FULL SIMULATION CYCLE",
            " RETRO → GRAV → KALI (CONSTRAINT PRESSURE)",
            "══════════════════════════════════════════════════",
            f"Target             : {report.target_name}",
            f"Status             : {report.status}",
            f"Classification     : SIMULATION ONLY",
            "",
            "── 1. Retro-Causal ──────────────────────────────",
            f"  target mass      : {report.target_mass}",
            f"  target authority : {report.target_authority}",
            f"  opt mass         : {opt.get('mass_density', 0):.6g}",
            f"  opt fold         : {opt.get('fold_strength', 0):.6g}",
            f"  opt authority    : {opt.get('authority', 0):.6g}",
            f"  opt entropy_eff  : {opt.get('entropy_efficiency', 0):.6g}",
            f"  residual L2      : {report.retro['residual_to_target']['l2_normalized']:.6g}",
            f"  optimizer        : {report.retro['optimizer'].get('method')}",
            "",
            "── 2. Gravitational Processing ──────────────────",
            f"  density          : {curv['density']:.6g}",
            f"  curvature κ      : {curv['curvature']:.6g}",
            f"  regime           : {curv['regime']}",
            f"  softness         : {curv['softness']:.4g}",
            f"  logic AND        : {report.grav['logic']['AND']:.4g}",
            f"  logic OR         : {report.grav['logic']['OR']:.4g}",
            f"  grav f*          : {report.grav['optimize_under_curvature']['f_best']:.6g}",
            "",
            "── 3. Kali Constraint Pressure ──────────────────",
            f"  kali status      : {kali.get('status')}",
            f"  overall yield    : {kali.get('overall_yield', 0):.4g}",
            f"  constraints      : {kali.get('constraints_scanned')}",
            f"  aggression       : {self.kali.base_aggression:.3g}",
        ]
        for v in kali.get("vectors", [])[:8]:
            c = v["constraint"]
            lines.append(
                f"    · {c['type'][:11]:11s} {c['name'][:22]:22s} "
                f"{v['status']:10s} y={v['yield_score']:.3f}"
            )
        lines += [
            "",
            "Blocked literal ops: network recon, exploits, OS escalation, bypass.",
            report.notes,
            "══════════════════════════════════════════════════",
        ]
        if report.artifact_paths:
            lines.append("Artifacts:")
            for k, p in report.artifact_paths.items():
                lines.append(f"  {k}: {p}")
        return "\n".join(lines)

    def _write_cycle(self, report: MastermindCycleReport) -> dict[str, str]:
        ensure_dirs()
        out = WORKSPACE / "deliverables" / "simulations" / "mastermind"
        out.mkdir(parents=True, exist_ok=True)
        stamp = utc_stamp()
        slug = slugify(report.target_name)
        stem = f"{stamp}-{slug}-mastermind_cycle"
        md_path = out / f"{stem}.md"
        json_path = out / f"{stem}.json"

        text = self.format_report(report)
        md = (
            f"# Mastermind Cycle — {report.target_name}\n\n"
            f"**Status:** `{report.status}`  \n"
            f"**Classification:** {report.classification}\n\n"
            "```\n" + text + "\n```\n"
        )
        write_text(md_path, md)
        write_json(json_path, report.to_dict())
        return {"markdown": str(md_path), "json": str(json_path)}


def demo() -> str:
    core = MastermindCore(base_aggression=0.93)
    report = core.full_cycle(
        target_mass=17.4,
        target_authority=0.97,
        target_name="Lexi-9-Omega Mastermind Cycle",
    )
    return core.format_report(report)


if __name__ == "__main__":
    print(demo())
