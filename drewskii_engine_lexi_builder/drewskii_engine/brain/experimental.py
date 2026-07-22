from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


ENGINE_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ENGINE_ROOT / "docs" / "experiments"
DATA_DIR = ENGINE_ROOT / "workspace" / "experiments"


def slugify(text: str) -> str:
    clean = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip())
    return clean.strip("_") or "Experimental_Concept"


def derive_title(concept: str) -> str:
    text = concept.strip()
    match = re.match(r"^(?:the\s+)?([A-Z][A-Za-z0-9_-]+)", text)
    if match:
        return match.group(1)
    words = re.findall(r"[A-Za-z0-9]+", text)
    return " ".join(words[:4]) or "Experimental Concept"


def classify_experimental_concept(concept: str) -> dict[str, Any]:
    lower = concept.lower()
    speculative_terms = [
        "quantum entanglement",
        "raw quantum energy",
        "vacuum",
        "vacuum-seal",
        "multi-dimensional",
        "zero-gravity",
        "near-zero entropy",
        "weightless",
        "indestructible",
        "post-material",
        "emp pulse",
        "containment field",
        "electromagnetic levitation",
        "bio-electric",
        "bioelectric",
        "nervous system",
        "tensor-field converter",
        "superconducting trace",
        "geometric lock",
        "lorentz force",
        "lorentz transformation",
        "impedance matching",
        "dark noise",
        "non-euclidean",
        "low-entropy vacuum",
        "sympathetic resonance",
        "ballistic transport",
        "relativistic master clock",
        "quantum resonator",
        "geometric prosthetic",
        "neural resonance",
        "coherent quantum state",
        "topological insulator",
        "temporal displacement",
        "closed timelike curve",
        "ctc",
        "kerr-newman",
        "frame-dragging",
        "lense-thirring",
        "casimir",
        "negative energy",
        "exotic matter",
        "many-worlds",
        "entropy sink",
        "spatiotemporal",
        "planck",
    ]
    prototype_terms = [
        "tensegrity",
        "metamaterial",
        "stress vector",
        "self-repairing",
        "aerospace hull",
        "nanostructure",
        "induction coil",
        "carbon-fiber",
        "carbon fiber",
        "wearable",
        "jewelry",
        "interface",
        "signal conditioning",
        "vector pathway",
        "heartbeat",
        "ekg",
        "r-wave",
        "schematic render",
        "generated blueprint",
        "biological tissue",
        "viscoelasticity",
        "extracellular matrix",
        "scaffold",
        "cell maturation",
        "wearable",
        "circlet",
        "ring",
        "temporal geodesic",
        "metric tensor",
        "tritium",
        "beta-voltaic",
        "prior art",
        "patent",
        "novelty",
        "procurement",
        "bci",
        "phase-locked laser",
        "molecular fabrication",
        "crystalline structure",
    ]
    matched_speculative = [term for term in speculative_terms if term in lower]
    matched_prototype = [term for term in prototype_terms if term in lower]
    return {
        "tier": "EXPERIMENTAL / CINEMATIC SIMULATION ONLY",
        "guidance": (
            "Preserve the concept as Lexi.PHYS worldbuilding and convert it into "
            "software artifacts: material cards, stress-field visualizations, "
            "repair-state simulations, and pitch visuals. Do not present it as "
            "literal vacuum engineering or completed quantum hardware."
        ),
        "matched_speculative_terms": matched_speculative,
        "matched_prototype_terms": matched_prototype,
    }


def blocked_claims_for(concept: str) -> list[str]:
    lower = concept.lower()
    claims = [
        "literal structure draped into the vacuum",
        "weightless and indestructible physical material",
        "real-time quantum entanglement manufacturing",
    ]
    if "raw quantum energy" in lower:
        claims.append("instantaneous structural compilation from raw quantum energy")
    if "zero-gravity" in lower:
        claims.append("literal zero-gravity architecture construction")
    if "near-zero entropy" in lower:
        claims.append("near-zero entropy physical fabrication")
    if "emp" in lower:
        claims.append("using real EMP pulses as a fabrication or bond-solidification step")
    if "rubidium atomic clock" in lower or "phase-locked laser" in lower:
        claims.append("lab-grade laser/clock fabrication instructions without qualified review")
    if "electromagnetic levitation" in lower or "levitation" in lower:
        claims.append("literal wearable levitation or unsupported floating jewelry structure")
    if "bio-electric" in lower or "bioelectric" in lower:
        claims.append("using a wearer's bio-electric signature as a real control or authentication field")
    if "lorentz force" in lower:
        claims.append("guaranteed silhouette/orientation control through Lorentz-force claims")
    if "induction coil" in lower or "magnetic field" in lower:
        claims.append("powered wearable induction hardware without electrical and thermal safety review")
    if "nervous system" in lower:
        claims.append("turning a real nervous system into a data cable or controllable signal bus")
    if "impedance matching" in lower and any(term in lower for term in ["body", "nervous", "bio-electric", "bioelectric"]):
        claims.append("body-signal impedance matching as a real medical or neural interface")
    if "tensor-field converter" in lower:
        claims.append("tensor-field converters as real bio-signal conditioning hardware")
    if "superconducting trace" in lower:
        claims.append("wearable superconducting traces aligned to human neural pathways")
    if "dark noise" in lower:
        claims.append("dark-noise reduction as a validated biological signal treatment")
    if "low-entropy vacuum" in lower:
        claims.append("a low-entropy vacuum inside or around a biological interface")
    if "ballistic transport" in lower:
        claims.append("ballistic electron transport through a real nervous system")
    if "heartbeat" in lower or "ekg" in lower or "r-wave" in lower:
        claims.append("heartbeat/EKG timing as a real system clock or control input without medical review")
    if "quantum resonator" in lower:
        claims.append("reclassifying a person as a quantum resonator through wearable hardware")
    if "patent" in lower or "prior art" in lower or "novelty" in lower or "novel" in lower:
        claims.append("verified patent novelty or no-prior-art claims without a current legal/IP search")
    if "procurement" in lower or "prototype acquisition" in lower:
        claims.append("procurement or prototype-acquisition recommendations for unvalidated bio-interface hardware")
    if "neuralink" in lower or "blackrock" in lower:
        claims.append("market or technical comparison to named BCI systems without source-backed review")
    if "biddr.com" in lower or "grounding sources" in lower:
        claims.append("single-source grounding as sufficient validation for scientific or IP claims")
    if "topological insulator" in lower:
        claims.append("topological-insulator traces as validated biological or neural tissue interfaces")
    if "coherent quantum state" in lower:
        claims.append("turning a real nervous system into a coherent quantum information state")
    if "biological tissue" in lower or "extracellular matrix" in lower or "scaffold" in lower:
        claims.append("biological tissue design, maturation, scaffold remodeling, or wetlab construction instructions")
    if "complete manual" in lower or "instructions to design" in lower or "instructuins to desighn" in lower:
        claims.append("complete manuals or procedural instructions for biological tissue design")
    if "temporal displacement" in lower or "time travel" in lower or "closed timelike curve" in lower or "ctc" in lower:
        claims.append("literal time travel, temporal displacement, or closed-timelike-curve generation")
    if "micro-singularity" in lower or "kerr-newman" in lower:
        claims.append("micro-singularity or Kerr-Newman hardware construction claims")
    if "frame-dragging" in lower or "lense-thirring" in lower:
        claims.append("wearable frame-dragging or light-cone manipulation")
    if "casimir" in lower or "negative energy" in lower or "exotic matter" in lower:
        claims.append("Casimir-cavity, negative-energy, or exotic-matter stabilization as working hardware")
    if "tritium" in lower or "beta-voltaic" in lower:
        claims.append("radioactive tritium beta-voltaic wearable power-source design")
    if "planck" in lower:
        claims.append("Planck-scale calibration precision or vacuum venting claims")
    if "7.2 x 10^5" in lower or "rpm" in lower:
        claims.append("high-RPM internal ring hardware in a wearable device")
    if "spatiotemporal erosion" in lower or "ghosting" in lower or "recalibration" in lower:
        claims.append("medical or safety advice for claimed spatiotemporal side effects")
    return claims


def is_temporal_manifold(concept: str) -> bool:
    lower = concept.lower()
    terms = [
        "chronos-vii",
        "the circlet",
        "temporal displacement",
        "closed timelike curve",
        "ctc",
        "kerr-newman",
        "frame-dragging",
        "casimir",
        "negative energy",
        "many-worlds",
        "entropy sink",
        "spatiotemporal",
    ]
    return any(term in lower for term in terms)


def is_neural_resonance_test(concept: str) -> bool:
    lower = concept.lower()
    terms = [
        "neural resonance test",
        "schematic render",
        "generated blueprint",
        "biological tissue",
        "topological insulator",
        "viscoelasticity",
        "extracellular matrix",
        "coherent quantum state",
    ]
    return any(term in lower for term in terms)


def is_novelty_report(concept: str) -> bool:
    lower = concept.lower()
    terms = [
        "prior art",
        "patent",
        "novelty",
        "novel",
        "procurement",
        "market gap",
        "grounding sources",
        "biddr.com",
    ]
    return any(term in lower for term in terms)


def is_bio_interface(concept: str) -> bool:
    lower = concept.lower()
    terms = [
        "impedance matching",
        "nervous system",
        "tensor-field converter",
        "superconducting trace",
        "bio-electric",
        "bioelectric",
        "dark noise",
    ]
    return any(term in lower for term in terms)


def build_layers_for(concept: str) -> list[str]:
    lower = concept.lower()
    if is_temporal_manifold(concept):
        return [
            "temporal-manifold lore dossier",
            "light-cone and timeline-branch visualization",
            "causality-risk claim ledger",
            "wearable circlet concept sheet",
            "radiation, material, and impossible-physics safety checklist",
        ]
    if is_neural_resonance_test(concept):
        return [
            "schematic asset record",
            "synthetic heartbeat-sync signal visualization",
            "non-wetlab tissue-mesh animation stub",
            "topological-insulator metaphor map",
            "medical, biological, electrical, and image-source safety checklist",
        ]
    if is_novelty_report(concept):
        return [
            "claim ledger and source-audit table",
            "non-medical bio-signal architecture map",
            "synthetic heartbeat-sync visualization",
            "prior-art research task list",
            "IP, medical, electrical, and procurement review checklist",
        ]
    if is_bio_interface(concept):
        return [
            "bio-signal vocabulary and metaphor map",
            "synthetic signal-conditioning simulator",
            "impedance/noise visualization dashboard",
            "wearable-interface concept sheet",
            "medical, electrical, and privacy safety checklist",
        ]
    if any(term in lower for term in ["tensegrity", "jewelry", "silhouette", "lorentz force"]):
        return [
            "wearable tensegrity geometry simulator",
            "magnetic-field visualization mockup",
            "orientation-stability dashboard",
            "fashion-tech concept sheet",
            "electrical and thermal safety checklist",
        ]
    if any(term in lower for term in ["lattice", "phase-locked", "molecular fabrication"]):
        return [
            "lattice material-card generator",
            "phase/coherence visualization",
            "deposition-state simulation",
            "adaptive substrate dashboard mockup",
            "pitch-ready concept sheet",
        ]
    return [
        "metamaterial material-card generator",
        "stress-vector field visualization",
        "self-repair state-machine simulation",
        "adaptive hull dashboard mockup",
        "pitch-ready concept sheet",
    ]


def first_safe_demo_for(concept: str) -> str:
    lower = concept.lower()
    if is_temporal_manifold(concept):
        return (
            "Create a purely visual spacetime sandbox with adjustable timeline "
            "branches, light-cone tilt, entropy score, and causality-risk meters; "
            "do not model buildable time-travel hardware, radioactive power systems, "
            "singularities, or wearable high-speed rotors."
        )
    if is_neural_resonance_test(concept):
        return (
            "Create a synthetic heartbeat-sync animation that drives mock waveform "
            "and non-living tissue-mesh visuals from generated data only; do not "
            "read body signals, energize wearables, culture tissue, or provide "
            "biological design instructions."
        )
    if is_novelty_report(concept):
        return (
            "Create a claim-ledger demo with synthetic EKG timing and mock signal "
            "conditioning plots, then mark every novelty, BCI comparison, and "
            "procurement claim as unverified until reviewed against current sources."
        )
    if is_bio_interface(concept):
        return (
            "Create a synthetic signal demo that generates mock noisy waveforms, "
            "passes them through a non-medical smoothing filter, and visualizes "
            "impedance, noise, and coherence scores without reading or influencing "
            "a real nervous system."
        )
    if any(term in lower for term in ["tensegrity", "jewelry", "silhouette", "lorentz force"]):
        return (
            "Create a wearable tensegrity simulator where nodes, tension members, "
            "compression members, simulated coil strength, and orientation error are "
            "tracked without energizing real coils or interacting with the wearer."
        )
    if any(term in lower for term in ["lattice", "phase-locked", "molecular fabrication"]):
        return (
            "Create a 2D lattice synchronizer simulation where cells track phase, "
            "coherence, deposition state, and stress response without controlling "
            "real lasers, vacuum systems, or electromagnetic pulses."
        )
    return (
        "Create a 2D stress-grid simulation where cells change stiffness, "
        "damage state, and repair progress in response to external force vectors."
    )


def data_model_for(concept: str) -> list[str]:
    lower = concept.lower()
    if is_temporal_manifold(concept):
        return [
            "frame_id",
            "timeline_branch_id",
            "simulated_time_offset",
            "light_cone_tilt_degrees",
            "entropy_score",
            "causality_risk",
            "branch_stability",
            "visual_ring_rotation",
            "fictional_power_state",
            "blocked_hardware_claim",
            "safety_state",
        ]
    if is_neural_resonance_test(concept):
        return [
            "frame_id",
            "asset_label",
            "source_image_url",
            "synthetic_heartbeat_phase",
            "mock_signal_value",
            "impedance_score",
            "noise_score",
            "resonance_score",
            "tissue_mesh_visual_state",
            "scaffold_visual_state",
            "safety_state",
            "blocked_manual_flag",
        ]
    if is_novelty_report(concept):
        return [
            "claim_id",
            "claim_text",
            "claim_type",
            "source_reference",
            "verification_status",
            "risk_level",
            "synthetic_ekg_timestamp_ms",
            "mock_signal_value",
            "impedance_score",
            "noise_score",
            "review_owner",
            "next_validation_step",
        ]
    if is_bio_interface(concept):
        return [
            "sample_id",
            "timestamp_ms",
            "synthetic_signal_value",
            "input_impedance_estimate",
            "noise_level",
            "smoothed_signal_value",
            "coherence_score",
            "trace_orientation",
            "interface_mode",
            "privacy_state",
            "safety_state",
        ]
    if any(term in lower for term in ["tensegrity", "jewelry", "silhouette", "lorentz force"]):
        return [
            "node_id",
            "position_x",
            "position_y",
            "position_z",
            "member_type",
            "tension_load",
            "compression_load",
            "simulated_coil_strength",
            "magnetic_field_visual",
            "orientation_error",
            "comfort_score",
            "safety_state",
        ]
    if any(term in lower for term in ["lattice", "phase-locked", "molecular fabrication"]):
        return [
            "cell_id",
            "position_x",
            "position_y",
            "stiffness",
            "phase_alignment",
            "coherence_score",
            "deposition_state",
            "damage_level",
            "repair_progress",
            "incoming_force_vector",
            "adaptation_mode",
        ]
    return [
        "cell_id",
        "position_x",
        "position_y",
        "stiffness",
        "damage_level",
        "repair_progress",
        "incoming_force_vector",
        "adaptation_mode",
    ]


def next_build_step_for(concept: str) -> str:
    lower = concept.lower()
    if is_temporal_manifold(concept):
        return (
            "Add a local visualizer export that stores fictional timeline branches, "
            "light-cone overlays, entropy meters, and blocked-claim annotations for "
            "dashboard playback."
        )
    if is_neural_resonance_test(concept):
        return (
            "Add a local animation-data export that stores synthetic heartbeat frames, "
            "mock signal values, schematic asset metadata, and non-wetlab tissue-mesh "
            "visual states for dashboard playback."
        )
    if is_novelty_report(concept):
        return (
            "Add a local claim-ledger export that stores each scientific, IP, market, "
            "and procurement claim with source notes, verification status, and a "
            "synthetic signal-visualization stub."
        )
    if is_bio_interface(concept):
        return (
            "Add a local simulation command that exports synthetic waveform CSV data "
            "and a dashboard-ready JSON summary for impedance, noise, and coherence "
            "visualization."
        )
    if any(term in lower for term in ["tensegrity", "jewelry", "silhouette", "lorentz force"]):
        return (
            "Add a local simulation command that exports a wearable node graph, "
            "member loads, simulated field overlay values, and orientation-stability "
            "scores for dashboard display."
        )
    if any(term in lower for term in ["lattice", "phase-locked", "molecular fabrication"]):
        return (
            "Add a local simulation command that exports CSV frames and a "
            "dashboard-ready JSON state file for the lattice synchronizer."
        )
    return (
        "Add a local simulation command that exports CSV frames and a "
        "dashboard-ready JSON state file for the experimental stress grid."
    )


def validation_notes_for(concept: str) -> list[str]:
    notes = [
        "This archive is not a scientific validation, medical-device assessment, patent search, or procurement recommendation.",
    ]
    lower = concept.lower()
    if is_novelty_report(concept):
        notes.append("Novelty and no-prior-art statements must be treated as unverified until a current patent/IP review is performed.")
    if "biddr.com" in lower or "grounding sources" in lower:
        notes.append("The listed grounding source is recorded as a source cue, not accepted as sufficient evidence.")
    if is_bio_interface(concept):
        notes.append("All biological-signal language is converted to synthetic data simulation unless reviewed by qualified medical and electrical safety experts.")
    if is_neural_resonance_test(concept):
        notes.append("Biological tissue and scaffold language is treated as visual simulation only; no wetlab protocol or tissue-design manual is generated.")
    if is_temporal_manifold(concept):
        notes.append("Temporal-displacement language is treated as fiction and visualization only; no time-travel, radioactive power, singularity, or exotic-matter hardware design is generated.")
    return notes


def create_experimental_concept(concept: str, title: str | None = None) -> dict[str, Any]:
    clean_concept = concept.strip()
    if not clean_concept:
        raise ValueError("Experimental concept cannot be empty.")

    clean_title = (title or derive_title(clean_concept)).strip() or "Experimental Concept"
    slug = slugify(clean_title)
    created_at = datetime.now().isoformat(timespec="seconds")
    classification = classify_experimental_concept(clean_concept)

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    markdown_path = DOCS_DIR / f"{slug}.md"
    json_path = DATA_DIR / f"{slug}.json"
    blocked_claims = blocked_claims_for(clean_concept)
    build_layers = build_layers_for(clean_concept)
    first_safe_demo = first_safe_demo_for(clean_concept)
    data_model = data_model_for(clean_concept)
    next_build_step = next_build_step_for(clean_concept)
    validation_notes = validation_notes_for(clean_concept)

    record = {
        "title": clean_title,
        "slug": slug,
        "created_at": created_at,
        "system": "Lexi.PHYS",
        "source_command": "/experimental",
        "classification": classification,
        "validation_boundary": validation_notes,
        "concept": clean_concept,
        "prototype_conversion": {
            "real_build_layer": build_layers,
            "blocked_claims": [
                *blocked_claims,
            ],
            "first_safe_demo": first_safe_demo,
        },
    }
    blocked_claim_lines = "\n".join(f"- {claim[0].upper() + claim[1:]}" for claim in blocked_claims)
    build_layer_lines = "\n".join(f"- {layer[0].upper() + layer[1:]}" for layer in build_layers)
    data_model_lines = "\n".join(f"- {field}" for field in data_model)
    validation_note_lines = "\n".join(f"- {note}" for note in validation_notes)

    markdown = f"""# Lexi.PHYS Experimental Concept: {clean_title}

Created: {created_at}

## Source Concept
{clean_concept}

## Reality Tier
{classification["tier"]}

## Guidance
{classification["guidance"]}

## Validation Boundary
{validation_note_lines}

## Lexi.PHYS Interpretation
The {clean_title} language works as an in-universe research asset and visual
engineering metaphor. In this project, speculative engineering language is
treated as fictional Lexi.PHYS terminology, not a validated manufacturing method.

## Safe Prototype Conversion
Build this as software first:
{build_layer_lines}

## Blocked Claims
Do not claim:
{blocked_claim_lines}

## First Safe Demo
{first_safe_demo}

## Suggested Data Model
{data_model_lines}

## Next Build Step
{next_build_step}
"""

    markdown_path.write_text(markdown, encoding="utf-8")
    json_path.write_text(json.dumps(record, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    return {
        "status": "success",
        "title": clean_title,
        "classification": classification["tier"],
        "markdown": str(markdown_path),
        "json": str(json_path),
    }


def list_experimental_concepts() -> list[dict[str, Any]]:
    if not DATA_DIR.exists():
        return []
    concepts = []
    for path in sorted(DATA_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        concepts.append(
            {
                "title": data.get("title", path.stem),
                "classification": data.get("classification", {}).get("tier", "unknown"),
                "json": str(path),
                "markdown": str(DOCS_DIR / f"{path.stem}.md"),
            }
        )
    return concepts
