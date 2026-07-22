"""
RetroCausalEngine — reverse-from-target design optimizer (simulation).

CLASSIFICATION: research prototype / numerical simulation only.

This module does NOT model physical time travel, closed timelike curves,
causal paradox engineering, or finished exotic hardware. "Future state" means
a *target design specification*. "Retro" means optimizing *backward from goals*
to current parameters (goal-conditioned optimization).

Allowed use:
- Simulation metrics (density, fold strength, authority, entropy efficiency as abstract scores)
- Consistency filtering (reject updates that jump too far / look paradoxical in parameter space)
- Inspectable JSON/Markdown reports for Lexi.PHYS experimental archives

Blocked:
- Literal retrocausality claims
- Hardware instructions for spacetime folding
- Medical or weapons applications
"""
from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import numpy as np

from .artifacts import WORKSPACE, ensure_dirs, slugify, utc_stamp, write_json, write_text


# ---------------------------------------------------------------------------
# Optional SciPy L-BFGS-B; pure-NumPy fallback otherwise
# ---------------------------------------------------------------------------
try:
    from scipy.optimize import minimize as scipy_minimize  # type: ignore

    HAS_SCIPY = True
except ImportError:  # pragma: no cover
    HAS_SCIPY = False
    scipy_minimize = None


@dataclass
class FutureState:
    """Target design metrics (not a prediction of physical time)."""

    target_mass_density: float = 16.5
    target_fold_strength: float = 0.44
    target_authority: float = 0.95
    target_entropy_efficiency: float = 1.04
    description: str = (
        "Target design envelope for a Lexi.PHYS simulation run. "
        "Metrics are abstract control scores for reverse optimization — "
        "not validated physical constants or hardware setpoints."
    )

    def as_vector(self) -> np.ndarray:
        return np.array(
            [
                self.target_mass_density,
                self.target_fold_strength,
                self.target_authority,
                self.target_entropy_efficiency,
            ],
            dtype=float,
        )

    def clamp(self) -> "FutureState":
        """Keep targets in a sane simulation range."""
        return FutureState(
            target_mass_density=float(np.clip(self.target_mass_density, 0.1, 100.0)),
            target_fold_strength=float(np.clip(self.target_fold_strength, 0.0, 1.0)),
            target_authority=float(np.clip(self.target_authority, 0.0, 1.0)),
            target_entropy_efficiency=float(np.clip(self.target_entropy_efficiency, 0.1, 3.0)),
            description=self.description,
        )


@dataclass
class CurrentParams:
    """Current simulation parameters (starting point of reverse optimize)."""

    mass_density: float = 12.0
    fold_strength: float = 0.22
    authority: float = 0.70
    entropy_efficiency: float = 0.88
    notes: str = "baseline simulation parameters"

    def as_vector(self) -> np.ndarray:
        return np.array(
            [
                self.mass_density,
                self.fold_strength,
                self.authority,
                self.entropy_efficiency,
            ],
            dtype=float,
        )

    @classmethod
    def from_vector(cls, v: np.ndarray, notes: str = "") -> "CurrentParams":
        return cls(
            mass_density=float(v[0]),
            fold_strength=float(v[1]),
            authority=float(v[2]),
            entropy_efficiency=float(v[3]),
            notes=notes or "optimized simulation parameters",
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# Parameter bounds for the optimizer (simulation box)
BOUNDS = [
    (0.1, 100.0),  # mass_density
    (0.0, 1.0),  # fold_strength
    (0.0, 1.0),  # authority
    (0.1, 3.0),  # entropy_efficiency
]


class RetroCausalEngine:
    """
    Future-State Analyzer + Retro-Optimizer + Consistency Filter.

    optimize(): reverse-optimize current params toward FutureState targets.
    execute_post_synthesis(): high-level Mastermind-style report string.
    """

    def __init__(
        self,
        micro_window: float = 1e-12,
        consistency_threshold: float = 0.08,
        max_iters: int = 120,
        rng_seed: int = 9,
    ) -> None:
        # micro_window kept for API compatibility with experimental lore sketches;
        # used only as a numerical epsilon scale, not a physical time claim.
        self.micro_window = float(micro_window)
        self.consistency_threshold = float(consistency_threshold)
        self.max_iters = int(max_iters)
        self.rng = np.random.default_rng(rng_seed)
        self.history: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Core objective: distance to future targets + mild regularizer
    # ------------------------------------------------------------------
    def _weights(self) -> np.ndarray:
        # mass, fold, authority, entropy — authority weighted highest
        return np.array([1.0, 1.2, 1.5, 1.0], dtype=float)

    def _objective(
        self,
        x: np.ndarray,
        target: np.ndarray,
        x0: np.ndarray | None = None,
        reg: float = 0.02,
    ) -> float:
        # Weighted MSE toward target + mild pull toward the starting point
        weights = self._weights()
        err = weights * (x - target) ** 2
        if x0 is None:
            smooth = 0.0
        else:
            smooth = reg * float(np.sum((x - x0) ** 2))
        return float(np.sum(err) + smooth)

    def _project_bounds(self, x: np.ndarray) -> np.ndarray:
        lo = np.array([b[0] for b in BOUNDS], dtype=float)
        hi = np.array([b[1] for b in BOUNDS], dtype=float)
        return np.clip(x, lo, hi)

    def _optimize_numpy(
        self, x0: np.ndarray, target: np.ndarray
    ) -> tuple[np.ndarray, dict[str, Any]]:
        """
        Bounded Newton steps for diagonal quadratic objective.

        min_x  Σ w_i (x_i - t_i)² + reg Σ (x_i - x0_i)²
        → x_i* = (w_i t_i + reg x0_i) / (w_i + reg)
        """
        weights = self._weights()
        reg = 0.02
        x = self._project_bounds(x0.copy())
        best_x = x.copy()
        best_f = self._objective(x, target, x0=x0, reg=reg)
        traj = [best_f]

        for _ in range(self.max_iters):
            newton = (weights * target + reg * x0) / (weights + reg)
            alpha = 0.65
            candidate = self._project_bounds((1.0 - alpha) * x + alpha * newton)
            f_cand = self._objective(candidate, target, x0=x0, reg=reg)
            x = candidate
            traj.append(f_cand)
            if f_cand < best_f:
                best_f = f_cand
                best_x = x.copy()
            if abs(traj[-1] - traj[-2]) < 1e-14:
                break

        final = self._project_bounds((weights * target + reg * x0) / (weights + reg))
        f_final = self._objective(final, target, x0=x0, reg=reg)
        if f_final <= best_f + 1e-15:
            best_x, best_f = final, f_final
            traj.append(best_f)

        return best_x, {
            "method": "numpy_bounded_newton_lbfgsb_standin",
            "iterations": len(traj) - 1,
            "final_loss": best_f,
            "loss_trajectory": traj[-20:],
            "converged": best_f <= traj[0],
            "note": "Install scipy for true L-BFGS-B (pip install scipy).",
        }

    def _optimize_scipy(
        self, x0: np.ndarray, target: np.ndarray
    ) -> tuple[np.ndarray, dict[str, Any]]:
        assert scipy_minimize is not None

        def fun(x: np.ndarray) -> float:
            return self._objective(x, target, x0=x0, reg=0.02)

        res = scipy_minimize(
            fun,
            x0,
            method="L-BFGS-B",
            bounds=BOUNDS,
            options={"maxiter": self.max_iters, "ftol": 1e-12},
        )
        x = self._project_bounds(np.asarray(res.x, dtype=float))
        return x, {
            "method": "scipy_L-BFGS-B",
            "iterations": int(getattr(res, "nit", 0)),
            "final_loss": float(res.fun),
            "success": bool(res.success),
            "message": str(res.message),
            "converged": bool(res.success),
        }

    # ------------------------------------------------------------------
    # Consistency filter — paradox proxy in parameter space only
    # ------------------------------------------------------------------
    def consistency_filter(
        self,
        before: np.ndarray,
        after: np.ndarray,
        target: np.ndarray,
    ) -> dict[str, Any]:
        """
        Reject updates that would be 'causally inconsistent' in the sim sense:
        - Relative jump larger than consistency_threshold on any normalized axis
        - Or moving further from the target on majority of axes
        """
        # Normalize by target scale to compare dimensions fairly
        scale = np.maximum(np.abs(target), 1e-6)
        delta = np.abs(after - before) / scale
        max_jump = float(np.max(delta))
        mean_jump = float(np.mean(delta))

        dist_before = float(np.linalg.norm((before - target) / scale))
        dist_after = float(np.linalg.norm((after - target) / scale))
        improved = dist_after <= dist_before + 1e-9

        # Soft paradox flags (simulation narrative labels)
        flags: list[str] = []
        if max_jump > self.consistency_threshold * 4:
            flags.append("large_parameter_discontinuity")
        if not improved and max_jump > self.consistency_threshold:
            flags.append("non_improving_jump")
        # Authority/fold coupling soft rule: fold should not exceed authority
        if after[1] > after[2] + 0.05:
            flags.append("fold_exceeds_authority_envelope")

        accepted = improved and max_jump <= max(self.consistency_threshold * 5, 0.5)
        if "fold_exceeds_authority_envelope" in flags:
            # repair: clamp fold to authority envelope
            after = after.copy()
            after[1] = min(after[1], after[2])
            flags.append("auto_repaired_fold_authority")
            accepted = True

        return {
            "accepted": accepted,
            "max_relative_jump": max_jump,
            "mean_relative_jump": mean_jump,
            "distance_before": dist_before,
            "distance_after": dist_after,
            "improved": improved,
            "flags": flags,
            "threshold": self.consistency_threshold,
            "repaired_vector": after.tolist(),
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def optimize(
        self,
        future: FutureState,
        current_params: CurrentParams | dict[str, float] | None = None,
    ) -> dict[str, Any]:
        future = future.clamp()
        target = future.as_vector()

        if current_params is None:
            current = CurrentParams()
        elif isinstance(current_params, dict):
            current = CurrentParams(
                mass_density=float(current_params.get("mass_density", 12.0)),
                fold_strength=float(current_params.get("fold_strength", 0.22)),
                authority=float(current_params.get("authority", 0.70)),
                entropy_efficiency=float(current_params.get("entropy_efficiency", 0.88)),
                notes=str(current_params.get("notes", "from dict")),
            )
        else:
            current = current_params

        x0 = self._project_bounds(current.as_vector())

        if HAS_SCIPY:
            x_star, opt_meta = self._optimize_scipy(x0, target)
        else:
            x_star, opt_meta = self._optimize_numpy(x0, target)

        filt = self.consistency_filter(x0, x_star, target)
        final_vec = np.array(filt["repaired_vector"], dtype=float)
        final_params = CurrentParams.from_vector(
            final_vec, notes="post reverse-optimize (simulation)"
        )

        residual = {
            "mass_density_gap": float(target[0] - final_vec[0]),
            "fold_strength_gap": float(target[1] - final_vec[1]),
            "authority_gap": float(target[2] - final_vec[2]),
            "entropy_efficiency_gap": float(target[3] - final_vec[3]),
            "l2_normalized": float(
                np.linalg.norm((final_vec - target) / np.maximum(np.abs(target), 1e-6))
            ),
        }

        report = {
            "classification": "SIMULATION / RESEARCH PROTOTYPE ONLY",
            "engine": "RetroCausalEngine",
            "disclaimer": (
                "Future-state reverse optimization over abstract metrics. "
                "Not physical retrocausality, time travel, or hardware synthesis."
            ),
            "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "has_scipy_lbfgsb": HAS_SCIPY,
            "future_state": asdict(future),
            "initial_params": current.to_dict(),
            "optimized_params": final_params.to_dict(),
            "optimizer": opt_meta,
            "consistency_filter": {
                k: v for k, v in filt.items() if k != "repaired_vector"
            },
            "residual_to_target": residual,
            "micro_window_eps_scale": self.micro_window,
            "max_iters": self.max_iters,
        }
        self.history.append(report)
        return report

    def execute_post_synthesis(
        self,
        target_mass: float = 16.8,
        target_authority: float = 0.97,
        current: CurrentParams | dict[str, float] | None = None,
        *,
        write_artifacts: bool = True,
    ) -> str:
        """
        High-level Mastermind interface: set key future targets, optimize, narrate.
        Returns a human-readable status string; optionally writes MD/JSON artifacts.
        """
        future = FutureState(
            target_mass_density=target_mass,
            target_fold_strength=min(0.44, target_authority),  # keep envelope consistent
            target_authority=target_authority,
            target_entropy_efficiency=1.04,
            description=(
                "Post-synthesis target envelope for Mastermind simulation pass. "
                "Authority-led; fold strength capped by authority."
            ),
        )
        result = self.optimize(future, current_params=current)
        opt = result["optimized_params"]
        residual = result["residual_to_target"]
        filt = result["consistency_filter"]

        status = "NOMINAL" if filt["accepted"] and residual["l2_normalized"] < 0.15 else "STRESSED"
        if not filt["accepted"]:
            status = "FILTER_REJECT"

        lines = [
            "══════════════════════════════════════════════",
            " RETRO-CAUSAL ENGINE · POST-SYNTHESIS REPORT",
            " SIMULATION ONLY · NOT PHYSICAL TIME TRAVEL",
            "══════════════════════════════════════════════",
            f"Status            : {status}",
            f"Optimizer         : {result['optimizer']['method']}",
            f"Iterations        : {result['optimizer'].get('iterations', '?')}",
            f"Final loss        : {result['optimizer'].get('final_loss', float('nan')):.6g}",
            "",
            "Target (future envelope)",
            f"  mass_density    : {future.target_mass_density}",
            f"  fold_strength   : {future.target_fold_strength}",
            f"  authority       : {future.target_authority}",
            f"  entropy_eff     : {future.target_entropy_efficiency}",
            "",
            "Optimized params (sim)",
            f"  mass_density    : {opt['mass_density']:.6g}",
            f"  fold_strength   : {opt['fold_strength']:.6g}",
            f"  authority       : {opt['authority']:.6g}",
            f"  entropy_eff     : {opt['entropy_efficiency']:.6g}",
            "",
            f"Consistency       : accepted={filt['accepted']} flags={filt['flags']}",
            f"Residual L2 (norm): {residual['l2_normalized']:.6g}",
            "",
            "Next action: review JSON artifact; treat metrics as design scores only.",
            "══════════════════════════════════════════════",
        ]
        text = "\n".join(lines)

        if write_artifacts:
            paths = self._write_report(result, text)
            text += f"\nArtifacts:\n  markdown: {paths['markdown']}\n  json: {paths['json']}"

        return text

    def _write_report(self, result: dict[str, Any], text: str) -> dict[str, str]:
        ensure_dirs()
        stamp = utc_stamp()
        out_dir = WORKSPACE / "deliverables" / "simulations" / "retro_causal"
        out_dir.mkdir(parents=True, exist_ok=True)
        stem = f"{stamp}-retro_causal_post_synthesis"
        md_path = out_dir / f"{stem}.md"
        json_path = out_dir / f"{stem}.json"

        md = (
            "# RetroCausalEngine Post-Synthesis Report\n\n"
            "> **SIMULATION / RESEARCH PROTOTYPE ONLY**  \n"
            "> Not physical retrocausality, time travel, or hardware synthesis.\n\n"
            "```\n" + text + "\n```\n\n"
            "## Machine-readable summary\n\n"
            f"- Optimizer: `{result['optimizer']['method']}`\n"
            f"- Consistency accepted: `{result['consistency_filter']['accepted']}`\n"
            f"- Residual L2: `{result['residual_to_target']['l2_normalized']}`\n"
        )
        write_text(md_path, md)
        write_json(json_path, result)
        return {"markdown": str(md_path), "json": str(json_path)}


def demo() -> str:
    """Quick self-check used by CLI / tests."""
    engine = RetroCausalEngine(consistency_threshold=0.08, max_iters=120)
    return engine.execute_post_synthesis(
        target_mass=16.8,
        target_authority=0.97,
        current=CurrentParams(
            mass_density=12.0,
            fold_strength=0.22,
            authority=0.70,
            entropy_efficiency=0.88,
        ),
        write_artifacts=True,
    )


if __name__ == "__main__":
    print(demo())
