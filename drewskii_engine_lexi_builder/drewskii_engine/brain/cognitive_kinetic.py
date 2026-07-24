"""
Cognitive Influence on Kinetic Flow — wellness UX simulation.

CLASSIFICATION: CONCEPT DESIGN / WELLNESS ENVIRONMENT SIMULATION ONLY

This module models abstract cognitive-state scores (focus, calm, stress) and
maps them to kinetic/environmental parameters (pace, haptic intensity, light
rhythm, floor compliance). It does NOT:

- diagnose medical or psychiatric conditions
- claim clinical neurofeedback efficacy
- process real EEG/medical-device streams as a regulated medical product
- prescribe treatment

Safe inputs: user-selected sliders, demo profiles, or future consumer-grade
wellness APIs with explicit consent. Always label outputs as design guidance.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import numpy as np

from .artifacts import WORKSPACE, ensure_dirs, slugify, utc_stamp, write_json, write_text


class CognitiveAxis(str, Enum):
    FOCUS = "focus"
    CALM = "calm"
    STRESS = "stress"  # abstract arousal score — not a clinical anxiety diagnosis
    ENERGY = "energy"
    PRESENCE = "presence"


class KineticMode(str, Enum):
    DELIBERATE = "deliberate"      # slow, soft, breathing-aligned
    BALANCED = "balanced"
    GOAL_ORIENTED = "goal_oriented"  # faster, sharper cues
    RECOVERY = "recovery"          # guided downshift


@dataclass
class CognitiveState:
    """Abstract 0–1 scores. Not medical measurements."""

    focus: float = 0.5
    calm: float = 0.5
    stress: float = 0.4
    energy: float = 0.5
    presence: float = 0.5
    source: str = "user_selected"  # user_selected | demo_profile | simulated_stream
    notes: str = ""

    def clamp(self) -> "CognitiveState":
        def c(x: float) -> float:
            return float(np.clip(x, 0.0, 1.0))

        return CognitiveState(
            focus=c(self.focus),
            calm=c(self.calm),
            stress=c(self.stress),
            energy=c(self.energy),
            presence=c(self.presence),
            source=self.source,
            notes=self.notes,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self.clamp())


@dataclass
class KineticEnvironment:
    """Environment / body-interface parameters (software + prop design)."""

    pace_bpm: float  # guided movement tempo
    step_compliance: float  # 0 hard floor → 1 soft cushioned
    haptic_intensity: float  # 0–1
    light_pulse_hz: float
    light_warmth: float  # 0 cool → 1 warm
    path_clarity: float  # how strongly space suggests a direction
    breath_guide_inhale_s: float
    breath_guide_exhale_s: float
    mode: KineticMode
    cues: list[str] = field(default_factory=list)
    safety_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["mode"] = self.mode.value if isinstance(self.mode, KineticMode) else str(self.mode)
        return d


@dataclass
class CognitiveKineticReport:
    title: str
    cognitive: dict[str, Any]
    kinetic: dict[str, Any]
    narrative: str
    application: str
    classification: str
    timestamp: str
    artifact_paths: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# Demo personas for storyboard / wellness center pitches
DEMO_PROFILES: dict[str, CognitiveState] = {
    "anxious_arrival": CognitiveState(
        focus=0.35, calm=0.2, stress=0.82, energy=0.55, presence=0.3,
        source="demo_profile",
        notes="High abstract stress; guide deliberate pace + breath.",
    ),
    "deep_focus": CognitiveState(
        focus=0.88, calm=0.7, stress=0.25, energy=0.6, presence=0.8,
        source="demo_profile",
        notes="Stable focus; minimal interruption, soft peripheral cues.",
    ),
    "post_session_calm": CognitiveState(
        focus=0.45, calm=0.85, stress=0.15, energy=0.35, presence=0.75,
        source="demo_profile",
        notes="Recovery; slow tempo, warm light, soft floor.",
    ),
    "activation": CognitiveState(
        focus=0.7, calm=0.4, stress=0.45, energy=0.85, presence=0.65,
        source="demo_profile",
        notes="Goal-oriented kinetic cues; clearer path, higher tempo.",
    ),
}


class CognitiveKineticFlow:
    """
    Map cognitive-state scores → kinetic / environmental feedback parameters.
    """

    CLASSIFICATION = (
        "CONCEPT DESIGN / WELLNESS UX SIMULATION ONLY — "
        "not a medical device, diagnosis, or treatment system"
    )

    def __init__(self) -> None:
        self.history: list[dict[str, Any]] = []

    def select_mode(self, state: CognitiveState) -> KineticMode:
        s = state.clamp()
        if s.stress >= 0.65 or s.calm <= 0.35:
            return KineticMode.DELIBERATE
        if s.calm >= 0.7 and s.energy <= 0.45:
            return KineticMode.RECOVERY
        if s.energy >= 0.7 and s.focus >= 0.55 and s.stress < 0.55:
            return KineticMode.GOAL_ORIENTED
        return KineticMode.BALANCED

    def map_environment(self, state: CognitiveState) -> KineticEnvironment:
        s = state.clamp()
        mode = self.select_mode(s)

        # Base continuous blends
        # High stress → slower pace, softer floor, warmer slower light, stronger breath guide
        # High energy + focus → faster pace, firmer floor, cooler clearer path
        pace = 48 + 42 * s.energy * (1.0 - 0.55 * s.stress) * (0.6 + 0.4 * s.focus)
        compliance = 0.25 + 0.65 * (0.55 * s.stress + 0.45 * (1.0 - s.energy))
        haptic = 0.15 + 0.55 * (0.4 * s.presence + 0.3 * s.focus + 0.3 * (1.0 - s.stress))
        # Breath-aligned light: slower when stressed/calm-seeking
        pulse = 0.05 + 0.18 * (1.0 - s.stress) * (0.5 + 0.5 * s.energy)
        warmth = 0.35 + 0.55 * (0.5 * s.calm + 0.5 * s.stress)  # warm for calm-down and comfort
        clarity = 0.3 + 0.6 * s.focus * (1.0 - 0.4 * s.stress)

        inhale = 3.5 + 1.5 * s.stress  # longer inhale cue when stressed
        exhale = 4.0 + 2.0 * s.stress  # longer exhale for downshift narrative

        cues: list[str] = []
        if mode == KineticMode.DELIBERATE:
            pace = min(pace, 58)
            compliance = max(compliance, 0.7)
            pulse = min(pulse, 0.12)
            cues = [
                "Slow, deliberate steps — match the floor pulse.",
                "Hands: optional guided breath arc (inhale up, exhale down).",
                "Haptics: soft metatarsal taps on each exhale.",
                "Lighting: warm, low-frequency pulse aligned to breath.",
            ]
        elif mode == KineticMode.GOAL_ORIENTED:
            pace = max(pace, 72)
            compliance = min(compliance, 0.4)
            clarity = max(clarity, 0.7)
            cues = [
                "Clear path markers; slightly firmer floor response.",
                "Shorter haptic ticks at target waypoints.",
                "Cooler edge lighting toward the goal vector.",
                "Keep breath free; avoid over-coaching during activation.",
            ]
        elif mode == KineticMode.RECOVERY:
            pace = min(pace, 52)
            compliance = max(compliance, 0.75)
            warmth = max(warmth, 0.75)
            cues = [
                "Cushioned path; minimal directional pressure.",
                "Breath guide dominant; movement optional.",
                "Warm ambient field; very low haptic intensity.",
            ]
        else:
            cues = [
                "Balanced tempo; gentle directional hints.",
                "Haptics only on path edges if user drifts.",
            ]

        safety = [
            "Not a medical or psychiatric diagnosis system.",
            "User can override pace, haptics, and exit at any time.",
            "No locked rooms, no forced movement, no clinical claims.",
            "Biofeedback sensors (if added later) require consent and wellness-grade labeling.",
            "Do not market as treatment for anxiety, depression, or neurological disease.",
        ]

        return KineticEnvironment(
            pace_bpm=float(np.clip(pace, 40, 110)),
            step_compliance=float(np.clip(compliance, 0.0, 1.0)),
            haptic_intensity=float(np.clip(haptic, 0.0, 1.0)),
            light_pulse_hz=float(np.clip(pulse, 0.03, 0.35)),
            light_warmth=float(np.clip(warmth, 0.0, 1.0)),
            path_clarity=float(np.clip(clarity, 0.0, 1.0)),
            breath_guide_inhale_s=float(np.clip(inhale, 3.0, 6.0)),
            breath_guide_exhale_s=float(np.clip(exhale, 3.5, 8.0)),
            mode=mode,
            cues=cues,
            safety_notes=safety,
        )

    def run(
        self,
        state: CognitiveState | None = None,
        profile: str | None = None,
        title: str = "Cognitive → Kinetic Flow Session",
        write_artifacts: bool = True,
    ) -> CognitiveKineticReport:
        if profile:
            if profile not in DEMO_PROFILES:
                raise ValueError(
                    f"Unknown profile '{profile}'. Available: {list(DEMO_PROFILES)}"
                )
            state = DEMO_PROFILES[profile]
        if state is None:
            state = DEMO_PROFILES["anxious_arrival"]

        state = state.clamp()
        env = self.map_environment(state)

        narrative = self._narrative(state, env)
        application = (
            "Wellness-center concept: optional consumer biofeedback or self-report "
            "drives environmental kinetic cues (floor compliance, haptics, light rhythm, "
            "breath-linked pacing). Real-time adaptation is a UX loop, not a clinical protocol."
        )

        report = CognitiveKineticReport(
            title=title,
            cognitive=state.to_dict(),
            kinetic=env.to_dict(),
            narrative=narrative,
            application=application,
            classification=self.CLASSIFICATION,
            timestamp=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        )
        if write_artifacts:
            report.artifact_paths = self._write(report)
        self.history.append(report.to_dict())
        return report

    def _narrative(self, state: CognitiveState, env: KineticEnvironment) -> str:
        mode = env.mode.value
        if env.mode == KineticMode.DELIBERATE:
            story = (
                "The system reads elevated abstract stress / low calm and shifts the space "
                "toward deliberate kinetic flow: softer steps, slower tempo, warm breath-synced light, "
                "and gentle haptic cues that invite longer exhales—not forced compliance."
            )
        elif env.mode == KineticMode.GOAL_ORIENTED:
            story = (
                "With higher energy and focus, the space clarifies a path and raises tempo slightly, "
                "using firmer floor response and waypoint haptics to support goal-oriented movement "
                "without punitive intensity."
            )
        elif env.mode == KineticMode.RECOVERY:
            story = (
                "Calm is high and energy low: the environment prioritizes recovery—cushioned path, "
                "warm field, optional movement, breath guide as the primary kinetic language."
            )
        else:
            story = (
                "A balanced cognitive profile yields moderate pace, soft edge guidance, "
                "and light haptic presence—fluid interaction without over-steering."
            )
        return (
            f"{story} Mode={mode}; pace≈{env.pace_bpm:.0f} guided BPM; "
            f"floor compliance={env.step_compliance:.2f}; light pulse={env.light_pulse_hz:.2f} Hz."
        )

    def format_report(self, report: CognitiveKineticReport) -> str:
        c = report.cognitive
        k = report.kinetic
        lines = [
            "══════════════════════════════════════════════════",
            " COGNITIVE INFLUENCE ON KINETIC FLOW",
            " WELLNESS UX SIMULATION — NOT A MEDICAL DEVICE",
            "══════════════════════════════════════════════════",
            f"Title              : {report.title}",
            f"Classification     : CONCEPT / WELLNESS SIM",
            "",
            "── Cognitive state (abstract 0–1) ───────────────",
            f"  focus={c['focus']:.2f}  calm={c['calm']:.2f}  stress={c['stress']:.2f}",
            f"  energy={c['energy']:.2f}  presence={c['presence']:.2f}",
            f"  source={c['source']}",
            "",
            "── Kinetic / environment mapping ────────────────",
            f"  mode             : {k['mode']}",
            f"  pace_bpm         : {k['pace_bpm']:.1f}",
            f"  step_compliance  : {k['step_compliance']:.2f}  (soft floor ↑)",
            f"  haptic_intensity : {k['haptic_intensity']:.2f}",
            f"  light_pulse_hz   : {k['light_pulse_hz']:.3f}",
            f"  light_warmth     : {k['light_warmth']:.2f}",
            f"  path_clarity     : {k['path_clarity']:.2f}",
            f"  breath inhale/ex : {k['breath_guide_inhale_s']:.1f}s / {k['breath_guide_exhale_s']:.1f}s",
            "",
            "── Cues ─────────────────────────────────────────",
        ]
        for cue in k.get("cues", []):
            lines.append(f"  · {cue}")
        lines += ["", "── Narrative ────────────────────────────────────", report.narrative, ""]
        lines += ["── Application ─────────────────────────────────", report.application, ""]
        lines.append("── Safety ──────────────────────────────────────")
        for note in k.get("safety_notes", []):
            lines.append(f"  · {note}")
        if report.artifact_paths:
            lines.append("")
            lines.append("Artifacts:")
            for key, path in report.artifact_paths.items():
                lines.append(f"  {key}: {path}")
        lines.append("══════════════════════════════════════════════════")
        return "\n".join(lines)

    def _write(self, report: CognitiveKineticReport) -> dict[str, str]:
        ensure_dirs()
        out = WORKSPACE / "deliverables" / "simulations" / "cognitive_kinetic"
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
            "```\n" + text + "\n```\n"
        )
        write_text(md_path, md)
        write_json(json_path, report.to_dict())
        return {"markdown": str(md_path), "json": str(json_path)}


def demo(profile: str = "anxious_arrival") -> str:
    flow = CognitiveKineticFlow()
    report = flow.run(profile=profile, title="Wellness Center — Kinetic Flow Demo")
    return flow.format_report(report)


if __name__ == "__main__":
    print(demo())
