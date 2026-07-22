"""
GravitationalProcessor — density→curvature simulation for logic + optimization.

CLASSIFICATION: research prototype / numerical simulation only.

"Mass density" and "curvature" here are *control scores* that shape:
- soft logic-gate sharpness (higher density → harder decision boundaries)
- optimizer step size and noise rejection (higher curvature → more decisive steps)

This is NOT:
- physical gravitation engineering
- spacetime curvature hardware
- finished exotic-matter / density weapons claims
- medical or structural load-bearing analysis for real buildings

Safe use: Lexi.PHYS visualization, abstract authority models, sim dashboards.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Callable

import numpy as np

from .artifacts import WORKSPACE, ensure_dirs, utc_stamp, write_json, write_text


# Softplus-like super-linear regime reference (kg/cm³ lore label only)
DENSITY_REF = 18.5
DENSITY_SOFT_KNEE = 8.0  # "above ~8" narrative threshold


@dataclass
class CurvatureReport:
    density: float
    curvature: float
    regime: str
    softness: float
    step_scale: float
    noise_scale: float
    notes: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class GravitationalProcessor:
    """
    Map abstract mass density → curvature, then use curvature to:
    1) sharpen soft logic gates
    2) scale optimization step size / noise rejection
    """

    def __init__(
        self,
        density_ref: float = DENSITY_REF,
        rng_seed: int = 42,
    ) -> None:
        self.density_ref = float(density_ref)
        self.rng = np.random.default_rng(rng_seed)
        self.history: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Curvature map
    # ------------------------------------------------------------------
    def curvature_from_density(self, density: float) -> float:
        """
        Super-linear response above ~8 kg/cm³ (simulation units).

        Smooth softplus branch + cubic term:
            x = density / 18.5
            κ = 0.15 * log1p(exp(6*(x-0.4))) + 2.8 * x**3
        """
        d = max(float(density), 0.0)
        x = d / self.density_ref
        # numerically stable softplus: log1p(exp(z)) with clip
        z = 6.0 * (x - 0.4)
        if z > 40:
            soft = z  # log1p(exp(z)) ~ z for large z
        elif z < -40:
            soft = math_exp_soft(z)
        else:
            soft = float(np.log1p(np.exp(z)))
        kappa = 0.15 * soft + 2.8 * (x**3)
        return float(max(kappa, 0.0))

    def analyze_density(self, density: float) -> CurvatureReport:
        kappa = self.curvature_from_density(density)
        # Softness of decision boundary: high κ → low softness
        softness = float(1.0 / (1.0 + 3.5 * kappa))
        # Step scale grows with curvature (decisive moves), capped
        step_scale = float(np.clip(0.15 + 0.55 * np.tanh(kappa), 0.05, 0.95))
        # Noise collapses under high mass/curvature
        noise_scale = float(np.clip(0.35 * softness, 0.0, 0.35))

        if density < DENSITY_SOFT_KNEE:
            regime = "diffuse"  # soft, exploratory
        elif density < self.density_ref:
            regime = "transitional"  # super-linear onset
        else:
            regime = "authoritative"  # high-mass decisive

        return CurvatureReport(
            density=float(density),
            curvature=kappa,
            regime=regime,
            softness=softness,
            step_scale=step_scale,
            noise_scale=noise_scale,
            notes=(
                "Abstract density→curvature control map. "
                "Not a physical gravitational field solver."
            ),
        )

    # ------------------------------------------------------------------
    # Soft logic under mass
    # ------------------------------------------------------------------
    def _sigmoid(self, z: float, sharpness: float) -> float:
        z = float(np.clip(z * sharpness, -60, 60))
        return float(1.0 / (1.0 + np.exp(-z)))

    def logic_gate(
        self,
        a: float,
        b: float,
        density: float,
        gate: str = "AND",
    ) -> float:
        """
        Soft boolean in [0, 1]. Softness of the decision boundary collapses
        under high mass → sharper, more authoritative logic.

        Gates: AND, OR, XOR, NAND, IMPLIES, NAND
        """
        a = float(np.clip(a, 0.0, 1.0))
        b = float(np.clip(b, 0.0, 1.0))
        report = self.analyze_density(density)
        # sharpness ↑ as softness ↓
        sharpness = float(1.0 / max(report.softness, 1e-3))

        def contrast(v: float) -> float:
            """Push soft values toward 0/1 as sharpness rises (boundary collapse)."""
            # mix continuous value with hard thresholded decision
            hard = 1.0 if v >= 0.5 else 0.0
            # softness=1 → mostly continuous; softness→0 → hard 0/1
            s = report.softness
            return float(np.clip((1.0 - s) * hard + s * v, 0.0, 1.0))

        g = gate.strip().upper()
        if g == "AND":
            # product AND (probabilistic) blended with Gödel min
            raw = 0.5 * (a * b) + 0.5 * min(a, b)
            return contrast(raw)
        if g == "OR":
            raw = 0.5 * (1.0 - (1.0 - a) * (1.0 - b)) + 0.5 * max(a, b)
            return contrast(raw)
        if g == "XOR":
            raw = abs(a - b)
            # high mass makes exclusive difference more binary
            return contrast(raw)
        if g == "NAND":
            return 1.0 - self.logic_gate(a, b, density, gate="AND")
        if g in {"IMPLIES", "IMP"}:
            # a → b  ≈  not a OR b
            return self.logic_gate(1.0 - a, b, density, gate="OR")
        if g == "AVG":
            return contrast(0.5 * (a + b))

        raise ValueError(f"Unknown gate '{gate}'. Use AND|OR|XOR|NAND|IMPLIES|AVG.")

    def logic_gate_hard(
        self,
        a: float,
        b: float,
        density: float,
        gate: str = "AND",
        threshold: float = 0.5,
    ) -> int:
        """Thresholded 0/1 decision after soft gate."""
        return 1 if self.logic_gate(a, b, density, gate=gate) >= threshold else 0

    # ------------------------------------------------------------------
    # Optimize under curvature
    # ------------------------------------------------------------------
    def optimize_under_curvature(
        self,
        cost_fn: Callable[[np.ndarray], float],
        x0: np.ndarray | list[float],
        density: float,
        steps: int = 80,
        bounds: tuple[float, float] | None = None,
        fd_eps: float = 1e-5,
    ) -> dict[str, Any]:
        """
        Gradient descent where step size and noise rejection scale with curvature.

        High mass / curvature → larger decisive steps, lower injected noise.
        Low mass → exploratory, noisier search.
        """
        x = np.asarray(x0, dtype=float).copy()
        if x.ndim != 1:
            raise ValueError("x0 must be a 1-D parameter vector")

        report = self.analyze_density(density)
        step_scale = report.step_scale
        noise_scale = report.noise_scale

        def project(v: np.ndarray) -> np.ndarray:
            if bounds is None:
                return v
            lo, hi = bounds
            return np.clip(v, lo, hi)

        def grad(v: np.ndarray) -> np.ndarray:
            g = np.zeros_like(v)
            f0 = float(cost_fn(v))
            for i in range(len(v)):
                vp = v.copy()
                vp[i] += fd_eps
                g[i] = (float(cost_fn(vp)) - f0) / fd_eps
            return g

        x = project(x)
        best_x = x.copy()
        best_f = float(cost_fn(x))
        traj = [best_f]
        lr0 = 0.25 * step_scale

        for t in range(int(steps)):
            g = grad(x)
            g_norm = float(np.linalg.norm(g) + 1e-12)
            direction = g / g_norm

            # noise rejection: additive noise collapses with curvature
            noise = self.rng.normal(0.0, noise_scale, size=x.shape)
            # high curvature damps noise further relative to gradient direction
            noise_weight = noise_scale / (1.0 + report.curvature)
            step = lr0 * direction + noise_weight * noise

            # backtracking line search
            lr = lr0
            f_curr = traj[-1]
            candidate = project(x - lr * step)
            f_cand = float(cost_fn(candidate))
            bt = 0
            while f_cand > f_curr and bt < 10:
                lr *= 0.5
                candidate = project(x - lr * step)
                f_cand = float(cost_fn(candidate))
                bt += 1

            x = candidate
            traj.append(f_cand)
            if f_cand < best_f:
                best_f = f_cand
                best_x = x.copy()

            if g_norm < 1e-7:
                break

        result = {
            "classification": "SIMULATION / RESEARCH PROTOTYPE ONLY",
            "disclaimer": (
                "Density/curvature are abstract control scores for optimizer behavior, "
                "not physical gravitational fields."
            ),
            "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "density": float(density),
            "curvature_report": report.to_dict(),
            "x0": np.asarray(x0, dtype=float).tolist(),
            "x_best": best_x.tolist(),
            "f_best": best_f,
            "f_final": traj[-1],
            "steps_run": len(traj) - 1,
            "loss_trajectory": traj[-25:],
            "step_scale": step_scale,
            "noise_scale": noise_scale,
        }
        self.history.append(result)
        return result

    # ------------------------------------------------------------------
    # Demo / report
    # ------------------------------------------------------------------
    def demo_report(self, density: float = 16.5, write_artifacts: bool = True) -> str:
        report = self.analyze_density(density)
        and_soft = self.logic_gate(0.7, 0.65, density, "AND")
        and_low = self.logic_gate(0.7, 0.65, 2.0, "AND")
        xor_hi = self.logic_gate(0.9, 0.1, density, "XOR")

        def bowl(v: np.ndarray) -> float:
            # simple quadratic bowl minimum at [1.5, -0.5]
            target = np.array([1.5, -0.5])
            return float(np.sum((v - target) ** 2))

        opt = self.optimize_under_curvature(
            bowl, x0=np.array([0.0, 0.0]), density=density, steps=60
        )

        lines = [
            "══════════════════════════════════════════════",
            " GRAVITATIONAL PROCESSOR · SIM REPORT",
            " ABSTRACT DENSITY→CURVATURE CONTROL ONLY",
            "══════════════════════════════════════════════",
            f"Density            : {report.density:.4g}",
            f"Curvature κ        : {report.curvature:.6g}",
            f"Regime             : {report.regime}",
            f"Softness           : {report.softness:.4g}",
            f"Step scale         : {report.step_scale:.4g}",
            f"Noise scale        : {report.noise_scale:.4g}",
            "",
            f"Logic AND @ density={density:.3g} : {and_soft:.4g}",
            f"Logic AND @ density=2.0           : {and_low:.4g}",
            f"Logic XOR @ high density          : {xor_hi:.4g}",
            "",
            f"Optimize f*        : {opt['f_best']:.6g}",
            f"x_best             : {opt['x_best']}",
            f"steps              : {opt['steps_run']}",
            "",
            "Not physical gravity hardware. Metrics are sim control scores.",
            "══════════════════════════════════════════════",
        ]
        text = "\n".join(lines)

        if write_artifacts:
            paths = self._write_report(report, opt, text)
            text += f"\nArtifacts:\n  markdown: {paths['markdown']}\n  json: {paths['json']}"
        return text

    def _write_report(
        self,
        report: CurvatureReport,
        opt: dict[str, Any],
        text: str,
    ) -> dict[str, str]:
        ensure_dirs()
        out_dir = WORKSPACE / "deliverables" / "simulations" / "gravitational_processor"
        out_dir.mkdir(parents=True, exist_ok=True)
        stamp = utc_stamp()
        stem = f"{stamp}-grav_processor"
        md_path = out_dir / f"{stem}.md"
        json_path = out_dir / f"{stem}.json"
        payload = {
            "curvature_report": report.to_dict(),
            "optimization": opt,
            "classification": "SIMULATION ONLY",
        }
        md = (
            "# GravitationalProcessor Report\n\n"
            "> **SIMULATION ONLY** — density/curvature are abstract control scores.\n\n"
            "```\n" + text + "\n```\n"
        )
        write_text(md_path, md)
        write_json(json_path, payload)
        return {"markdown": str(md_path), "json": str(json_path)}


def math_exp_soft(z: float) -> float:
    """log1p(exp(z)) for very negative z ≈ exp(z)."""
    return float(np.exp(z))


def demo() -> str:
    return GravitationalProcessor().demo_report(density=16.5, write_artifacts=True)


if __name__ == "__main__":
    print(demo())
