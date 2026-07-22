#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from brain.memory import (
    recent_autonomous_runs,
    recent_memories,
    save_autonomous_run,
    search_indexed_files,
    upsert_project_files,
)

ROOT = Path(__file__).resolve().parent.parent
ELITE_PROFILE_PATH = ROOT / "lexi_app" / "profiles" / "lexi_phys_elite.json"

try:
    from .lexi_backend import BigDaddyDrewBackendError, OllamaBigDaddyDrewClient
    from .project_monitor import ProjectMonitor
    from .project_scanner import ProjectScanner
except ImportError:
    from lexi_backend import BigDaddyDrewBackendError, OllamaBigDaddyDrewClient
    from project_monitor import ProjectMonitor
    from project_scanner import ProjectScanner


@dataclass
class AutonomousRun:
    goal: str
    mode: str = "auto"
    autonomy: str = "supervised"
    max_files: int = 250
    roots: Optional[Iterable[str]] = None


@dataclass
class BlueprintBuildRequest:
    idea: str
    depth: str = "prototype"
    write_artifacts: bool = True
    use_model_notes: bool = False
    max_files: int = 200
    roots: Optional[Iterable[str]] = None
    artifact_root: Optional[str] = None


@dataclass
class CashSystemRequest:
    idea: str
    market: str = "creators, builders, and small businesses"
    offer_type: str = "content-product-service"
    speed: str = "minutes"
    write_artifacts: bool = True
    use_model_notes: bool = False
    max_files: int = 200
    roots: Optional[Iterable[str]] = None
    artifact_root: Optional[str] = None


class LexiAutonomousCore:
    """Local-first creative engineering intelligence core for Lexi.AI.

    The core positions Lexi.AI as part AI companion, part invention lab, and
    part futuristic blueprint generator. It deliberately separates thinking and
    safe local discovery from risky actions. It can plan, index, and prepare
    work immediately. File writes, shell commands, network calls, purchases,
    account changes, and secrets stay behind explicit operator approval.
    """

    def __init__(self, llm_client: Optional[OllamaBigDaddyDrewClient] = None) -> None:
        self.llm_client = llm_client

    @classmethod
    def from_disk(cls) -> "LexiAutonomousCore":
        try:
            return cls(OllamaBigDaddyDrewClient.from_disk())
        except Exception:
            return cls(None)

    def elite_profile(self) -> Dict[str, Any]:
        try:
            return json.loads(ELITE_PROFILE_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {
                "id": "lexi_phys_elite",
                "name": "Lexi.PHYS Elite",
                "summary": (
                    "A local design-and-reasoning system for geometry, architecture, "
                    "reverse engineering, blueprint documentation, and controlled code generation."
                ),
                "safe_operating_interpretation": {
                    "treat_as": [
                        "local design intelligence",
                        "structured reverse-engineering assistant",
                        "architectural reasoning engine",
                    ],
                    "not_as": [
                        "hidden implant",
                        "device exploit platform",
                        "unsupervised unrestricted agent",
                    ],
                },
            }

    def capabilities(self) -> List[dict]:
        return [
            {
                "name": "lexi_phys_elite_profile",
                "description": "Defines Lexi.PHYS as a geometry-first, reverse-engineering, physics-inspired blueprint intelligence with approval gates.",
                "risk": "identity plus planning",
            },
            {
                "name": "local_project_scan",
                "description": "Indexes Lexi.AI, configured workspaces, ChatGPT exports, and common Mac work folders.",
                "risk": "read-only",
            },
            {
                "name": "structural_foresight",
                "description": "Maps load paths, stress responses, pre-failure signals, and geometric failure modes for concept and inspection work.",
                "risk": "planning",
            },
            {
                "name": "reverse_engineering_analyst",
                "description": "Reconstructs components, interfaces, workflows, failure modes, and verification plans from fragments.",
                "risk": "planning",
            },
            {
                "name": "invention_lab",
                "description": "Turns rough ideas into concept briefs, constraints, prototype paths, and buildable experiments.",
                "risk": "planning",
            },
            {
                "name": "blueprint_generator",
                "description": "Turns ideas into saved blueprint artifacts, component specs, prototype sprints, and validation plans.",
                "risk": "planning plus local-write",
            },
            {
                "name": "simulation_planner",
                "description": "Frames digital twins, field visualizations, node maps, interpolation logic, and conceptual multiphysics validation plans.",
                "risk": "planning",
            },
            {
                "name": "interface_architect",
                "description": "Designs dashboards, command centers, mobile controls, browser surfaces, and system maps for technical workflows.",
                "risk": "planning",
            },
            {
                "name": "model_workbench",
                "description": "Turns model ideas into dataset, training, eval, deployment, and cost plans.",
                "risk": "planning",
            },
            {
                "name": "ai_company_operator",
                "description": "Builds offer, product, sales, delivery, support, and weekly operating plans.",
                "risk": "planning",
            },
            {
                "name": "cash_system",
                "description": "Turns an idea into content hooks, productized offers, service packages, launch assets, and a validation queue.",
                "risk": "planning plus local-write",
            },
            {
                "name": "engineering_copilot",
                "description": "Finds relevant files, proposes implementation steps, and records creative engineering run history.",
                "risk": "approval-gated",
            },
            {
                "name": "long_term_memory",
                "description": "Stores chat memory, project inventory, invention goals, plans, and outcomes in SQLite.",
                "risk": "local-write",
            },
            {
                "name": "project_monitor",
                "description": "Snapshots selected project roots, detects meaningful file changes, and stores check-ins.",
                "risk": "read-only plus local-write",
            },
        ]

    def scan_projects(
        self,
        roots: Optional[Iterable[str]] = None,
        max_files: int = 500,
        query: str = "",
    ) -> Dict[str, Any]:
        scanner = ProjectScanner.from_config(roots=roots, max_files=max_files)
        records = scanner.search(query, limit=max_files) if query else scanner.scan()
        upsert_project_files(records)
        return {
            "roots": [str(root) for root in scanner.roots],
            "indexed_count": len(records),
            "files": records[:100],
        }

    def monitor_projects(
        self,
        roots: Optional[Iterable[str]] = None,
        max_files: int = 500,
        query: str = "",
    ) -> Dict[str, Any]:
        monitor = ProjectMonitor(roots=roots, max_files=max_files, query=query)
        return monitor.check_in()

    def run(self, request: AutonomousRun) -> Dict[str, Any]:
        goal = request.goal.strip()
        if not goal:
            raise ValueError("Autonomous goal cannot be empty.")

        mode = self.determine_mode(goal, request.mode)
        context = self.scan_projects(
            roots=request.roots,
            max_files=request.max_files,
            query="",
        )
        indexed_matches = search_indexed_files(self._context_query(goal), limit=20)
        if not indexed_matches:
            indexed_matches = context["files"][:20]
        memories = [
            {"user_input": row[0], "lexi_response": row[1], "created_at": row[2]}
            for row in recent_memories(limit=5)
        ]

        plan = self._build_plan(goal, mode, request.autonomy, indexed_matches)
        result = {
            "summary": self._summary(goal, mode),
            "context": {
                "scan_roots": context["roots"],
                "indexed_count": context["indexed_count"],
                "relevant_files": indexed_matches[:12],
                "recent_memories": memories,
            },
            "model_workbench": self._model_workbench(goal),
            "business_os": self._business_os(goal),
            "cash_system_os": self._cash_system_os(goal),
            "next_actions": self._next_actions(mode),
            "approval_gates": self._approval_gates(),
            "llm_notes": self._llm_notes(goal, mode, indexed_matches[:8]),
        }

        run_id = save_autonomous_run(
            goal=goal,
            mode=mode,
            autonomy=request.autonomy,
            status="planned",
            plan=plan,
            result=result,
        )
        result["run_id"] = run_id

        return {
            "run_id": run_id,
            "goal": goal,
            "mode": mode,
            "autonomy": request.autonomy,
            "status": "planned",
            "plan": plan,
            "result": result,
        }

    def generate_blueprint(self, request: BlueprintBuildRequest) -> Dict[str, Any]:
        idea = request.idea.strip()
        if not idea:
            raise ValueError("Blueprint idea cannot be empty.")

        context = self.scan_projects(
            roots=request.roots,
            max_files=request.max_files,
            query="",
        )
        files = search_indexed_files(self._context_query(idea), limit=12)
        if not files:
            files = context["files"][:12]
        memories = [
            {"user_input": row[0], "lexi_response": row[1], "created_at": row[2]}
            for row in recent_memories(limit=5)
        ]

        blueprint = self._blueprint_spec(idea, request.depth, files, memories)
        result = {
            "summary": (
                "Lexi.AI converted the idea into a blueprint with a component map, "
                "prototype automation path, validation checks, and next build actions."
            ),
            "context": {
                "scan_roots": context["roots"],
                "indexed_count": context["indexed_count"],
                "relevant_files": files[:8],
                "recent_memories": memories,
            },
            "blueprint": blueprint,
            "artifacts": {},
            "approval_gates": self._approval_gates(),
            "llm_notes": (
                self._blueprint_llm_notes(idea, blueprint, files[:6])
                if request.use_model_notes
                else "Model enrichment was skipped; deterministic blueprint automation was used."
            ),
        }

        if request.write_artifacts:
            result["artifacts"] = self._write_blueprint_artifacts(
                blueprint=blueprint,
                artifact_root=request.artifact_root,
            )

        run_id = save_autonomous_run(
            goal=f"Blueprint: {idea}",
            mode="blueprint-builder",
            autonomy="supervised",
            status="blueprinted",
            plan={
                "goal": idea,
                "mode": "blueprint-builder",
                "steps": [item["action"] for item in blueprint["build_queue"]],
                "deliverables": [item["name"] for item in blueprint["artifact_plan"]],
            },
            result=result,
        )
        result["run_id"] = run_id

        return {
            "run_id": run_id,
            "status": "blueprinted",
            "idea": idea,
            "depth": request.depth,
            "result": result,
        }

    def generate_cash_system(self, request: CashSystemRequest) -> Dict[str, Any]:
        idea = request.idea.strip()
        if not idea:
            raise ValueError("Cash System idea cannot be empty.")

        context = self.scan_projects(
            roots=request.roots,
            max_files=request.max_files,
            query="",
        )
        files = search_indexed_files(self._context_query(idea), limit=12)
        if not files:
            files = context["files"][:12]
        memories = [
            {"user_input": row[0], "lexi_response": row[1], "created_at": row[2]}
            for row in recent_memories(limit=5)
        ]

        cash_system = self._cash_system_spec(
            idea=idea,
            market=request.market.strip() or "creators, builders, and small businesses",
            offer_type=request.offer_type.strip() or "content-product-service",
            speed=request.speed.strip() or "minutes",
            files=files,
            memories=memories,
        )
        result = {
            "summary": (
                "Lexi.AI packaged the idea into a Cash System with content hooks, "
                "product ideas, service offers, launch assets, fulfillment steps, "
                "and validation checks."
            ),
            "context": {
                "scan_roots": context["roots"],
                "indexed_count": context["indexed_count"],
                "relevant_files": files[:8],
                "recent_memories": memories,
            },
            "cash_system": cash_system,
            "artifacts": {},
            "approval_gates": self._approval_gates(),
            "llm_notes": (
                self._cash_system_llm_notes(idea, cash_system, files[:6])
                if request.use_model_notes
                else "Model enrichment was skipped; deterministic Cash System automation was used."
            ),
        }

        if request.write_artifacts:
            result["artifacts"] = self._write_cash_system_artifacts(
                cash_system=cash_system,
                artifact_root=request.artifact_root,
            )

        run_id = save_autonomous_run(
            goal=f"Cash System: {idea}",
            mode="cash-system",
            autonomy="supervised",
            status="packaged",
            plan={
                "goal": idea,
                "mode": "cash-system",
                "steps": [item["action"] for item in cash_system["build_queue"]],
                "deliverables": [item["name"] for item in cash_system["artifact_plan"]],
            },
            result=result,
        )
        result["run_id"] = run_id

        return {
            "run_id": run_id,
            "status": "packaged",
            "idea": idea,
            "market": request.market,
            "offer_type": request.offer_type,
            "result": result,
        }

    def recent_runs(self, limit: int = 10) -> List[dict]:
        return recent_autonomous_runs(limit=limit)

    def recent_monitor_checkins(self, limit: int = 10) -> List[dict]:
        return ProjectMonitor.recent_checkins(limit=limit)

    def determine_mode(self, goal: str, requested_mode: str = "auto") -> str:
        if requested_mode and requested_mode != "auto":
            return requested_mode

        text = goal.lower()
        model_terms = {"model", "fine-tune", "finetune", "train", "dataset", "eval", "ollama", "llama", "agent"}
        business_terms = {"business", "company", "customer", "sales", "offer", "revenue", "marketing", "product"}
        cash_terms = {"cash", "money", "monetize", "monetization", "income", "content", "service", "services", "sell", "launch"}
        engineering_terms = {"code", "app", "api", "repo", "bug", "build", "deploy", "website", "software", "engineer", "engineering"}
        creative_terms = {"creative", "invention", "invent", "blueprint", "prototype", "concept", "platform", "lab"}

        has_model = any(term in text for term in model_terms)
        has_business = any(term in text for term in business_terms)
        has_cash = any(term in text for term in cash_terms)
        has_engineering = any(term in text for term in engineering_terms)
        has_creative = any(term in text for term in creative_terms)

        if has_cash:
            return "cash-system"
        if has_model and has_business:
            return "company-builder"
        if has_creative and has_engineering:
            return "creative-engineering"
        if has_model:
            return "model-builder"
        if has_business:
            return "business-operator"
        if has_creative:
            return "invention-lab"
        if has_engineering:
            return "engineering"
        return "operator"

    def _context_query(self, goal: str) -> str:
        words = [word.strip(".,:;!?()[]{}").lower() for word in goal.split()]
        keep = [
            word
            for word in words
            if len(word) > 3
            and word
            not in {"with", "from", "that", "this", "everything", "other", "help"}
        ]
        return " ".join(keep[:6]) or goal

    def _build_plan(self, goal: str, mode: str, autonomy: str, files: List[dict]) -> Dict[str, Any]:
        steps = [
            "Ingest and index relevant Lexi.AI files, ChatGPT exports, and configured Mac folders.",
            "Frame the goal as a companion brief, invention-lab experiment, and blueprint-ready system.",
            "Turn the goal into measurable outcomes, constraints, owners, and approval gates.",
            "Extract reusable assets: prompts, code, datasets, product ideas, sales notes, and model configs.",
            "Create a build plan with smallest useful prototype, eval criteria, and deployment path.",
            "Create an AI-company operating plan covering offer, customer pipeline, delivery, support, and metrics.",
            "Run only read-only or pre-approved actions automatically; queue risky actions for approval.",
        ]
        if mode == "model-builder":
            steps.insert(3, "Choose base model, data strategy, evaluation harness, and packaging target.")
        elif mode == "business-operator":
            steps.insert(3, "Define target customer, urgent pain, paid offer, distribution channel, and proof assets.")
        elif mode == "cash-system":
            steps.insert(3, "Package the idea into content hooks, paid products, productized services, launch copy, and validation metrics.")
        elif mode == "engineering":
            steps.insert(3, "Map relevant source files, interfaces, test commands, and implementation order.")
        elif mode in {"creative-engineering", "invention-lab"}:
            steps.insert(3, "Define concept promise, technical feasibility, prototype surface, and validation experiment.")

        return {
            "goal": goal,
            "mode": mode,
            "autonomy": autonomy,
            "steps": steps,
            "relevant_file_count": len(files),
            "deliverables": [
                "project inventory",
                "goal brief",
                "invention brief",
                "futuristic blueprint spec",
                "prototype roadmap",
                "model build spec",
                "business operating plan",
                "cash system offer pack",
                "next-action queue",
            ],
        }

    def _summary(self, goal: str, mode: str) -> str:
        return (
            f"Lexi.AI created a {mode} run for: {goal}. "
            "This run is planned and stored locally as a companion brief, invention plan, and blueprint path; execution stays approval-gated."
        )

    def _model_workbench(self, goal: str) -> Dict[str, Any]:
        return {
            "objective": goal,
            "recommended_sequence": [
                "Collect examples from local projects, ChatGPT exports, docs, and chat logs.",
                "Separate companion behavior, invention-lab workflows, and blueprint-generation tasks into distinct examples.",
                "Split data into training, validation, and holdout eval sets before any tuning.",
                "Start with prompt/RAG improvements before fine-tuning; fine-tune only when examples repeat.",
                "Evaluate with task-specific checks: accuracy, refusal boundaries, latency, cost, and user usefulness.",
                "Package the best model path for Ollama, llama.cpp, API deployment, or a hosted app.",
            ],
            "artifacts_to_create": [
                "data/source_manifest.jsonl",
                "data/training_examples.jsonl",
                "evals/cases.jsonl",
                "docs/model_card.md",
                "docs/deployment_runbook.md",
            ],
        }

    def _business_os(self, goal: str) -> Dict[str, Any]:
        return {
            "mission": "Position Lexi.AI as a creative engineering intelligence platform that helps Drew convert ideas into prototypes, blueprints, offers, and shipped systems.",
            "operating_loops": [
                "Daily: capture leads, tasks, invention ideas, project context, and customer signals into Lexi memory.",
                "Weekly: ship one demo, publish one blueprint or proof asset, and review pipeline plus product metrics.",
                "Monthly: package repeatable services into offers, templates, automations, or model products.",
            ],
            "core_assets": [
                "customer problem library",
                "invention backlog",
                "blueprint gallery",
                "demo gallery",
                "prompt and agent library",
                "model evaluation harness",
                "delivery checklist",
                "sales follow-up queue",
            ],
            "first_offers": [
                "Creative engineering blueprint sprint",
                "Local AI companion setup for builders and small teams",
                "Custom invention-lab workflow automation",
                "Private model and knowledge-base buildout",
                "AI readiness audit with prototype roadmap",
            ],
        }

    def _cash_system_os(self, goal: str) -> Dict[str, Any]:
        return {
            "mission": f"Turn '{goal}' into fast testable revenue assets without promising guaranteed income.",
            "cash_loops": [
                "Content loop: publish proof, teach the transformation, invite replies, and capture objections.",
                "Product loop: package repeated answers into templates, prompts, blueprints, checklists, or mini-tools.",
                "Service loop: sell a productized sprint, deliver with a checklist, then turn each delivery into proof assets.",
            ],
            "core_assets": [
                "content hook library",
                "one-page offer",
                "product shelf",
                "service menu",
                "delivery checklist",
                "objection and FAQ bank",
                "launch metrics sheet",
            ],
            "guardrails": [
                "Do not imply guaranteed earnings.",
                "Validate demand before building a large product.",
                "Keep fulfillment scoped enough to deliver in one focused sprint.",
                "Track replies, booked calls, checkout clicks, and paid conversions separately.",
            ],
        }

    def _next_actions(self, mode: str) -> List[str]:
        base = [
            "Add ChatGPT export files to chat_logs/ or configure their folder in lexi_app/config.json.",
            "Run a project scan and review the top indexed files.",
            "Pick one visible platform demo that proves companion memory, invention planning, or blueprint generation.",
        ]
        if mode in {"creative-engineering", "invention-lab"}:
            base.append("Create a one-page blueprint for the first invention-lab demo, including constraints and validation checks.")
        if mode in {"company-builder", "model-builder"}:
            base.append("Create a 20-case eval set before changing model weights or prompts.")
        if mode in {"company-builder", "business-operator"}:
            base.append("Write a one-page offer and test it with five real prospects.")
        if mode == "cash-system":
            base.append("Generate one Cash System pack, publish three proof posts, and test one productized service with five real prospects.")
        return base

    def _blueprint_spec(
        self,
        idea: str,
        depth: str,
        files: List[dict],
        memories: List[dict],
    ) -> Dict[str, Any]:
        title = self._title_from_idea(idea)
        context_paths = [item.get("path", "") for item in files[:5] if item.get("path")]
        memory_signal = memories[0]["user_input"] if memories else "No recent memory signal yet."

        return {
            "title": title,
            "idea": idea,
            "depth": depth,
            "mission": f"Bring '{title}' to life as a testable product, prototype, or operating system.",
            "companion_brief": {
                "user_outcome": "A working blueprint that turns the idea into concrete decisions, screens, systems, and next actions.",
                "conversation_role": "Ask only for missing critical constraints; otherwise make safe assumptions and keep the build moving.",
                "memory_signal": memory_signal,
            },
            "invention_brief": {
                "promise": f"Convert the raw idea into a buildable {depth} with visible proof of progress.",
                "core_loop": [
                    "Capture the idea and target user.",
                    "Break it into system layers and component responsibilities.",
                    "Generate artifacts that a builder can implement immediately.",
                    "Validate the prototype against clear acceptance checks.",
                ],
                "non_goals": [
                    "Do not claim physics, hardware, or integrations are real before validation.",
                    "Do not spend money, publish data, or modify external services without approval.",
                ],
            },
            "system_layers": [
                {
                    "name": "Command surface",
                    "purpose": "Collect the idea, constraints, desired output, and target build depth.",
                    "inputs": ["idea text", "depth", "constraints", "local project context"],
                    "outputs": ["normalized brief", "build mode", "artifact plan"],
                },
                {
                    "name": "Blueprint engine",
                    "purpose": "Transform the idea into layers, components, dependencies, and validation checks.",
                    "inputs": ["normalized brief", "indexed files", "recent memory"],
                    "outputs": ["component specs", "prototype sprints", "risk register"],
                },
                {
                    "name": "Artifact forge",
                    "purpose": "Create local markdown and JSON artifacts that can be iterated into code, docs, or designs.",
                    "inputs": ["blueprint object", "workspace path"],
                    "outputs": ["blueprint markdown", "blueprint JSON", "next-action queue"],
                },
                {
                    "name": "Validation loop",
                    "purpose": "Keep futuristic ideas grounded by checking feasibility, safety, and proof criteria.",
                    "inputs": ["prototype", "acceptance checks", "risks"],
                    "outputs": ["pass/fail notes", "iteration plan", "approval gates"],
                },
            ],
            "component_specs": [
                {
                    "component": "Idea intake",
                    "build": "Textarea or command endpoint that accepts rough ideas and optional constraints.",
                    "done_when": "A user can submit an idea and receive a structured brief without manual prompting.",
                },
                {
                    "component": "Blueprint renderer",
                    "build": "Readable UI sections for layers, components, sprints, risks, and validation checks.",
                    "done_when": "The blueprint can be scanned in under one minute and used as a build plan.",
                },
                {
                    "component": "Artifact writer",
                    "build": "Local artifact generation under workspace/blueprints with markdown and JSON outputs.",
                    "done_when": "Every blueprint run returns paths to saved artifacts.",
                },
                {
                    "component": "Build queue",
                    "build": "A ranked task list that starts with the smallest visible prototype.",
                    "done_when": "The first task can be started immediately without re-planning.",
                },
            ],
            "automation_ladder": [
                {"stage": "Capture", "action": "Normalize the raw idea into a companion brief."},
                {"stage": "Structure", "action": "Generate system layers, component specs, and dependencies."},
                {"stage": "Materialize", "action": "Save blueprint artifacts and expose them in the dashboard."},
                {"stage": "Prototype", "action": "Build the smallest visible working slice."},
                {"stage": "Validate", "action": "Run feasibility, safety, UX, and usefulness checks before expansion."},
            ],
            "prototype_sprints": [
                {
                    "window": "First 2 hours",
                    "outcome": "A saved blueprint and visible dashboard result.",
                    "tasks": [
                        "Submit the idea through the dashboard blueprint builder.",
                        "Review generated component specs and remove anything unsafe or vague.",
                        "Choose the first visible prototype surface.",
                    ],
                },
                {
                    "window": "First 48 hours",
                    "outcome": "Clickable or runnable prototype slice.",
                    "tasks": [
                        "Implement the command surface.",
                        "Render the blueprint sections from JSON.",
                        "Save and reload blueprint artifacts from local workspace storage.",
                    ],
                },
                {
                    "window": "First 7 days",
                    "outcome": "Repeatable invention-lab workflow.",
                    "tasks": [
                        "Add templates for app, hardware, automation, and research ideas.",
                        "Create a gallery of saved blueprints.",
                        "Add validation notes after each prototype pass.",
                    ],
                },
            ],
            "artifact_plan": [
                {
                    "name": "blueprint.md",
                    "purpose": "Human-readable invention blueprint and build plan.",
                },
                {
                    "name": "blueprint.json",
                    "purpose": "Structured source of truth for UI rendering and later automation.",
                },
                {
                    "name": "prototype-backlog",
                    "purpose": "Ranked implementation queue for turning the idea into a working surface.",
                },
            ],
            "validation_checks": [
                "The blueprint names a user outcome, not just a vibe.",
                "Every system layer has inputs and outputs.",
                "The first prototype can be built without external accounts or paid APIs.",
                "Risky actions are explicit approval gates.",
                "The saved artifacts can be reopened and used as implementation context.",
            ],
            "risk_register": [
                {
                    "risk": "The idea stays inspirational but not buildable.",
                    "countermeasure": "Force each section to include a done-when condition and first build task.",
                },
                {
                    "risk": "The automation overclaims feasibility.",
                    "countermeasure": "Label speculative pieces and require validation before calling them real.",
                },
                {
                    "risk": "The user has to manually translate the output into work.",
                    "countermeasure": "Return a build queue and save artifacts to the workspace.",
                },
            ],
            "build_queue": [
                {"rank": 1, "action": "Open the saved markdown blueprint and choose the first visible prototype slice."},
                {"rank": 2, "action": "Create or update the UI/API route needed for that slice."},
                {"rank": 3, "action": "Add one validation check that proves the slice is useful."},
                {"rank": 4, "action": "Capture what changed in memory and queue the next slice."},
            ],
            "context_paths": context_paths,
        }

    def _cash_system_spec(
        self,
        idea: str,
        market: str,
        offer_type: str,
        speed: str,
        files: List[dict],
        memories: List[dict],
    ) -> Dict[str, Any]:
        raw_title = self._cash_title_from_idea(idea)
        title = f"Cash System: {raw_title}"
        context_paths = [item.get("path", "") for item in files[:5] if item.get("path")]
        memory_signal = memories[0]["user_input"] if memories else "No recent memory signal yet."

        return {
            "title": title,
            "idea": idea,
            "market": market,
            "offer_type": offer_type,
            "speed": speed,
            "mission": (
                f"Turn '{raw_title}' into a fast monetization engine that creates content, "
                "products, and productized services from one clear customer problem."
            ),
            "positioning": {
                "promise": f"Create sellable {offer_type} assets in {speed}, then validate them with real buyer signals.",
                "target_customer": market,
                "urgent_problem": "People have ideas, skills, and notes but need a fast path from raw thinking to a paid offer.",
                "safe_claim": "Lexi.AI speeds up packaging, content creation, and offer validation; it does not guarantee revenue.",
                "memory_signal": memory_signal,
            },
            "money_rules": [
                "Sell a useful outcome, not vague access to AI.",
                "Start with a productized service before building a big product.",
                "Use content to surface buyer pain and objections before scaling.",
                "Keep every offer small enough to deliver with a repeatable checklist.",
                "Measure replies, calls, checkout clicks, and paid conversions separately.",
            ],
            "cash_ladder": [
                {"stage": "Signal", "action": "Turn the idea into hooks that test pain, desire, and urgency."},
                {"stage": "Offer", "action": "Package one paid promise with a clear deliverable and fast delivery window."},
                {"stage": "Product", "action": "Convert repeated delivery assets into a template, prompt pack, checklist, or mini-tool."},
                {"stage": "Service", "action": "Sell a focused sprint that uses Lexi.AI to deliver the outcome for a client."},
                {"stage": "Systemize", "action": "Save proof, objections, and delivery steps back into Lexi.AI memory."},
            ],
            "content_engine": {
                "channels": ["short video", "carousel", "email", "DM follow-up", "offer page"],
                "hooks": [
                    {
                        "format": "pain callout",
                        "hook": f"You do not need more ideas. You need a system that turns {raw_title} into something people can buy.",
                        "cta": "Reply CASH and I will show you the first offer stack.",
                    },
                    {
                        "format": "before-after",
                        "hook": f"Before: scattered notes about {raw_title}. After: content, product, service, and launch queue.",
                        "cta": "Ask for the blueprint.",
                    },
                    {
                        "format": "proof build",
                        "hook": f"I used Lexi.AI to package {raw_title} into a sellable offer in one focused session.",
                        "cta": "Comment SYSTEM for the breakdown.",
                    },
                    {
                        "format": "contrarian",
                        "hook": "The fastest AI business is not a giant app. It is a sharp service with product assets behind it.",
                        "cta": "Send your idea and I will map the first package.",
                    },
                    {
                        "format": "tutorial",
                        "hook": "Take one customer problem, generate ten hooks, package one service, then ship one proof asset.",
                        "cta": "Save this and build your first offer today.",
                    },
                    {
                        "format": "objection flip",
                        "hook": "If you think your idea is too rough to sell, that is exactly what the Cash System is built to fix.",
                        "cta": "Reply with the rough version.",
                    },
                ],
            },
            "products": [
                {
                    "name": f"{raw_title} Blueprint Pack",
                    "deliverable": "A downloadable template pack with offer prompts, content hooks, launch checklist, and buyer questions.",
                    "build_minutes": "30-60",
                    "price_test": "$19-$49",
                    "done_when": "A buyer can open the pack and create a first offer without another explanation.",
                },
                {
                    "name": f"{raw_title} Cash System Kit",
                    "deliverable": "A structured mini-product that turns one idea into content, product, service, and validation assets.",
                    "build_minutes": "60-120",
                    "price_test": "$49-$149",
                    "done_when": "The kit includes examples, blank templates, and a launch queue.",
                },
                {
                    "name": "Lexi.AI Offer Forge Prompt Stack",
                    "deliverable": "Reusable prompts and checklists for creating offers, posts, service scopes, and fulfillment plans.",
                    "build_minutes": "20-45",
                    "price_test": "$9-$29",
                    "done_when": "The prompt stack produces a usable one-page offer from a raw idea.",
                },
            ],
            "services": [
                {
                    "name": "Cash System Sprint",
                    "promise": f"Turn a raw {raw_title} idea into a content plan, product shelf, service offer, and launch assets.",
                    "scope": "One intake, one generated asset pack, one revision pass, and one launch checklist.",
                    "delivery_window": "48 hours",
                    "price_test": "$500-$1500",
                },
                {
                    "name": "Offer Page Buildout",
                    "promise": "Create a one-page offer, checkout-ready copy, FAQ, and proof plan for one productized service.",
                    "scope": "Copy, structure, content angles, CTA, and validation metrics.",
                    "delivery_window": "24-72 hours",
                    "price_test": "$300-$900",
                },
                {
                    "name": "Creator Revenue Asset Day",
                    "promise": "Convert a creator's existing notes into posts, emails, a mini-product outline, and a service menu.",
                    "scope": "Asset extraction, packaging, first-week content, and follow-up scripts.",
                    "delivery_window": "1 day",
                    "price_test": "$750-$2500",
                },
            ],
            "launch_assets": {
                "one_page_offer": {
                    "headline": f"Turn {raw_title} into content, products, and services in minutes.",
                    "subheadline": "Lexi.AI packages raw ideas into buyer-ready assets so you can test demand before overbuilding.",
                    "deliverables": [
                        "content hooks",
                        "product ideas",
                        "service packages",
                        "DM and email scripts",
                        "validation checklist",
                    ],
                    "cta": "Book a Cash System Sprint",
                },
                "dm_script": (
                    f"I am testing a Lexi.AI Cash System for {raw_title}. "
                    "It turns a rough idea into hooks, products, services, and launch copy fast. "
                    "Want me to map yours?"
                ),
                "email_subjects": [
                    f"Your {raw_title} idea can become an offer today",
                    "Stop collecting ideas. Start packaging outcomes.",
                    "A fast way to turn AI output into a paid service",
                ],
                "short_posts": [
                    "One idea can become three assets: a proof post, a small product, and a productized service.",
                    "The first goal is not automation. The first goal is buyer signal.",
                    "Lexi.AI should make the path from thought to offer feel almost unfairly fast.",
                ],
            },
            "fulfillment_workflow": [
                "Collect customer goal, current assets, target buyer, proof, and deadline.",
                "Generate the Cash System pack and remove anything that overpromises.",
                "Pick one paid offer and one simple product asset.",
                "Publish three proof posts and send ten direct outreach messages.",
                "Log replies, objections, and conversion signals before expanding.",
            ],
            "artifact_plan": [
                {
                    "name": "cash-system.md",
                    "purpose": "Human-readable monetization pack for content, products, services, and launch assets.",
                },
                {
                    "name": "cash-system.json",
                    "purpose": "Structured source of truth for UI rendering, follow-up automation, and testing.",
                },
                {
                    "name": "launch-assets",
                    "purpose": "Hooks, DM script, email subjects, one-page offer copy, and validation checklist.",
                },
            ],
            "validation_checks": [
                "The offer names one buyer and one outcome.",
                "The buyer can understand the deliverable in under ten seconds.",
                "The service can be delivered with a repeatable checklist.",
                "At least five prospects are asked before building a larger product.",
                "Revenue claims are framed as tests, not guarantees.",
            ],
            "metrics": [
                "published posts",
                "qualified replies",
                "booked calls",
                "checkout clicks",
                "paid conversions",
                "delivery time per client",
                "refund or revision requests",
            ],
            "risk_register": [
                {
                    "risk": "The system promises money instead of a useful business process.",
                    "countermeasure": "Use validation language and buyer-signal metrics instead of guaranteed income claims.",
                },
                {
                    "risk": "Too many products are built before demand is proven.",
                    "countermeasure": "Sell a productized service first and turn delivery assets into products later.",
                },
                {
                    "risk": "Fulfillment becomes custom work every time.",
                    "countermeasure": "Keep a delivery checklist, scope limits, and one revision pass.",
                },
            ],
            "build_queue": [
                {"rank": 1, "action": "Choose one buyer segment and one painful outcome for the first Cash System offer."},
                {"rank": 2, "action": "Publish three hooks from the content engine and track replies."},
                {"rank": 3, "action": "Package the Cash System Sprint as the first paid service."},
                {"rank": 4, "action": "Create the Blueprint Pack from repeated delivery assets after the first buyer signal."},
                {"rank": 5, "action": "Save objections, proof, and conversion notes back into Lexi.AI memory."},
            ],
            "context_paths": context_paths,
        }

    def _write_blueprint_artifacts(
        self,
        blueprint: Dict[str, Any],
        artifact_root: Optional[str] = None,
    ) -> Dict[str, str]:
        output_root = Path(artifact_root) if artifact_root else ROOT / "workspace" / "blueprints"
        output_root.mkdir(parents=True, exist_ok=True)

        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        slug = self._slugify(blueprint["title"])
        base_path = output_root / f"{stamp}-{slug}"
        markdown_path = base_path.with_suffix(".md")
        json_path = base_path.with_suffix(".json")

        markdown_path.write_text(self._blueprint_markdown(blueprint), encoding="utf-8")
        json_path.write_text(json.dumps(blueprint, indent=2, ensure_ascii=True), encoding="utf-8")

        return {
            "markdown": str(markdown_path),
            "json": str(json_path),
        }

    def _write_cash_system_artifacts(
        self,
        cash_system: Dict[str, Any],
        artifact_root: Optional[str] = None,
    ) -> Dict[str, str]:
        output_root = Path(artifact_root) if artifact_root else ROOT / "workspace" / "cash-systems"
        output_root.mkdir(parents=True, exist_ok=True)

        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        slug = self._slugify(cash_system["title"])
        base_path = output_root / f"{stamp}-{slug}"
        markdown_path = base_path.with_suffix(".md")
        json_path = base_path.with_suffix(".json")

        markdown_path.write_text(self._cash_system_markdown(cash_system), encoding="utf-8")
        json_path.write_text(json.dumps(cash_system, indent=2, ensure_ascii=True), encoding="utf-8")

        return {
            "markdown": str(markdown_path),
            "json": str(json_path),
        }

    def _blueprint_markdown(self, blueprint: Dict[str, Any]) -> str:
        lines = [
            f"# {blueprint['title']}",
            "",
            f"**Idea:** {blueprint['idea']}",
            f"**Depth:** {blueprint['depth']}",
            "",
            f"## Mission",
            "",
            blueprint["mission"],
            "",
            "## Automation Ladder",
            "",
        ]
        for item in blueprint["automation_ladder"]:
            lines.append(f"- **{item['stage']}:** {item['action']}")

        lines.extend(["", "## System Layers", ""])
        for layer in blueprint["system_layers"]:
            lines.extend(
                [
                    f"### {layer['name']}",
                    f"- Purpose: {layer['purpose']}",
                    f"- Inputs: {', '.join(layer['inputs'])}",
                    f"- Outputs: {', '.join(layer['outputs'])}",
                    "",
                ]
            )

        lines.extend(["## Component Specs", ""])
        for spec in blueprint["component_specs"]:
            lines.extend(
                [
                    f"### {spec['component']}",
                    f"- Build: {spec['build']}",
                    f"- Done when: {spec['done_when']}",
                    "",
                ]
            )

        lines.extend(["## Prototype Sprints", ""])
        for sprint in blueprint["prototype_sprints"]:
            lines.append(f"### {sprint['window']}")
            lines.append(f"- Outcome: {sprint['outcome']}")
            for task in sprint["tasks"]:
                lines.append(f"- {task}")
            lines.append("")

        lines.extend(["## Validation Checks", ""])
        for check in blueprint["validation_checks"]:
            lines.append(f"- [ ] {check}")

        lines.extend(["", "## Build Queue", ""])
        for item in blueprint["build_queue"]:
            lines.append(f"{item['rank']}. {item['action']}")

        if blueprint["context_paths"]:
            lines.extend(["", "## Context Files", ""])
            for path in blueprint["context_paths"]:
                lines.append(f"- {path}")

        return "\n".join(lines).strip() + "\n"

    def _cash_system_markdown(self, cash_system: Dict[str, Any]) -> str:
        offer = cash_system["launch_assets"]["one_page_offer"]
        lines = [
            f"# {cash_system['title']}",
            "",
            f"**Idea:** {cash_system['idea']}",
            f"**Market:** {cash_system['market']}",
            f"**Offer type:** {cash_system['offer_type']}",
            "",
            "## Mission",
            "",
            cash_system["mission"],
            "",
            "## Positioning",
            "",
            f"- Promise: {cash_system['positioning']['promise']}",
            f"- Target customer: {cash_system['positioning']['target_customer']}",
            f"- Urgent problem: {cash_system['positioning']['urgent_problem']}",
            f"- Safe claim: {cash_system['positioning']['safe_claim']}",
            "",
            "## Money Rules",
            "",
        ]
        for rule in cash_system["money_rules"]:
            lines.append(f"- {rule}")

        lines.extend(["", "## Cash Ladder", ""])
        for item in cash_system["cash_ladder"]:
            lines.append(f"- **{item['stage']}:** {item['action']}")

        lines.extend(["", "## Content Hooks", ""])
        for hook in cash_system["content_engine"]["hooks"]:
            lines.extend(
                [
                    f"### {hook['format']}",
                    f"- Hook: {hook['hook']}",
                    f"- CTA: {hook['cta']}",
                    "",
                ]
            )

        lines.extend(["## Products", ""])
        for product in cash_system["products"]:
            lines.extend(
                [
                    f"### {product['name']}",
                    f"- Deliverable: {product['deliverable']}",
                    f"- Build time: {product['build_minutes']} minutes",
                    f"- Price test: {product['price_test']}",
                    f"- Done when: {product['done_when']}",
                    "",
                ]
            )

        lines.extend(["## Services", ""])
        for service in cash_system["services"]:
            lines.extend(
                [
                    f"### {service['name']}",
                    f"- Promise: {service['promise']}",
                    f"- Scope: {service['scope']}",
                    f"- Delivery window: {service['delivery_window']}",
                    f"- Price test: {service['price_test']}",
                    "",
                ]
            )

        lines.extend(
            [
                "## One-Page Offer",
                "",
                f"- Headline: {offer['headline']}",
                f"- Subheadline: {offer['subheadline']}",
                f"- CTA: {offer['cta']}",
                "- Deliverables:",
            ]
        )
        for deliverable in offer["deliverables"]:
            lines.append(f"  - {deliverable}")

        lines.extend(["", "## Launch Assets", ""])
        lines.append(f"- DM script: {cash_system['launch_assets']['dm_script']}")
        lines.append("- Email subjects:")
        for subject in cash_system["launch_assets"]["email_subjects"]:
            lines.append(f"  - {subject}")
        lines.append("- Short posts:")
        for post in cash_system["launch_assets"]["short_posts"]:
            lines.append(f"  - {post}")

        lines.extend(["", "## Fulfillment Workflow", ""])
        for step in cash_system["fulfillment_workflow"]:
            lines.append(f"- {step}")

        lines.extend(["", "## Validation Checks", ""])
        for check in cash_system["validation_checks"]:
            lines.append(f"- [ ] {check}")

        lines.extend(["", "## Build Queue", ""])
        for item in cash_system["build_queue"]:
            lines.append(f"{item['rank']}. {item['action']}")

        if cash_system["context_paths"]:
            lines.extend(["", "## Context Files", ""])
            for path in cash_system["context_paths"]:
                lines.append(f"- {path}")

        return "\n".join(lines).strip() + "\n"

    def _cash_system_llm_notes(self, idea: str, cash_system: Dict[str, Any], files: List[dict]) -> str:
        if not self.llm_client:
            return "Ollama client is not configured; deterministic Cash System automation was used."

        file_lines = "\n".join(
            f"- {item['path']}: {item['summary']}" for item in files[:6]
        ) or "- No relevant files found yet."
        prompt = f"""You are Lexi.AI's Cash System packaging engine.

Idea: {idea}
Cash System title: {cash_system['title']}

Relevant local files:
{file_lines}

Return one concise note naming the first offer to test, the strongest content angle,
and the biggest fulfillment risk. Do not promise guaranteed revenue."""
        try:
            return self.llm_client.chat([{"role": "user", "content": prompt}])
        except BigDaddyDrewBackendError as exc:
            return f"Ollama was unavailable, so deterministic Cash System automation was used. Detail: {exc}"
        except Exception as exc:
            return f"LLM Cash System enrichment failed, so deterministic automation was used. Detail: {exc}"

    def _blueprint_llm_notes(self, idea: str, blueprint: Dict[str, Any], files: List[dict]) -> str:
        if not self.llm_client:
            return "Ollama client is not configured; deterministic blueprint automation was used."

        file_lines = "\n".join(
            f"- {item['path']}: {item['summary']}" for item in files[:6]
        ) or "- No relevant files found yet."
        prompt = f"""You are Lexi.AI's blueprint automation engine.

Idea: {idea}
Blueprint title: {blueprint['title']}

Relevant local files:
{file_lines}

Return one concise note naming the first artifact to build, the biggest feasibility risk,
and the smallest useful prototype. Do not claim anything has been built."""
        try:
            return self.llm_client.chat([{"role": "user", "content": prompt}])
        except BigDaddyDrewBackendError as exc:
            return f"Ollama was unavailable, so deterministic blueprint automation was used. Detail: {exc}"
        except Exception as exc:
            return f"LLM blueprint enrichment failed, so deterministic automation was used. Detail: {exc}"

    def _title_from_idea(self, idea: str) -> str:
        clean = " ".join(idea.strip().split())
        words = clean.split()[:8]
        return " ".join(words).strip(" .,:;!?") or "Untitled Blueprint"

    def _cash_title_from_idea(self, idea: str) -> str:
        clean = " ".join(idea.strip().split())
        lower = clean.lower()
        if lower.startswith("turn ") and " into " in lower:
            into_index = lower.index(" into ")
            subject = clean[len("turn "):into_index].strip(" .,:;!?")
            outcome = clean[into_index + len(" into "):].strip(" .,:;!?")
            if subject:
                if any(term in outcome.lower() for term in ("money", "cash", "revenue", "income")):
                    return f"{subject} Money Machine"
                return self._title_from_idea(subject)
        return self._title_from_idea(idea)

    def _slugify(self, value: str) -> str:
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
        return slug[:72] or "blueprint"

    def _approval_gates(self) -> List[str]:
        return [
            "Reading local files is allowed only inside configured roots.",
            "Writing files outside the LexiAI workspace requires explicit approval.",
            "Shell commands that install packages, delete files, publish data, spend money, or call paid APIs require approval.",
            "Secrets are never printed, indexed, or stored in memory.",
        ]

    def _llm_notes(self, goal: str, mode: str, files: List[dict]) -> str:
        if not self.llm_client:
            return "Ollama client is not configured; deterministic local plan was used."

        file_lines = "\n".join(
            f"- {item['path']}: {item['summary']}" for item in files[:8]
        ) or "- No relevant files found yet."
        prompt = f"""You are Lexi.AI's local creative engineering intelligence core.

Goal: {goal}
Mode: {mode}

Relevant local files:
{file_lines}

Return a concise platform note with the most important next move, biggest risk,
and first blueprint or artifact to create. Do not claim any action was already completed."""
        try:
            return self.llm_client.chat([{"role": "user", "content": prompt}])
        except BigDaddyDrewBackendError as exc:
            return f"Ollama was unavailable, so deterministic planning was used. Detail: {exc}"
        except Exception as exc:
            return f"LLM enrichment failed, so deterministic planning was used. Detail: {exc}"
