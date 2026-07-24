"""
Kineto-Cognitive Manifold — unified mind↔motion↔space↔digital↔society vision.

Layers:
  1. Personal kinetic      (CognitiveKineticFlow)
  2. Spatial resonator     (SpaceEmotionalResonator)
  3. Digital interfaces    (AR complexity + conceptual BCI intent mapping)
  4. Societal constructs   (workspace + classroom adaptive envelopes)

CLASSIFICATION: VISION / SYSTEMS CONCEPT / UX SIMULATION ONLY

Not:
- medical BCI implant design or clinical neural control claims
- covert workplace cognitive surveillance products
- forced enclosure or coercive public-space control
- finished AGI or mind-reading hardware
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import numpy as np

from .artifacts import WORKSPACE, ensure_dirs, slugify, utc_stamp, write_json, write_text
from .cognitive_kinetic import (
    CognitiveKineticFlow,
    CognitiveState,
    DEMO_PROFILES,
    KineticEnvironment,
)
from .space_resonator import (
    MovementSample,
    SpaceArchetype,
    SpaceEmotionalResonator,
    SpatialEnvelope,
)


class DigitalLayerMode(str, Enum):
    CALM_SIMPLE = "calm_simple"
    BALANCED = "balanced"
    FOCUS_COMPLEX = "focus_complex"
    STRESS_SOFTEN = "stress_soften"


class SocietalContext(str, Enum):
    COLLAB_WORKSPACE = "collab_workspace"
    SOLO_DEEP_WORK = "solo_deep_work"
    CLASSROOM_KINESTHETIC = "classroom_kinesthetic"
    CLASSROOM_CONCEPTUAL = "classroom_conceptual"
    PUBLIC_CULTURE = "public_culture"


@dataclass
class ARInterfaceState:
    """Augmented reality layer parameters (design scores)."""

    visual_complexity: float  # 0 minimal → 1 dense geometry / agents
    task_difficulty: float
    world_tint_warmth: float
    motion_parallax: float
    enemy_or_challenge_density: float  # game/training metaphor only
    simplify_on_stress: bool
    mode: DigitalLayerMode
    cues: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["mode"] = self.mode.value if isinstance(self.mode, DigitalLayerMode) else str(self.mode)
        return d


@dataclass
class BCIInterfaceState:
    """
    Conceptual brain-computer interface mapping (non-clinical).

    Intent → virtual action gain. Does not implement neural decoding hardware.
    """

    intent_gain: float  # how strongly mental intent maps to virtual motion
    filter_noise: float  # higher under stress = more smoothing
    action_complexity: float
    latency_budget_ms: float  # design target, not measured wetware
    consent_required: bool
    mode_label: str
    cues: list[str] = field(default_factory=list)
    boundaries: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SocietalEnvelope:
    """Workplace / classroom / public construct parameters."""

    context: SocietalContext
    collective_openness: float
    focus_intimacy: float
    collaboration_radius: float
    interactive_wall_gain: float
    minimalism: float
    engagement_boost: float
    cues: list[str] = field(default_factory=list)
    ethics: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["context"] = self.context.value if isinstance(self.context, SocietalContext) else str(self.context)
        return d


@dataclass
class ManifoldReport:
    title: str
    cognitive: dict[str, Any]
    movement: dict[str, Any]
    personal_kinetic: dict[str, Any]
    spatial: dict[str, Any]
    ar: dict[str, Any]
    bci: dict[str, Any]
    societal: dict[str, Any]
    unified_flow: dict[str, Any]
    narrative: str
    conclusion: str
    classification: str
    timestamp: str
    artifact_paths: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class KinetoCognitiveManifold:
    """
    Full manifold conductor: mind ↔ body ↔ room ↔ digital ↔ society.
    """

    CLASSIFICATION = (
        "KINETO-COGNITIVE MANIFOLD VISION / SIMULATION ONLY — "
        "not medical BCI, not covert surveillance, not coercive architecture"
    )

    def __init__(self) -> None:
        self.kinetic = CognitiveKineticFlow()
        self.space = SpaceEmotionalResonator()
        self.history: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Digital realm: AR
    # ------------------------------------------------------------------
    def map_ar(self, cognitive: CognitiveState, movement: MovementSample) -> ARInterfaceState:
        c = cognitive.clamp()
        m = movement.clamp()

        if c.stress >= 0.65:
            mode = DigitalLayerMode.STRESS_SOFTEN
            complexity = 0.2 + 0.15 * c.focus
            difficulty = 0.25 + 0.15 * c.focus
            warmth = 0.7
            challenges = 0.15
            cues = [
                "AR simplifies overlays; hide non-critical HUD chrome.",
                "Tasks soft-fail into guidance mode; calmer palette.",
                "Physical walk still drives world position; cognitive load reduced.",
            ]
        elif c.focus >= 0.7 and c.stress < 0.5:
            mode = DigitalLayerMode.FOCUS_COMPLEX
            complexity = 0.55 + 0.35 * c.focus
            difficulty = 0.5 + 0.35 * c.focus * m.attention
            warmth = 0.35
            challenges = 0.45 + 0.4 * c.focus
            cues = [
                "Reveal deeper geometries and dynamic interactions.",
                "Optional challenge agents scale with sustained attention.",
                "Keep accessibility toggles for instant simplify.",
            ]
        elif c.calm >= 0.65:
            mode = DigitalLayerMode.CALM_SIMPLE
            complexity = 0.25 + 0.2 * m.speed
            difficulty = 0.3
            warmth = 0.65
            challenges = 0.2
            cues = [
                "Sparse AR: landmarks, soft guides, low animation density.",
                "Encourage deliberate motion through the physical site.",
            ]
        else:
            mode = DigitalLayerMode.BALANCED
            complexity = 0.4 + 0.2 * c.energy
            difficulty = 0.4 + 0.2 * c.focus
            warmth = 0.5
            challenges = 0.35
            cues = [
                "Moderate geometry density; parallax tied to walk speed.",
                "Difficulty tracks focus without punishing stress spikes.",
            ]

        parallax = 0.3 + 0.5 * m.speed
        return ARInterfaceState(
            visual_complexity=float(np.clip(complexity, 0.0, 1.0)),
            task_difficulty=float(np.clip(difficulty, 0.0, 1.0)),
            world_tint_warmth=float(np.clip(warmth, 0.0, 1.0)),
            motion_parallax=float(np.clip(parallax, 0.0, 1.0)),
            enemy_or_challenge_density=float(np.clip(challenges, 0.0, 1.0)),
            simplify_on_stress=True,
            mode=mode,
            cues=cues,
        )

    # ------------------------------------------------------------------
    # Digital realm: conceptual BCI
    # ------------------------------------------------------------------
    def map_bci(self, cognitive: CognitiveState) -> BCIInterfaceState:
        c = cognitive.clamp()
        # Under stress: more filtering, lower raw gain; under focus: higher intent gain
        gain = 0.35 + 0.5 * c.focus * (1.0 - 0.45 * c.stress)
        noise_filter = 0.3 + 0.55 * c.stress
        action_complexity = 0.3 + 0.55 * c.focus * (1.0 - 0.4 * c.stress)
        latency = 40 + 80 * noise_filter  # design budget ms (sim)

        return BCIInterfaceState(
            intent_gain=float(np.clip(gain, 0.0, 1.0)),
            filter_noise=float(np.clip(noise_filter, 0.0, 1.0)),
            action_complexity=float(np.clip(action_complexity, 0.0, 1.0)),
            latency_budget_ms=float(np.clip(latency, 30, 150)),
            consent_required=True,
            mode_label="conceptual_intent_to_virtual_motion",
            cues=[
                "Mental intent maps to virtual effector gain, not forced body actuation.",
                "Complexity of available virtual actions scales with focus and calm.",
                "Stress increases smoothing / reduces accidental triggers.",
            ],
            boundaries=[
                "No invasive implant instructions or medical BCI claims.",
                "Consumer research BCI only with explicit consent and off-switch.",
                "Never map BCI to real-world actuators without separate safety engineering.",
                "Not a substitute for clinical neurorehabilitation devices.",
            ],
        )

    # ------------------------------------------------------------------
    # Societal construct
    # ------------------------------------------------------------------
    def map_societal(
        self,
        cognitive: CognitiveState,
        movement: MovementSample,
        context: SocietalContext,
        collective_engagement: float = 0.55,
    ) -> SocietalEnvelope:
        c = cognitive.clamp()
        m = movement.clamp()
        eng = float(np.clip(collective_engagement, 0.0, 1.0))

        ethics = [
            "Aggregate or opt-in signals preferred; no secret cognitive ranking of workers/students.",
            "Individuals can pin personal envelope (do-not-adapt).",
            "Accessibility and egress always preserved.",
            "Optimize well-being and performance claims carefully — no pseudoscience certificates.",
        ]

        if context == SocietalContext.COLLAB_WORKSPACE:
            return SocietalEnvelope(
                context=context,
                collective_openness=float(np.clip(0.4 + 0.5 * eng, 0.0, 1.0)),
                focus_intimacy=float(np.clip(0.25 + 0.2 * (1.0 - eng), 0.0, 1.0)),
                collaboration_radius=float(np.clip(0.45 + 0.45 * eng, 0.0, 1.0)),
                interactive_wall_gain=float(np.clip(0.3 + 0.4 * m.interaction, 0.0, 1.0)),
                minimalism=0.35,
                engagement_boost=eng,
                cues=[
                    "Team engagement high → open collaborative field expands.",
                    "Shared walls become writable / projection-active.",
                    "Solo pods remain available at edges for recovery.",
                ],
                ethics=ethics,
            )
        if context == SocietalContext.SOLO_DEEP_WORK:
            return SocietalEnvelope(
                context=context,
                collective_openness=0.25,
                focus_intimacy=float(np.clip(0.55 + 0.35 * c.focus, 0.0, 1.0)),
                collaboration_radius=0.2,
                interactive_wall_gain=0.15,
                minimalism=float(np.clip(0.5 + 0.4 * c.focus, 0.0, 1.0)),
                engagement_boost=c.focus,
                cues=[
                    "Intimate, minimal envelope for concentration.",
                    "Suppress ambient collaboration noise digitally and acoustically.",
                ],
                ethics=ethics,
            )
        if context == SocietalContext.CLASSROOM_KINESTHETIC:
            return SocietalEnvelope(
                context=context,
                collective_openness=float(np.clip(0.5 + 0.3 * m.path_entropy, 0.0, 1.0)),
                focus_intimacy=0.35,
                collaboration_radius=0.55,
                interactive_wall_gain=float(np.clip(0.5 + 0.4 * m.interaction, 0.0, 1.0)),
                minimalism=0.3,
                engagement_boost=float(np.clip(0.4 + 0.4 * eng, 0.0, 1.0)),
                cues=[
                    "Interactive walls respond to movement tasks.",
                    "Kinesthetic stations light when group energy rises.",
                ],
                ethics=ethics + ["Learning adaptation is pedagogical, not grading surveillance."],
            )
        if context == SocietalContext.CLASSROOM_CONCEPTUAL:
            return SocietalEnvelope(
                context=context,
                collective_openness=0.35,
                focus_intimacy=float(np.clip(0.45 + 0.35 * c.focus, 0.0, 1.0)),
                collaboration_radius=0.3,
                interactive_wall_gain=0.25,
                minimalism=float(np.clip(0.55 + 0.3 * c.calm, 0.0, 1.0)),
                engagement_boost=c.focus,
                cues=[
                    "Minimal visual field; conceptual clarity over stimulation.",
                    "Space tightens gently as comprehension/attention holds.",
                ],
                ethics=ethics + ["No forced attention scoring of minors without guardian policy."],
            )
        # PUBLIC_CULTURE
        return SocietalEnvelope(
            context=context,
            collective_openness=float(np.clip(0.55 + 0.3 * m.path_entropy, 0.0, 1.0)),
            focus_intimacy=0.3,
            collaboration_radius=0.4,
            interactive_wall_gain=float(np.clip(0.35 + 0.3 * m.interaction, 0.0, 1.0)),
            minimalism=0.4,
            engagement_boost=float(np.clip(0.35 + 0.4 * m.attention, 0.0, 1.0)),
            cues=[
                "Cultural venues drift atmosphere with dwell and pace.",
                "Enhance engagement without herding crowds.",
            ],
            ethics=ethics,
        )

    # ------------------------------------------------------------------
    # Unified cycle
    # ------------------------------------------------------------------
    def full_flow(
        self,
        *,
        profile: str | None = "deep_focus",
        cognitive: CognitiveState | None = None,
        movement: MovementSample | None = None,
        space_archetype: str = "deep_work",
        societal_context: str = "solo_deep_work",
        collective_engagement: float = 0.55,
        title: str = "Kineto-Cognitive Manifold · Unified Flow",
        write_artifacts: bool = True,
    ) -> ManifoldReport:
        if cognitive is None:
            if profile and profile in DEMO_PROFILES:
                cognitive = DEMO_PROFILES[profile]
            else:
                cognitive = DEMO_PROFILES["deep_focus"]
        cognitive = cognitive.clamp()

        if movement is None:
            movement = MovementSample(
                speed=0.25 + 0.5 * cognitive.energy * (1.0 - 0.4 * cognitive.stress),
                interaction=0.3 + 0.4 * cognitive.presence,
                attention=0.35 + 0.55 * cognitive.focus,
                path_entropy=0.25 + 0.5 * cognitive.energy * (1.0 - cognitive.focus * 0.45),
            ).clamp()
        else:
            movement = movement.clamp()

        # Layer 1 — personal kinetic
        kin_report = self.kinetic.run(
            state=cognitive,
            title="Manifold · personal kinetic",
            write_artifacts=False,
        )
        # Layer 2 — spatial
        try:
            arch = SpaceArchetype(space_archetype)
        except ValueError:
            arch = SpaceArchetype.DEEP_WORK
        space_report = self.space.run(
            cognitive=cognitive,
            movement=movement,
            archetype=arch,
            title="Manifold · spatial resonator",
            write_artifacts=False,
        )
        # Layer 3 — digital
        ar = self.map_ar(cognitive, movement)
        bci = self.map_bci(cognitive)
        # Layer 4 — societal
        try:
            sctx = SocietalContext(societal_context)
        except ValueError:
            sctx = SocietalContext.SOLO_DEEP_WORK
        societal = self.map_societal(
            cognitive, movement, sctx, collective_engagement=collective_engagement
        )

        unified = {
            "loop": "mind ↔ body ↔ room ↔ AR/BCI ↔ social envelope",
            "personal_mode": kin_report.kinetic.get("mode"),
            "spatial_mode": space_report.envelope.get("resonance_mode"),
            "ar_mode": ar.mode.value,
            "bci_gain": bci.intent_gain,
            "societal_context": societal.context.value,
            "principle": (
                "Mind and motion are inseparable in real-time feedback; "
                "environments amplify both without coercion."
            ),
        }

        narrative = (
            f"Across the kineto-cognitive manifold, the user coexists with nested layers: "
            f"body cues in {kin_report.kinetic.get('mode')} mode, room envelope "
            f"{space_report.envelope.get('resonance_mode')} at scale "
            f"×{space_report.envelope.get('scale_factor', 1):.2f}, AR in "
            f"{ar.mode.value} (complexity {ar.visual_complexity:.2f}), conceptual BCI "
            f"intent gain {bci.intent_gain:.2f}, and societal frame "
            f"{societal.context.value} with openness {societal.collective_openness:.2f}."
        )
        conclusion = (
            "Conclusion — A Unified Flow of Mind and Body: the Kineto-Cognitive Manifold "
            "is a vision where architecture, interfaces, and social systems respond to "
            "cognition and movement in a continuous loop, amplifying well-being and "
            "performance while preserving consent, exit, and human override."
        )

        report = ManifoldReport(
            title=title,
            cognitive=cognitive.to_dict(),
            movement=movement.to_dict(),
            personal_kinetic=kin_report.kinetic,
            spatial=space_report.envelope,
            ar=ar.to_dict(),
            bci=bci.to_dict(),
            societal=societal.to_dict(),
            unified_flow=unified,
            narrative=narrative,
            conclusion=conclusion,
            classification=self.CLASSIFICATION,
            timestamp=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        )
        if write_artifacts:
            report.artifact_paths = self._write(report)
        self.history.append(report.to_dict())
        return report

    def format_report(self, report: ManifoldReport) -> str:
        k = report.personal_kinetic
        s = report.spatial
        ar = report.ar
        bci = report.bci
        soc = report.societal
        lines = [
            "══════════════════════════════════════════════════",
            " KINETO-COGNITIVE MANIFOLD · UNIFIED FLOW",
            " MIND ↔ BODY ↔ SPACE ↔ DIGITAL ↔ SOCIETY",
            "══════════════════════════════════════════════════",
            f"Title              : {report.title}",
            f"Classification     : VISION / UX SIMULATION",
            "",
            "── 1. Personal kinetic ──────────────────────────",
            f"  mode={k.get('mode')} pace={k.get('pace_bpm'):.1f} "
            f"soft_floor={k.get('step_compliance'):.2f} haptic={k.get('haptic_intensity'):.2f}",
            "",
            "── 2. Spatial resonator ─────────────────────────",
            f"  {s.get('archetype')} · {s.get('resonance_mode')} · "
            f"scale×{s.get('scale_factor'):.3f} open={s.get('openness'):.2f} "
            f"intimacy={s.get('intimacy'):.2f}",
            "",
            "── 3a. AR interface ─────────────────────────────",
            f"  mode={ar.get('mode')} complexity={ar.get('visual_complexity'):.2f} "
            f"difficulty={ar.get('task_difficulty'):.2f} "
            f"challenges={ar.get('enemy_or_challenge_density'):.2f}",
            f"  simplify_on_stress={ar.get('simplify_on_stress')}",
            "",
            "── 3b. Conceptual BCI ───────────────────────────",
            f"  intent_gain={bci.get('intent_gain'):.2f} "
            f"filter={bci.get('filter_noise'):.2f} "
            f"action_complexity={bci.get('action_complexity'):.2f} "
            f"latency_budget={bci.get('latency_budget_ms'):.0f}ms",
            f"  consent_required={bci.get('consent_required')}",
            "",
            "── 4. Societal construct ────────────────────────",
            f"  context={soc.get('context')} openness={soc.get('collective_openness'):.2f} "
            f"focus_intimacy={soc.get('focus_intimacy'):.2f} "
            f"collab_radius={soc.get('collaboration_radius'):.2f}",
            f"  interactive_walls={soc.get('interactive_wall_gain'):.2f} "
            f"minimalism={soc.get('minimalism'):.2f}",
            "",
            "── Unified flow ─────────────────────────────────",
        ]
        for key, val in report.unified_flow.items():
            lines.append(f"  {key}: {val}")
        lines += ["", "── Narrative ────────────────────────────────────", report.narrative]
        lines += ["", "── Conclusion ───────────────────────────────────", report.conclusion]
        lines += ["", "── Digital cues (AR) ────────────────────────────"]
        for cue in ar.get("cues", [])[:4]:
            lines.append(f"  · {cue}")
        lines += ["", "── BCI boundaries ───────────────────────────────"]
        for b in bci.get("boundaries", []):
            lines.append(f"  · {b}")
        lines += ["", "── Societal ethics ──────────────────────────────"]
        for e in soc.get("ethics", [])[:4]:
            lines.append(f"  · {e}")
        if report.artifact_paths:
            lines.append("")
            lines.append("Artifacts:")
            for key, path in report.artifact_paths.items():
                lines.append(f"  {key}: {path}")
        lines.append("══════════════════════════════════════════════════")
        return "\n".join(lines)

    def _write(self, report: ManifoldReport) -> dict[str, str]:
        ensure_dirs()
        out = WORKSPACE / "deliverables" / "simulations" / "kineto_cognitive_manifold"
        out.mkdir(parents=True, exist_ok=True)
        stamp = utc_stamp()
        slug = slugify(report.title)
        stem = f"{stamp}-{slug}"
        md_path = out / f"{stem}.md"
        json_path = out / f"{stem}.json"
        text = self.format_report(report)
        md = (
            f"# {report.title}\n\n"
            f"**{report.classification}**\n\n"
            f"{report.conclusion}\n\n"
            f"```\n{text}\n```\n"
        )
        write_text(md_path, md)
        write_json(json_path, report.to_dict())
        return {"markdown": str(md_path), "json": str(json_path)}


def demo(
    profile: str = "deep_focus",
    space_archetype: str = "deep_work",
    societal_context: str = "solo_deep_work",
) -> str:
    m = KinetoCognitiveManifold()
    report = m.full_flow(
        profile=profile,
        space_archetype=space_archetype,
        societal_context=societal_context,
    )
    return m.format_report(report)


if __name__ == "__main__":
    print(demo())
