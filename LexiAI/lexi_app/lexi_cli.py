#!/usr/bin/env python3
from __future__ import annotations

import json
import shlex
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from brain.memory import init_memory, recent_memories, save_memory
from autonomous_core import AutonomousRun, BlueprintBuildRequest, CashSystemRequest, LexiAutonomousCore
from chatgpt_importer import import_chatgpt_export
from lexi_backend import OllamaBigDaddyDrewClient, BigDaddyDrewBackendError


def print_help() -> None:
    print(
        "\nCommands:\n"
        "  /goal <objective>   Plan a Lexi.AI invention or engineering run\n"
        "  /blueprint <idea>   Generate and save a buildable blueprint\n"
        "  /cash-system <idea> Generate content, product, service, and launch assets\n"
        "  /cash <idea>        Shortcut for /cash-system\n"
        "  /scan [query]       Index local project files and optional query matches\n"
        "  /import-chatgpt <path>\n"
        "                      Import a ChatGPT data export ZIP or folder\n"
        "  /watch [root ...]   Snapshot watched roots and report project changes\n"
        "  /changes [limit]    Show recent project monitor check-ins\n"
        "  /runs               Show recent autonomous runs\n"
        "  /memory             Show recent chat memory\n"
        "  /tools              Show available platform capabilities\n"
        "  /profile            Show the Lexi.PHYS Elite capability profile\n"
        "  /help               Show this help\n"
        "  /exit               Quit\n"
    )


def print_json(data) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=True))


def main() -> int:
    init_memory()
    client = OllamaBigDaddyDrewClient.from_disk()
    core = LexiAutonomousCore(client)
    print(f"[{client.config.window_title}] CLI mode")
    print("Type /help for commands or /exit to quit.\n")

    try:
        client.ping()
    except BigDaddyDrewBackendError as exc:
        print(f"Startup warning: {exc}")
        print("Autonomous planning and scanning still work without the local model.\n")

    messages = []
    while True:
        try:
            user_text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_text:
            continue
        if user_text.lower() in {"/exit", "exit", "quit"}:
            break
        if user_text.lower() == "/help":
            print_help()
            continue
        if user_text.lower() == "/tools":
            print_json({"tools": core.capabilities()})
            continue
        if user_text.lower() == "/profile":
            print_json(core.elite_profile())
            continue
        if user_text.lower().startswith("/scan"):
            query = user_text.removeprefix("/scan").strip()
            print_json(core.scan_projects(query=query, max_files=250))
            continue
        if user_text.lower().startswith("/import-chatgpt"):
            raw_path = user_text.removeprefix("/import-chatgpt").strip()
            try:
                parts = shlex.split(raw_path)
            except ValueError as exc:
                print(f"Import error: {exc}")
                continue
            if len(parts) != 1:
                print("Usage: /import-chatgpt <path-to-export.zip-or-folder>")
                continue
            try:
                result = import_chatgpt_export(parts[0])
            except (FileNotFoundError, ValueError, RuntimeError) as exc:
                print(f"Import error: {exc}")
                continue
            print_json(result.as_dict())
            continue
        if user_text.lower().startswith("/watch"):
            raw_roots = user_text.removeprefix("/watch").strip()
            try:
                roots = shlex.split(raw_roots) if raw_roots else None
            except ValueError as exc:
                print(f"Watch error: {exc}")
                continue
            print_json(core.monitor_projects(roots=roots, max_files=250))
            continue
        if user_text.lower().startswith("/goal"):
            goal = user_text.removeprefix("/goal").strip()
            if not goal:
                print("Usage: /goal <objective>")
                continue
            try:
                run = core.run(AutonomousRun(goal=goal))
            except ValueError as exc:
                print(f"Goal error: {exc}")
                continue
            print_json(
                {
                    "run_id": run["run_id"],
                    "mode": run["mode"],
                    "status": run["status"],
                    "plan": run["plan"],
                    "next_actions": run["result"]["next_actions"],
                    "llm_notes": run["result"]["llm_notes"],
                }
            )
            continue
        if user_text.lower().startswith("/blueprint"):
            idea = user_text.removeprefix("/blueprint").strip()
            if not idea:
                print("Usage: /blueprint <idea>")
                continue
            try:
                blueprint = core.generate_blueprint(BlueprintBuildRequest(idea=idea))
            except ValueError as exc:
                print(f"Blueprint error: {exc}")
                continue
            print_json(
                {
                    "run_id": blueprint["run_id"],
                    "status": blueprint["status"],
                    "title": blueprint["result"]["blueprint"]["title"],
                    "artifacts": blueprint["result"]["artifacts"],
                    "build_queue": blueprint["result"]["blueprint"]["build_queue"],
                }
            )
            continue
        if user_text.lower().startswith("/cash-system") or user_text.lower().startswith("/cash"):
            command = "/cash-system" if user_text.lower().startswith("/cash-system") else "/cash"
            idea = user_text[len(command):].strip()
            if not idea:
                print(f"Usage: {command} <idea>")
                continue
            try:
                cash_system = core.generate_cash_system(CashSystemRequest(idea=idea))
            except ValueError as exc:
                print(f"Cash System error: {exc}")
                continue
            print_json(
                {
                    "run_id": cash_system["run_id"],
                    "status": cash_system["status"],
                    "title": cash_system["result"]["cash_system"]["title"],
                    "artifacts": cash_system["result"]["artifacts"],
                    "build_queue": cash_system["result"]["cash_system"]["build_queue"],
                    "products": cash_system["result"]["cash_system"]["products"],
                    "services": cash_system["result"]["cash_system"]["services"],
                }
            )
            continue
        if user_text.lower() == "/runs":
            print_json({"runs": core.recent_runs(limit=5)})
            continue
        if user_text.lower().startswith("/changes"):
            raw_limit = user_text.removeprefix("/changes").strip()
            limit = 5
            if raw_limit:
                try:
                    limit = max(1, int(raw_limit))
                except ValueError:
                    print("Usage: /changes [limit]")
                    continue
            print_json({"checkins": core.recent_monitor_checkins(limit=limit)})
            continue
        if user_text.lower() == "/memory":
            rows = recent_memories(limit=10)
            print_json(
                {
                    "recent_memory": [
                        {
                            "user_input": row[0],
                            "lexi_response": row[1],
                            "created_at": row[2],
                        }
                        for row in rows
                    ]
                }
            )
            continue

        messages.append({"role": "user", "content": user_text})
        try:
            reply = client.chat(messages)
        except BigDaddyDrewBackendError as exc:
            print(f"Lexi.AI error: {exc}")
            continue

        messages.append({"role": "assistant", "content": reply})
        save_memory(user_text, reply)
        print(f"Lexi.AI: {reply}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
