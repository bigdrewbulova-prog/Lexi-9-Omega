"""
Kinetic-Cognitive Architecture — Space as an Emotional Resonator.

CLASSIFICATION: ARCHITECTURAL CONCEPT / IMMERSIVE UX SIMULATION ONLY

Models how a space co-adapts with human movement and abstract cognitive state:
- Adaptive floor-plan scale (expand / constrict)
- Atmosphere (color temperature, acoustics, floor texture)
- Public-space feedback loops (museums, galleries)

Does NOT:
- claim real-time structural transformation of load-bearing buildings without engineering review
- diagnose mental health conditions
- force enclosure or trap users (intimacy ≠ lockdown)
- serve as a medical or security surveillance product
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import numpy as np

from .artifacts import WORKSPACE, ensure_dirs, slugify, utc_stamp, write_json, write_text
from .cognitive_kinetic import CognitiveState, DEMO_PROFILES, KineticMode


class SpaceArchetype(str, Enum):
    DEEP_WORK = "deep_work"
    CREATIVE = "creative"
    MEDITATIVE = "meditative"
    GALLERY = "gallery"
    PUBLIC_PLAZA = "public_plaza"


class ResonanceMode(str, Enum):
    EXPAND = "expand"          # freer movement, inspiration
    CONSTRICT = "constrict"    # intimate focus (never sealed)
    HOLD = "hold"              # stable envelope
    DRIFT = "drift"            # slow atmospheric shift for public flow


@dataclass
class MovementSample:
    """Abstract movement / attention signals (not biometric ID)."""

    speed: float = 0.4          # 0 still → 1 fast traverse
    interaction: float = 0.3    # 0 passive → 1 high touch/dwell
    attention: float = 0.5      # 0 distracted → 1 absorbed
    path_entropy: float = 0.4   # 0 linear path → 1 exploratory wandering

    def clamp(self) -> "MovementSample":
        def c(x: float) -> float:
            return float(np.clip(x, 0.0, 1.0))

        return MovementSample(
            speed=c(self.speed),
            interaction=c(self.interaction),
            attention=c(self.attention),
            path_entropy=c(self.path_entropy),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self.clamp())


@dataclass
class SpatialEnvelope:
    """Adaptive floor-plan / atmosphere parameters (design scores)."""

    scale_factor: float           # 1.0 baseline; >1 expand; <1 constrict
    openness: float               # 0 intimate enclosure cues → 1 open plan
    intimacy: float               # perceived closeness (soft partitions, not locks)
    wall_color_temp_k: float      # abstract Kelvin-like score 2700–6500
    acoustic_absorption: float    # 0 live/echo → 1 dead/soft
    floor_texture: float          # 0 smooth hard → 1 soft textured
    partition_mobility: float     # how much partitions may drift (sim)
    exploration_invite: float     # prompts to wander vs settle
    resonance_mode: ResonanceMode
    archetype: SpaceArchetype
    cues: list[str] = field(default_factory=list)
    safety_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["resonance_mode"] = (
            self.resonance_mode.value
            if isinstance(self.resonance_mode, ResonanceMode)
            else str(self.resonance_mode)
        )
        d["archetype"] = (
            self.archetype.value
            if isinstance(self.archetype, SpaceArchetype)
            else str(self.archetype)
        )
        return d


@dataclass
class SpaceResonatorReport:
    title: str
    cognitive: dict[str, Any]
    movement: dict[str, Any]
    envelope: dict[str, Any]
    feedback_loop: dict[str, Any]
    narrative: str
    application: str
    classification: str
    timestamp: str
    artifact_paths: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SpaceEmotionalResonator:
    """
    Space coexists with the user: cognitive + movement → adaptive envelope.
    """

    CLASSIFICATION = (
        "ARCHITECTURAL CONCEPT / IMMERSIVE UX SIMULATION ONLY — "
        "not medical, not forced enclosure, not unreviewed structural morphing"
    )

    def __init__(self) -> None:
        self.history: list[dict[str, Any]] = []

    def choose_resonance(
        self,
        cognitive: CognitiveState,
        movement: MovementSample,
        archetype: SpaceArchetype,
    ) -> ResonanceMode:
        c = cognitive.clamp()
        m = movement.clamp()

        # Creative energy + exploratory path → expand
        creative_drive = 0.45 * c.energy + 0.35 * m.path_entropy + 0.20 * c.focus
        # Stillness / immersion / high calm → constrict (intimate, not sealed)
        still_drive = 0.40 * c.calm + 0.35 * m.attention + 0.25 * (1.0 - m.speed)

        if archetype in {SpaceArchetype.GALLERY, SpaceArchetype.PUBLIC_PLAZA}:
            if m.speed > 0.65 or m.path_entropy > 0.6:
                return ResonanceMode.DRIFT
            if m.attention > 0.7 and m.speed < 0.35:
                return ResonanceMode.HOLD

        if creative_drive >= 0.62 and c.stress < 0.7:
            return ResonanceMode.EXPAND
        if still_drive >= 0.60 or (c.focus > 0.7 and m.speed < 0.4):
            return ResonanceMode.CONSTRICT
        return ResonanceMode.HOLD

    def map_envelope(
        self,
        cognitive: CognitiveState,
        movement: MovementSample | None = None,
        archetype: SpaceArchetype = SpaceArchetype.DEEP_WORK,
    ) -> SpatialEnvelope:
        c = cognitive.clamp()
        m = (movement or MovementSample()).clamp()
        mode = self.choose_resonance(c, m, archetype)

        # Baseline by archetype
        base_scale = {
            SpaceArchetype.DEEP_WORK: 1.0,
            SpaceArchetype.CREATIVE: 1.1,
            SpaceArchetype.MEDITATIVE: 0.95,
            SpaceArchetype.GALLERY: 1.15,
            SpaceArchetype.PUBLIC_PLAZA: 1.25,
        }[archetype]

        if mode == ResonanceMode.EXPAND:
            scale = base_scale * (1.08 + 0.18 * c.energy + 0.12 * m.path_entropy)
            openness = 0.55 + 0.35 * c.energy
            intimacy = 0.25 + 0.2 * (1.0 - c.energy)
            exploration = 0.6 + 0.3 * m.path_entropy
            color_k = 4500 + 1200 * c.energy  # cooler/brighter open creative
            absorption = 0.35 + 0.2 * c.calm
            texture = 0.3 + 0.2 * m.interaction
            cues = [
                "Soft partitions drift outward; sightlines lengthen.",
                "Floor texture invites lateral exploration.",
                "Acoustics open slightly; light cools and lifts.",
                "Encourage wandering paths and idea-collision zones.",
            ]
        elif mode == ResonanceMode.CONSTRICT:
            scale = base_scale * (0.82 - 0.08 * c.focus + 0.05 * c.stress * 0.1)
            scale = max(0.72, scale)  # never collapse to trapping scale
            openness = 0.25 + 0.2 * (1.0 - c.focus)
            intimacy = 0.55 + 0.3 * c.focus * (1.0 - 0.3 * c.stress)
            exploration = 0.2 + 0.15 * m.attention
            color_k = 3200 + 400 * c.calm  # warmer, intimate
            absorption = 0.55 + 0.3 * c.calm  # quieter
            texture = 0.45 + 0.25 * (1.0 - m.speed)  # softer underfoot when still
            cues = [
                "Envelope gently tightens; focus cocoon without sealed exits.",
                "Warmer light; higher acoustic absorption for deep work / stillness.",
                "Path options remain; intimacy is perceptual, not lockdown.",
                "Optional breath-aligned ambient pulse at perimeter only.",
            ]
        elif mode == ResonanceMode.DRIFT:
            scale = base_scale * (1.0 + 0.05 * np.sin(m.speed * 3.14))
            openness = 0.5 + 0.2 * m.path_entropy
            intimacy = 0.35
            exploration = 0.5 + 0.3 * m.speed
            color_k = 4000 + 800 * m.attention
            absorption = 0.4 + 0.2 * m.interaction
            texture = 0.35 + 0.25 * m.speed
            cues = [
                "Public flow: subtle wall hue and floor grain shift with pace.",
                "High-attention dwell zones soften acoustics locally.",
                "Fast traverse keeps brighter, clearer corridors.",
            ]
        else:  # HOLD
            scale = base_scale
            openness = 0.5
            intimacy = 0.4
            exploration = 0.4
            color_k = 4000
            absorption = 0.45
            texture = 0.4
            cues = [
                "Stable envelope; micro-adjust atmosphere only.",
                "Hold geometry while cognitive state settles.",
            ]

        # Stress never increases trapping: bump openness slightly if stress high during constrict
        if c.stress > 0.7 and mode == ResonanceMode.CONSTRICT:
            openness = min(1.0, openness + 0.15)
            intimacy = max(0.35, intimacy - 0.1)
            cues.append("High stress: keep exits obvious; reduce enclosure pressure.")

        safety = [
            "Intimacy and constrict modes must preserve visible exits and user override.",
            "Scale factors are design scores for media/robotic scenery — not unreviewed structural moves.",
            "No biometric identification required; prefer opt-in aggregate or self-report signals.",
            "Public spaces: prioritize accessibility, crowd safety, and non-coercive cues.",
            "Not a medical or therapeutic device claim.",
        ]

        return SpatialEnvelope(
            scale_factor=float(np.clip(scale, 0.72, 1.45)),
            openness=float(np.clip(openness, 0.0, 1.0)),
            intimacy=float(np.clip(intimacy, 0.0, 1.0)),
            wall_color_temp_k=float(np.clip(color_k, 2700, 6500)),
            acoustic_absorption=float(np.clip(absorption, 0.0, 1.0)),
            floor_texture=float(np.clip(texture, 0.0, 1.0)),
            partition_mobility=float(np.clip(0.3 + 0.5 * abs(scale - 1.0), 0.0, 1.0)),
            exploration_invite=float(np.clip(exploration, 0.0, 1.0)),
            resonance_mode=mode,
            archetype=archetype,
            cues=cues,
            safety_notes=safety,
        )

    def feedback_loop(
        self,
        cognitive: CognitiveState,
        movement: MovementSample,
        envelope: SpatialEnvelope,
    ) -> dict[str, Any]:
        """
        Describe the closed loop: body ↔ mind ↔ space.
        Returns suggested next cognitive/movement nudges (non-coercive).
        """
        c = cognitive.clamp()
        m = movement.clamp()
        # Simple loop gain: how strongly space is co-driving state
        gain = 0.35 + 0.4 * abs(envelope.scale_factor - 1.0) + 0.2 * envelope.intimacy

        if envelope.resonance_mode == ResonanceMode.EXPAND:
            mind_nudge = "Invite curiosity; reduce time-pressure messaging."
            body_nudge = "Lateral steps and longer paths encouraged."
        elif envelope.resonance_mode == ResonanceMode.CONSTRICT:
            mind_nudge = "Support single-task focus; dim peripheral notifications."
            body_nudge = "Settle stance; optional seated deep-work pocket."
        elif envelope.resonance_mode == ResonanceMode.DRIFT:
            mind_nudge = "Gallery pacing: allow dwell without FOMO pressure."
            body_nudge = "Speed-sensitive corridor brightness only."
        else:
            mind_nudge = "Maintain stable attention without over-stimulation."
            body_nudge = "Neutral gait; micro-texture only at edges."

        return {
            "loop_gain": float(np.clip(gain, 0.0, 1.0)),
            "coexistence": "environment co-adapts; user retains override",
            "mind_nudge": mind_nudge,
            "body_nudge": body_nudge,
            "inputs": {
                "cognitive_energy": c.energy,
                "cognitive_focus": c.focus,
                "movement_speed": m.speed,
                "movement_attention": m.attention,
                "path_entropy": m.path_entropy,
            },
            "outputs": {
                "scale_factor": envelope.scale_factor,
                "openness": envelope.openness,
                "acoustic_absorption": envelope.acoustic_absorption,
            },
        }

    def run(
        self,
        *,
        cognitive: CognitiveState | None = None,
        profile: str | None = None,
        movement: MovementSample | None = None,
        archetype: str | SpaceArchetype = SpaceArchetype.DEEP_WORK,
        title: str = "Space as Emotional Resonator",
        write_artifacts: bool = True,
    ) -> SpaceResonatorReport:
        if profile:
            if profile not in DEMO_PROFILES:
                raise ValueError(f"Unknown profile. Available: {list(DEMO_PROFILES)}")
            cognitive = DEMO_PROFILES[profile]
        if cognitive is None:
            cognitive = DEMO_PROFILES["deep_focus"]
        if movement is None:
            # Derive a default movement sample from cognitive state
            c0 = cognitive.clamp()
            movement = MovementSample(
                speed=0.25 + 0.5 * c0.energy * (1.0 - 0.4 * c0.stress),
                interaction=0.3 + 0.4 * c0.presence,
                attention=0.35 + 0.55 * c0.focus,
                path_entropy=0.25 + 0.5 * c0.energy * (1.0 - c0.focus * 0.5),
            )

        if not isinstance(archetype, SpaceArchetype):
            archetype = SpaceArchetype(str(archetype).lower())

        cognitive = cognitive.clamp()
        movement = movement.clamp()
        envelope = self.map_envelope(cognitive, movement, archetype)
        loop = self.feedback_loop(cognitive, movement, envelope)
        narrative = self._narrative(cognitive, movement, envelope, archetype)
        application = (
            "Adaptive rooms and public cultural spaces that co-resonate with movement "
            "and self-reported or opt-in wellness signals—expanding for creative energy, "
            "gently intimating for deep focus, and drifting atmosphere in galleries. "
            "Implementation path: media architecture, kinetic scenery, lighting/audio systems "
            "with explicit user override—not unreviewed structural transformation."
        )

        report = SpaceResonatorReport(
            title=title,
            cognitive=cognitive.to_dict(),
            movement=movement.to_dict(),
            envelope=envelope.to_dict(),
            feedback_loop=loop,
            narrative=narrative,
            application=application,
            classification=self.CLASSIFICATION,
            timestamp=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        )
        if write_artifacts:
            report.artifact_paths = self._write(report)
        self.history.append(report.to_dict())
        return report

    def _narrative(
        self,
        cognitive: CognitiveState,
        movement: MovementSample,
        envelope: SpatialEnvelope,
        archetype: SpaceArchetype,
    ) -> str:
        mode = envelope.resonance_mode.value
        if mode == "expand":
            return (
                f"In a {archetype.value} setting, rising creative/exploratory drive "
                f"(energy={cognitive.energy:.2f}, path_entropy={movement.path_entropy:.2f}) "
                f"opens the kineto-cognitive manifold: scale×{envelope.scale_factor:.2f}, "
                f"higher openness, cooler lift in light, freer movement for innovation."
            )
        if mode == "constrict":
            return (
                f"As immersion deepens (focus={cognitive.focus:.2f}, attention={movement.attention:.2f}), "
                f"the space co-settles into an intimate envelope (scale×{envelope.scale_factor:.2f})—"
                f"warmer, quieter, softer underfoot—supporting stillness without sealing exits."
            )
        if mode == "drift":
            return (
                f"Public flow resonates with pace and dwell: walls, acoustics, and floor grain "
                f"shift subtly (attention={movement.attention:.2f}, speed={movement.speed:.2f}) "
                f"so the gallery coexists with visitors rather than only housing them."
            )
        return (
            f"Envelope holds steady (scale×{envelope.scale_factor:.2f}) while micro-atmosphere "
            f"tracks coexistence between body and mind."
        )

    def format_report(self, report: SpaceResonatorReport) -> str:
        e = report.envelope
        c = report.cognitive
        m = report.movement
        loop = report.feedback_loop
        lines = [
            "══════════════════════════════════════════════════",
            " KINETIC-COGNITIVE ARCHITECTURE",
            " SPACE AS AN EMOTIONAL RESONATOR",
            "══════════════════════════════════════════════════",
            f"Title              : {report.title}",
            f"Classification     : ARCHITECTURAL CONCEPT / UX SIM",
            "",
            "── Cognitive ────────────────────────────────────",
            f"  focus={c['focus']:.2f} calm={c['calm']:.2f} stress={c['stress']:.2f}",
            f"  energy={c['energy']:.2f} presence={c['presence']:.2f}",
            "",
            "── Movement ─────────────────────────────────────",
            f"  speed={m['speed']:.2f} interaction={m['interaction']:.2f}",
            f"  attention={m['attention']:.2f} path_entropy={m['path_entropy']:.2f}",
            "",
            "── Spatial envelope ─────────────────────────────",
            f"  archetype        : {e['archetype']}",
            f"  resonance_mode   : {e['resonance_mode']}",
            f"  scale_factor     : {e['scale_factor']:.3f}  (>1 expand, <1 constrict)",
            f"  openness         : {e['openness']:.2f}",
            f"  intimacy         : {e['intimacy']:.2f}",
            f"  color_temp_k     : {e['wall_color_temp_k']:.0f}",
            f"  acoustic_absorb  : {e['acoustic_absorption']:.2f}",
            f"  floor_texture    : {e['floor_texture']:.2f}",
            f"  exploration      : {e['exploration_invite']:.2f}",
            "",
            "── Feedback loop ────────────────────────────────",
            f"  loop_gain        : {loop['loop_gain']:.2f}",
            f"  mind_nudge       : {loop['mind_nudge']}",
            f"  body_nudge       : {loop['body_nudge']}",
            "",
            "── Cues ─────────────────────────────────────────",
        ]
        for cue in e.get("cues", []):
            lines.append(f"  · {cue}")
        lines += ["", "── Narrative ────────────────────────────────────", report.narrative, ""]
        lines += ["── Application ─────────────────────────────────", report.application, ""]
        lines.append("── Safety ──────────────────────────────────────")
        for note in e.get("safety_notes", []):
            lines.append(f"  · {note}")
        if report.artifact_paths:
            lines.append("")
            lines.append("Artifacts:")
            for k, p in report.artifact_paths.items():
                lines.append(f"  {k}: {p}")
        lines.append("══════════════════════════════════════════════════")
        return "\n".join(lines)

    def _write(self, report: SpaceResonatorReport) -> dict[str, str]:
        ensure_dirs()
        out = WORKSPACE / "deliverables" / "simulations" / "space_resonator"
        out.mkdir(parents=True, exist_ok=True)
        stamp = utc_stamp()
        slug = slugify(report.title)
        stem = f"{stamp}-{slug}"
        md_path = out / f"{stem}.md"
        json_path = out / f"{stem}.json"
        text = self.format_report(report)
        md = f"# {report.title}\n\n**{report.classification}**\n\n```\n{text}\n```\n"
        write_text(md_path, md)
        write_json(json_path, report.to_dict())
        return {"markdown": str(md_path), "json": str(json_path)}


def demo(
    profile: str = "deep_focus",
    archetype: str = "deep_work",
) -> str:
    engine = SpaceEmotionalResonator()
    report = engine.run(
        profile=profile,
        archetype=archetype,
        title=f"Resonator · {archetype} · {profile}",
    )
    return engine.format_report(report)


if __name__ == "__main__":
    print(demo())
