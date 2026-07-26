"""Drewskii.Engine CLI — builder command center."""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Ensure package root is importable when run as script
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from brain.planner import build_plan, roadmap, save_plan
from brain.memory import Memory
from brain.code_generator import generate_brand_blueprint, generate_ui_shell
from brain.blueprint_forge import forge_blueprint
from brain.documentary import export_documentary_map, export_offer_map
from brain.eval_log import log_evaluation
from brain.experimental import create_experimental_concept, list_experimental_concepts
from brain.safety import is_blocked, blocked_reason
from brain.logger import log_event
from brain.artifacts import DASHBOARD_DATA, ensure_dirs, write_json
from android.termux_helpers import helpers_markdown, list_helpers, prepare_helper


MANIFEST_PATH = PROJECT_ROOT / "lexi_project_manifest.json"
IDENTITY_PATH = PROJECT_ROOT / "lexi_identity.json"
SKILLS_PATH = PROJECT_ROOT / "lexi_skills.json"
MODEL_PROFILE_PATH = PROJECT_ROOT / "model_profiles" / "lexi_phys.json"
MODEL_DOC_PATH = PROJECT_ROOT / "docs" / "models" / "Lexi_PHYS.md"
DREWSKII_MODEL_PROFILE_PATH = PROJECT_ROOT / "model_profiles" / "drewskii_engine.json"
DREWSKII_MODEL_DOC_PATH = PROJECT_ROOT / "docs" / "models" / "Drewskii_Engine.md"
CORTANA_MODEL_PROFILE_PATH = PROJECT_ROOT / "model_profiles" / "cortana_phys.json"
CORTANA_MODEL_DOC_PATH = PROJECT_ROOT / "docs" / "models" / "CORTANA_PHYS.md"
PROTOTYPE_PATH = PROJECT_ROOT / "docs" / "user_space_to_official_app.md"
DOCUMENTARY_PATH = PROJECT_ROOT / "docs" / "lexi_documentary_map.md"
TOP_LAYER_PATH = PROJECT_ROOT / "docs" / "drewskii_engine_documentary_top_layer.md"

BANNER = """
Drewskii.Engine online.
Architecture locked. Lexi build path engaged.

Type 'help' to see commands.
"""

HELP = """
Commands:
  help                         Show this menu
  manifest                     Show the project manifest
  identity                     Show the Lexi identity contract
  model [name]                 Profile: Lexi.PHYS | Drewskii.Engine | CORTANA-PHYS
  cortana status|mint|keys|models|invent|ask   CORTANA-PHYS model layer
  skills                       Show the Lexi skill catalog
  prototype                    Show the user-space to official app path
  documentary                  Show the LEXI-9-OMEGA documentary map (docs)
  documentary-map              Export documentary map → MD/JSON/HTML
  offer / offer-map            Export paid offer map + one-page offer
  top-layer                    Show the Drewskii.Engine documentary map
  software                     Show the software build path
  experimental <concept>       Archive a Lexi.PHYS experimental concept
  experiments                  List archived experimental concepts
  retro [mass] [authority]     RetroCausalEngine sim (goal→params optimizer)
  grav [density]               GravitationalProcessor sim (curvature/logic/opt)
  kali [density]               Constraint-pressure sim (NOT network attacks)
  mastermind [mass] [auth]     Full cycle: retro → grav → kali
  kinetic [profile]            Cognitive→kinetic wellness flow sim
  resonator [profile] [arch]   Space as emotional resonator (floor plan sim)
  manifold [profile] [arch] [society]  Full kineto-cognitive manifold
  cocoon [spin] [energize]     Transcendent Cocoon V3 inverse-physics sim
  cocoon-resonance             Neural Resonance Test (design sweep)
  autonomy [seconds]           Autonomy OS control-loop simulation
  stack                        Local-first Intelligence Model Stack (Stage 1)
  stack run                    Full Stage-1 automation pipeline
  stack brand <name|vibe|aud|offer>
  stack pack <name|vibe|aud|offer>   Alias: brand pack + ZIP path
  stack rules                  Operating rules + promotion gate
  stack promote <feature>      Promotion gate checklist
  blueprint [name]             Quick Brand Blueprint Pack (MD/JSON/HTML)
  forge [name]                 Blueprint Forge (+ starter code templates)
  forge name | vibe | audience | offer
  roadmap                      Show Lexi build roadmap
  plan <idea>                  Plan + save to SQLite/files
  remember key=value           Save a project memory
  remember <note>              Save a timestamped note
  recall <key>                 Recall a memory
  memory                       Show all saved memory
  stats                        SQLite memory / plan / deliverable counts
  deliverables                 List recent deliverables
  evals                        List recent evaluation logs
  eval <category> | <subject> | <notes> [| score]
  list                         Show project files and commands
  log <note>                   Save a project log
  generate-ui                  Refresh web dashboard shell
  termux                       List Termux helpers (approved catalog)
  termux <id>                  Prepare helper script (asks approval)
  termux <id> --yes            Prepare helper after explicit approval
  exit / quit                  Close the engine
"""


def read_json_file(path: Path, label: str) -> str:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return f"{label} unavailable: {exc}"
    return json.dumps(data, indent=2, ensure_ascii=True)


def read_text_file(path: Path, label: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        return f"{label} unavailable: {exc}"


def remember(memory: Memory, data: str) -> str:
    if "=" in data:
        key, value = data.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key or not value:
            return "Use: remember key=value"
    else:
        value = data.strip()
        if not value:
            return "Use: remember key=value or remember <note>"
        key = "note_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    memory.set(key, value)
    return f"Remembered: {key}"


def show_memory(memory: Memory) -> str:
    rows = memory.all()
    if not rows:
        return "No saved memory yet."
    return "\n".join(f"- {key}: {value}" for key, value in rows)


def refresh_dashboard_stats(memory: Memory) -> None:
    ensure_dirs()
    index: dict = {}
    if DASHBOARD_DATA.exists():
        try:
            index = json.loads(DASHBOARD_DATA.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            index = {}
    index["stats"] = memory.stats()
    index["updated_at"] = datetime.now().isoformat(timespec="seconds")
    index["system"] = "Drewskii.Engine / Lexi-9-Omega"
    write_json(DASHBOARD_DATA, index)


def list_project() -> str:
    files = [
        "lexi_project_manifest.json",
        "lexi_identity.json",
        "model_profiles/drewskii_engine.json",
        "model_profiles/lexi_phys.json",
        "docs/models/Drewskii_Engine.md",
        "docs/blocked_operation_ledger.md",
        "workspace/deliverables/",
        "workspace/lexi_dashboard.html",
        "workspace/dashboard_data.json",
        "memory/drewskii_memory.db",
        "android/termux_helpers.py",
    ]
    commands = [
        "model Drewskii.Engine",
        "plan <idea>",
        "forge <brand name>",
        "blueprint <name>",
        "documentary-map",
        "offer-map",
        "generate-ui",
        "termux",
        "stats",
        "evals",
    ]
    return (
        "Project files:\n"
        + "\n".join(f"- {item}" for item in files)
        + "\n\nCore commands:\n"
        + "\n".join(f"- {item}" for item in commands)
    )


def model_paths(name: str) -> tuple[Path, Path] | None:
    normalized = name.strip().lower().replace("_", ".").replace("-", ".")
    if not normalized or normalized in {"lexi", "lexi.phys"}:
        return MODEL_DOC_PATH, MODEL_PROFILE_PATH
    if normalized in {"drewskii", "drewskii.engine"}:
        return DREWSKII_MODEL_DOC_PATH, DREWSKII_MODEL_PROFILE_PATH
    if normalized in {"cortana", "cortana.phys", "cortanaphys"}:
        return CORTANA_MODEL_DOC_PATH, CORTANA_MODEL_PROFILE_PATH
    return None


def show_model_profile(name: str) -> str:
    paths = model_paths(name)
    if not paths:
        return "Unknown model profile. Available: Lexi.PHYS, Drewskii.Engine, CORTANA-PHYS"
    doc_path, profile_path = paths
    return (
        read_text_file(doc_path, "Model profile")
        + "\n\nProfile JSON:\n"
        + read_json_file(profile_path, "Model profile")
    )


def parse_forge_args(raw: str) -> dict[str, str]:
    """forge Name | vibe | audience | offer"""
    parts = [p.strip() for p in raw.split("|")]
    while len(parts) < 4:
        parts.append("")
    return {
        "name": parts[0] or "Custom AI Brand Blueprint Pack",
        "vibe": parts[1],
        "audience": parts[2],
        "offer": parts[3],
    }


def print_paths(paths: dict[str, str]) -> None:
    for key, value in paths.items():
        print(f"  {key}: {value}")


def main() -> None:
    os.chdir(PROJECT_ROOT)
    ensure_dirs()
    memory = Memory(PROJECT_ROOT / "memory" / "drewskii_memory.db")
    print(BANNER)

    while True:
        try:
            command = input("Drewskii.Engine > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nEngine offline.")
            break

        if not command:
            continue

        if is_blocked(command):
            reason = blocked_reason(command) or "safety boundary"
            print(
                f"Blocked ({reason}): that request crosses a safety line. "
                "I can redirect into a legal, permission-based, user-space build."
            )
            log_event(f"blocked_command: {reason}")
            continue

        if command == "help":
            print(HELP)

        elif command == "manifest":
            print(read_json_file(MANIFEST_PATH, "Manifest"))

        elif command == "identity":
            print(read_json_file(IDENTITY_PATH, "Identity"))

        elif command in {"model", "/model"} or command.startswith("model ") or command.startswith("/model "):
            model_name = command.split(" ", 1)[1].strip() if " " in command else "Drewskii.Engine"
            print(show_model_profile(model_name))

        elif command == "cortana" or command.startswith("cortana "):
            from brain.cortana_phys import CortanaPhysCore

            core = CortanaPhysCore()
            rest = command.removeprefix("cortana").strip()
            if not rest or rest == "status":
                print(json.dumps(core.status(), indent=2))
            elif rest == "mint" or rest.startswith("mint "):
                label = rest.removeprefix("mint").strip() or "cortana-local"
                print(json.dumps(core.mint_key(label=label), indent=2))
                log_event(f"cortana_key_minted label={label}")
            elif rest == "keys":
                print(json.dumps(core.list_keys(), indent=2))
            elif rest == "models":
                print(json.dumps(core.list_models(), indent=2))
            elif rest.startswith("invent "):
                # invent Name [| family | description]
                raw = rest.removeprefix("invent").strip()
                parts = [p.strip() for p in raw.split("|")]
                name = parts[0] if parts else "Custom Module"
                family = parts[1] if len(parts) > 1 and parts[1] else "custom"
                desc = parts[2] if len(parts) > 2 else ""
                spec = core.invent_model(name, family=family, description=desc)
                print(json.dumps(spec, indent=2))
                log_event(f"cortana_model_invented id={spec['model_id']}")
            elif rest.startswith("ask "):
                body = rest.removeprefix("ask").strip()
                model_id = None
                prompt = body
                if "|" in body:
                    left, right = body.split("|", 1)
                    # if left looks like a model id, treat as model|prompt
                    if left.strip().startswith("cortana-") or left.strip() in {
                        m["model_id"] for m in core.list_models()
                    }:
                        model_id = left.strip()
                        prompt = right.strip()
                resp = core.complete(prompt, model_id=model_id)
                print(resp["output"])
                print("\n---")
                print(json.dumps({k: v for k, v in resp.items() if k != "output"}, indent=2))
            else:
                print(
                    "Usage:\n"
                    "  cortana status\n"
                    "  cortana mint [label]\n"
                    "  cortana keys\n"
                    "  cortana models\n"
                    "  cortana invent <name> [| family | description]\n"
                    "  cortana ask <prompt>\n"
                    "  cortana ask <model_id> | <prompt>\n"
                )

        elif command == "skills":
            print(read_json_file(SKILLS_PATH, "Skills"))

        elif command == "prototype":
            print(read_text_file(PROTOTYPE_PATH, "Prototype path"))

        elif command == "documentary":
            print(read_text_file(DOCUMENTARY_PATH, "Documentary map"))

        elif command in {"documentary-map", "doc-map"}:
            result = export_documentary_map(memory=memory)
            refresh_dashboard_stats(memory)
            print("Documentary map exported:")
            print_paths(result["paths"])

        elif command in {"offer", "offer-map", "offers"}:
            result = export_offer_map(memory=memory)
            refresh_dashboard_stats(memory)
            print("Offer map exported:")
            print_paths(result["paths"])

        elif command == "top-layer":
            print(read_text_file(TOP_LAYER_PATH, "Top-layer documentary map"))

        elif command == "software":
            print(read_text_file(PROTOTYPE_PATH, "Software build path"))

        elif command.startswith("experimental ") or command.startswith("/experimental "):
            concept = command.split(" ", 1)[1].strip()
            try:
                result = create_experimental_concept(concept)
            except ValueError as exc:
                print(f"Experimental concept error: {exc}")
            else:
                print(json.dumps(result, indent=2, ensure_ascii=True))

        elif command == "experiments":
            print(json.dumps({"experiments": list_experimental_concepts()}, indent=2, ensure_ascii=True))

        elif command == "retro" or command.startswith("retro "):
            # retro [target_mass] [target_authority]  — simulation only
            from brain.retro_causal import RetroCausalEngine, CurrentParams

            parts = command.split()
            mass = float(parts[1]) if len(parts) > 1 else 16.8
            auth = float(parts[2]) if len(parts) > 2 else 0.97
            engine = RetroCausalEngine(consistency_threshold=0.08, max_iters=120)
            report = engine.execute_post_synthesis(
                target_mass=mass,
                target_authority=auth,
                current=CurrentParams(),
                write_artifacts=True,
            )
            print(report)
            log_event(f"retro_sim mass={mass} authority={auth}")

        elif command == "grav" or command.startswith("grav "):
            # grav [density] — simulation only
            from brain.gravitational_processor import GravitationalProcessor

            parts = command.split()
            density = float(parts[1]) if len(parts) > 1 else 16.5
            print(GravitationalProcessor().demo_report(density=density, write_artifacts=True))
            log_event(f"grav_sim density={density}")

        elif command == "kali" or command.startswith("kali "):
            # Constraint-pressure simulation — NOT offensive security / host attacks
            from brain.offensive_kali_layer import (
                Constraint,
                ConstraintType,
                OffensiveKaliLayer,
            )

            parts = command.split()
            density = float(parts[1]) if len(parts) > 1 else 16.5
            layer = OffensiveKaliLayer(base_aggression=0.93)
            constraints = [
                Constraint("export_control_review", ConstraintType.REGULATORY, 1.2),
                Constraint("thermal_limit", ConstraintType.PHYSICAL, 1.4),
                Constraint("alloy_yield", ConstraintType.MATERIAL, 1.0),
                Constraint("public_trust", ConstraintType.SOCIAL, 0.8),
                Constraint("launch_window", ConstraintType.TEMPORAL, 0.9),
            ]
            report = layer.full_assault(
                target_name="Lexi.PHYS Showcase Capsule",
                constraints=constraints,
                mass_density=density,
                social_pull=0.55,
                stakeholders={"ops": 0.4, "legal": 0.3, "community": 0.55},
                write_artifacts=True,
            )
            print(report.classification)
            print(f"status={report.status} overall_yield={report.overall_yield:.3f}")
            for v in report.vectors:
                c = v["constraint"]
                print(f"  {c['type']:12s} {c['name']:20s} {v['status']:10s} yield={v['yield_score']:.3f}")
            print("Blocked literal ops:")
            for b in report.blocked_operations:
                print(f"  - {b}")
            log_event(f"kali_constraint_sim density={density} status={report.status}")

        elif command == "mastermind" or command.startswith("mastermind "):
            from brain.mastermind_core import MastermindCore

            parts = command.split()
            mass = float(parts[1]) if len(parts) > 1 else 17.4
            auth = float(parts[2]) if len(parts) > 2 else 0.97
            name = " ".join(parts[3:]) if len(parts) > 3 else "Lexi-9-Omega Mastermind Cycle"
            core = MastermindCore(base_aggression=0.93)
            report = core.full_cycle(
                target_mass=mass,
                target_authority=auth,
                target_name=name,
                write_artifacts=True,
            )
            print(core.format_report(report))
            log_event(f"mastermind_cycle status={report.status} mass={mass} auth={auth}")

        elif command == "kinetic" or command.startswith("kinetic "):
            from brain.cognitive_kinetic import CognitiveKineticFlow, DEMO_PROFILES

            parts = command.split()
            profile = parts[1] if len(parts) > 1 else "anxious_arrival"
            if profile not in DEMO_PROFILES:
                print(f"Unknown profile. Available: {', '.join(DEMO_PROFILES)}")
            else:
                flow = CognitiveKineticFlow()
                report = flow.run(
                    profile=profile,
                    title=f"Cognitive→Kinetic · {profile}",
                    write_artifacts=True,
                )
                print(flow.format_report(report))
                log_event(f"cognitive_kinetic profile={profile} mode={report.kinetic['mode']}")

        elif command == "resonator" or command.startswith("resonator "):
            from brain.cognitive_kinetic import DEMO_PROFILES
            from brain.space_resonator import SpaceEmotionalResonator, SpaceArchetype

            parts = command.split()
            profile = parts[1] if len(parts) > 1 else "deep_focus"
            arch = parts[2] if len(parts) > 2 else "deep_work"
            if profile not in DEMO_PROFILES:
                print(f"Unknown profile. Available: {', '.join(DEMO_PROFILES)}")
            else:
                try:
                    SpaceArchetype(arch)
                except ValueError:
                    print(
                        "Unknown archetype. Available: "
                        + ", ".join(a.value for a in SpaceArchetype)
                    )
                else:
                    engine = SpaceEmotionalResonator()
                    report = engine.run(
                        profile=profile,
                        archetype=arch,
                        title=f"Resonator · {arch} · {profile}",
                        write_artifacts=True,
                    )
                    print(engine.format_report(report))
                    log_event(
                        f"space_resonator profile={profile} arch={arch} "
                        f"mode={report.envelope['resonance_mode']}"
                    )

        elif command == "manifold" or command.startswith("manifold "):
            from brain.cognitive_kinetic import DEMO_PROFILES
            from brain.kineto_cognitive_manifold import (
                KinetoCognitiveManifold,
                SocietalContext,
            )
            from brain.space_resonator import SpaceArchetype

            parts = command.split()
            profile = parts[1] if len(parts) > 1 else "deep_focus"
            arch = parts[2] if len(parts) > 2 else "deep_work"
            society = parts[3] if len(parts) > 3 else "solo_deep_work"
            if profile not in DEMO_PROFILES:
                print(f"Unknown profile. Available: {', '.join(DEMO_PROFILES)}")
            else:
                try:
                    SpaceArchetype(arch)
                    SocietalContext(society)
                except ValueError as exc:
                    print(
                        f"Bad archetype or society ({exc}).\n"
                        f"Archetypes: {', '.join(a.value for a in SpaceArchetype)}\n"
                        f"Society: {', '.join(s.value for s in SocietalContext)}"
                    )
                else:
                    engine = KinetoCognitiveManifold()
                    report = engine.full_flow(
                        profile=profile,
                        space_archetype=arch,
                        societal_context=society,
                        title=f"Manifold · {profile} · {arch} · {society}",
                        write_artifacts=True,
                    )
                    print(engine.format_report(report))
                    log_event(
                        f"manifold profile={profile} arch={arch} society={society} "
                        f"ar={report.ar['mode']} spatial={report.spatial['resonance_mode']}"
                    )

        elif command == "cocoon" or command.startswith("cocoon "):
            from brain.cocoon_transcendent import TranscendentCocoonV3

            parts = command.split()
            if len(parts) >= 1 and parts[0] == "cocoon" and len(parts) > 1 and parts[1] == "resonance":
                pass  # handled below as cocoon-resonance
            spin = float(parts[1]) if len(parts) > 1 else 0.62
            energize = float(parts[2]) if len(parts) > 2 else 0.85
            cocoon = TranscendentCocoonV3()
            result = cocoon.execute_post_synthesis(
                spin_rate=spin,
                energize=energize,
                write_artifacts=True,
            )
            print(
                cocoon._render_inverse_physics_report(
                    result["simulation"],
                    {"residual_to_target": result["retro"]["residual_to_target"]},
                    result["determination"],
                )
            )
            if result.get("artifact_paths"):
                print("\nArtifacts:")
                for k, v in result["artifact_paths"].items():
                    print(f"  {k}: {v}")
            log_event(
                f"cocoon_v3 status={result['determination']['status']} "
                f"aesthetic={result['simulation']['scores']['aesthetic_dominance']:.3f}"
            )

        elif command in {"cocoon-resonance", "cocoon resonance"}:
            from brain.cocoon_transcendent import TranscendentCocoonV3

            test = TranscendentCocoonV3().neural_resonance_test()
            print(json.dumps(test, indent=2))
            log_event("cocoon_neural_resonance_test")

        elif command == "autonomy" or command.startswith("autonomy "):
            from brain.autonomy_os import AutonomyOS

            parts = command.split()
            seconds = float(parts[1]) if len(parts) > 1 else 2.0
            max_ticks = int(parts[2]) if len(parts) > 2 else 250
            aos = AutonomyOS(hz=50.0, max_ticks=max_ticks)
            print("Starting Autonomy OS (simulation)...")
            summary = aos.run_for(seconds=seconds)
            print(json.dumps(summary, indent=2))
            print("\n--- Event Log (last 8) ---")
            for event in aos.replay_log()[-8:]:
                print(event)
            log_event(
                f"autonomy_os ticks={summary.get('ticks')} "
                f"safe={summary.get('safe')} reason={summary.get('stop_reason')}"
            )

        elif command == "stack" or command.startswith("stack "):
            from brain.intelligence_stack import BrandIntake, LocalFirstIntelligenceStack

            stack = LocalFirstIntelligenceStack(memory=memory)
            rest = command.removeprefix("stack").strip()
            if not rest or rest in {"status", "rules"}:
                print(json.dumps(stack.operating_rules(), indent=2))
            elif rest == "run" or rest.startswith("run "):
                brand = rest.removeprefix("run").strip() or "Lexi Local-First Intelligence"
                print("Running Stage-1 full automation pipeline...")
                result = stack.full_stage1_run(brand_name=brand, mint_key=True)
                # redact key for console (still shown truncated)
                if "cortana_key" in result.get("steps", {}):
                    once = result["steps"]["cortana_key"].pop("api_key_once", None)
                    if once:
                        print(f"\n[one-time API key — store now]\n{once}\n")
                print(json.dumps(result, indent=2, default=str))
            elif rest.startswith("brand ") or rest.startswith("pack "):
                raw = rest.split(" ", 1)[1].strip() if " " in rest else ""
                parts = [p.strip() for p in raw.split("|")]
                while len(parts) < 4:
                    parts.append("")
                intake = BrandIntake(
                    name=parts[0] or "Custom AI Brand Blueprint Pack",
                    vibe=parts[1] or "dark, clean, futuristic",
                    audience=parts[2] or "creators and small businesses",
                    offer=parts[3] or "identity pack starting at $50",
                )
                try:
                    out = stack.brand_pack(intake)
                except ValueError as exc:
                    print(f"Intake error: {exc}")
                else:
                    print(json.dumps({
                        "brand_name": out["pack"]["data"].get("brand_name"),
                        "quality_checklist": out["quality_checklist"],
                        "zip": out.get("zip"),
                        "delivery": out.get("delivery"),
                        "paths": out["pack"]["paths"],
                        "promotion_ready_checklist": out["promotion_ready"],
                    }, indent=2))
                    if out.get("zip"):
                        print(f"\nCustomer ZIP ready: {out['zip']}")
            elif rest.startswith("promote "):
                feature = rest.removeprefix("promote").strip() or "brand_pack"
                # empty evidence shows what's missing
                print(json.dumps(stack.promotion_review(feature), indent=2))
            else:
                print(
                    "Usage:\n"
                    "  stack\n"
                    "  stack run [brand name]\n"
                    "  stack brand <name> | <vibe> | <audience> | <offer>\n"
                    "  stack pack  <name> | <vibe> | <audience> | <offer>\n"
                    "  stack rules\n"
                    "  stack promote <feature>\n"
                )

        elif command == "blueprint" or command.startswith("blueprint "):
            name = command.removeprefix("blueprint").strip() or "Custom AI Brand Blueprint Pack"
            result = generate_brand_blueprint(name, memory=memory)
            refresh_dashboard_stats(memory)
            log_evaluation(
                memory,
                category="template",
                subject=f"blueprint:{result['data']['brand_name']}",
                notes="Quick brand blueprint pack generated",
                score=0.85,
                payload={"paths": result["paths"]},
            )
            print(f"Generated blueprint: {result['title']}")
            print_paths(result["paths"])

        elif command == "forge" or command.startswith("forge "):
            raw = command.removeprefix("forge").strip()
            args = parse_forge_args(raw)
            result = forge_blueprint(
                args["name"],
                vibe=args["vibe"],
                audience=args["audience"],
                offer=args["offer"],
                include_code=True,
                memory=memory,
            )
            refresh_dashboard_stats(memory)
            print(f"Blueprint Forge complete: {result['brand_name']}")
            print_paths(result["paths"])

        elif command == "roadmap":
            print(roadmap())

        elif command.startswith("plan "):
            idea = command[5:].strip()
            result = save_plan(memory, idea)
            refresh_dashboard_stats(memory)
            log_evaluation(
                memory,
                category="plan",
                subject=idea[:80],
                notes="Prototype plan saved",
                score=0.8,
                payload={"plan_id": result["plan_id"], "paths": result["paths"]},
            )
            print(result["text"])
            print("\nSaved plan artifacts:")
            print_paths(result["paths"])

        elif command.startswith("remember "):
            data = command[9:].strip()
            print(remember(memory, data))

        elif command.startswith("recall "):
            key = command[7:].strip()
            value = memory.get(key)
            print(value if value else "No memory found for that key.")

        elif command == "memory":
            print(show_memory(memory))

        elif command == "stats":
            refresh_dashboard_stats(memory)
            print(json.dumps(memory.stats(), indent=2))

        elif command == "deliverables":
            print(json.dumps(memory.recent_deliverables(15), indent=2, ensure_ascii=True))

        elif command == "evals":
            print(json.dumps(memory.recent_evals(15), indent=2, ensure_ascii=True))

        elif command.startswith("eval "):
            # eval category | subject | notes [| score]
            raw = command[5:].strip()
            parts = [p.strip() for p in raw.split("|")]
            if len(parts) < 3:
                print("Usage: eval <category> | <subject> | <notes> [| score]")
            else:
                score = float(parts[3]) if len(parts) > 3 and parts[3] else None
                record = log_evaluation(
                    memory,
                    category=parts[0],
                    subject=parts[1],
                    notes=parts[2],
                    score=score,
                )
                refresh_dashboard_stats(memory)
                print(json.dumps(record, indent=2, ensure_ascii=True))

        elif command == "list":
            print(list_project())

        elif command.startswith("log "):
            note = command[4:].strip()
            log_event(note)
            print("Logged.")

        elif command == "generate-ui":
            path = generate_ui_shell()
            refresh_dashboard_stats(memory)
            print(f"Generated: {path}")
            print(f"Dashboard data: {DASHBOARD_DATA}")

        elif command == "termux":
            print(helpers_markdown())

        elif command.startswith("termux "):
            rest = command[7:].strip()
            approved = False
            if rest.endswith("--yes"):
                approved = True
                rest = rest[: -len("--yes")].strip()
            helper_id = rest.split()[0] if rest else ""
            if not helper_id:
                print("Usage: termux <id> [--yes]")
                print("IDs:", ", ".join(h["id"] for h in list_helpers()))
            elif not approved:
                print(
                    f"Review required for helper '{helper_id}'.\n"
                    f"Re-run: termux {helper_id} --yes\n"
                    "This only writes a Termux script draft; it does not execute on a phone."
                )
                try:
                    # show command without writing
                    from android.termux_helpers import APPROVED_HELPERS

                    h = APPROVED_HELPERS.get(helper_id.lower())
                    if h:
                        print(f"Command preview: {h['command']}")
                    else:
                        print("Unknown helper id.")
                except Exception as exc:
                    print(exc)
            else:
                try:
                    meta = prepare_helper(helper_id, approved=True)
                except (ValueError, PermissionError) as exc:
                    print(f"Termux helper error: {exc}")
                else:
                    log_event(f"termux_helper_prepared:{helper_id}")
                    print(json.dumps(meta, indent=2, ensure_ascii=True))

        elif command in {"exit", "quit"}:
            print("Engine offline.")
            break

        else:
            print("Unknown command. Type 'help'.")


if __name__ == "__main__":
    main()
