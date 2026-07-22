from __future__ import annotations

import importlib
import os
import tempfile
import unittest
from pathlib import Path

from lexi_app.project_scanner import ProjectScanner


class ProjectScannerTests(unittest.TestCase):
    def test_scan_skips_real_env_files_and_keeps_templates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Demo\nUseful project notes.", encoding="utf-8")
            (root / ".env.local").write_text("OPENAI_API_KEY=secret", encoding="utf-8")
            (root / ".env.example").write_text("OPENAI_API_KEY=", encoding="utf-8")

            records = ProjectScanner(roots=[str(root)], max_files=10).scan()
            names = {Path(record["path"]).name for record in records}

            self.assertIn("README.md", names)
            self.assertIn(".env.example", names)
            self.assertNotIn(".env.local", names)


class AutonomousCoreTests(unittest.TestCase):
    def test_elite_profile_loads_structured_capabilities(self) -> None:
        import lexi_app.autonomous_core as autonomous_core

        core = autonomous_core.LexiAutonomousCore(llm_client=None)
        profile = core.elite_profile()
        tool_names = {item["name"] for item in core.capabilities()}

        self.assertEqual(profile["id"], "lexi_phys_elite")
        self.assertIn("core_domains", profile)
        self.assertIn("elite_capability_clusters", profile)
        self.assertIn("lexi_phys_elite_profile", tool_names)
        self.assertIn("structural_foresight", tool_names)
        self.assertIn("reverse_engineering_analyst", tool_names)
        self.assertIn("cash_system", tool_names)

    def test_run_creates_company_builder_plan_with_temp_memory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "notes.md").write_text("AI company model notes", encoding="utf-8")
            previous_db = os.environ.get("LEXI_MEMORY_DB")
            os.environ["LEXI_MEMORY_DB"] = str(root / "memory.db")

            import brain.memory as memory
            import lexi_app.autonomous_core as autonomous_core

            try:
                importlib.reload(memory)
                importlib.reload(autonomous_core)

                core = autonomous_core.LexiAutonomousCore(llm_client=None)
                run = core.run(
                    autonomous_core.AutonomousRun(
                        goal="Build a model and AI company",
                        roots=[str(root)],
                        max_files=10,
                    )
                )

                self.assertEqual(run["mode"], "company-builder")
                self.assertEqual(run["status"], "planned")
                self.assertTrue((root / "memory.db").exists())
                self.assertGreaterEqual(run["run_id"], 1)

                cash_run = core.run(
                    autonomous_core.AutonomousRun(
                        goal="Create content products and services to monetize Lexi.AI",
                        roots=[str(root)],
                        max_files=10,
                    )
                )
                self.assertEqual(cash_run["mode"], "cash-system")
                self.assertIn("cash_system_os", cash_run["result"])
            finally:
                if previous_db is None:
                    os.environ.pop("LEXI_MEMORY_DB", None)
                else:
                    os.environ["LEXI_MEMORY_DB"] = previous_db
                importlib.reload(memory)
                importlib.reload(autonomous_core)

    def test_blueprint_generation_writes_artifacts_and_build_queue(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "idea.md").write_text("Blueprint generator notes", encoding="utf-8")
            artifact_root = root / "blueprints"
            previous_db = os.environ.get("LEXI_MEMORY_DB")
            os.environ["LEXI_MEMORY_DB"] = str(root / "memory.db")

            import brain.memory as memory
            import lexi_app.autonomous_core as autonomous_core

            try:
                importlib.reload(memory)
                importlib.reload(autonomous_core)

                core = autonomous_core.LexiAutonomousCore(llm_client=None)
                result = core.generate_blueprint(
                    autonomous_core.BlueprintBuildRequest(
                        idea="Build a blueprint automation lab",
                        roots=[str(root)],
                        artifact_root=str(artifact_root),
                        max_files=10,
                    )
                )

                blueprint = result["result"]["blueprint"]
                artifacts = result["result"]["artifacts"]

                self.assertEqual(result["status"], "blueprinted")
                self.assertGreaterEqual(result["run_id"], 1)
                self.assertIn("build_queue", blueprint)
                self.assertGreaterEqual(len(blueprint["build_queue"]), 1)
                self.assertTrue(Path(artifacts["markdown"]).exists())
                self.assertTrue(Path(artifacts["json"]).exists())
                self.assertIn("Validation Checks", Path(artifacts["markdown"]).read_text(encoding="utf-8"))
            finally:
                if previous_db is None:
                    os.environ.pop("LEXI_MEMORY_DB", None)
                else:
                    os.environ["LEXI_MEMORY_DB"] = previous_db
                importlib.reload(memory)
                importlib.reload(autonomous_core)

    def test_cash_system_generation_writes_artifacts_and_offer_stack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "offer-notes.md").write_text("Cash system and creator offer notes", encoding="utf-8")
            artifact_root = root / "cash-systems"
            previous_db = os.environ.get("LEXI_MEMORY_DB")
            os.environ["LEXI_MEMORY_DB"] = str(root / "memory.db")

            import brain.memory as memory
            import lexi_app.autonomous_core as autonomous_core

            try:
                importlib.reload(memory)
                importlib.reload(autonomous_core)

                core = autonomous_core.LexiAutonomousCore(llm_client=None)
                result = core.generate_cash_system(
                    autonomous_core.CashSystemRequest(
                        idea="Turn Lexi.AI into a money-making machine for content products and services",
                        roots=[str(root)],
                        artifact_root=str(artifact_root),
                        max_files=10,
                    )
                )

                cash_system = result["result"]["cash_system"]
                artifacts = result["result"]["artifacts"]

                self.assertEqual(result["status"], "packaged")
                self.assertGreaterEqual(result["run_id"], 1)
                self.assertEqual(cash_system["title"], "Cash System: Lexi.AI Money Machine")
                self.assertIn("content_engine", cash_system)
                self.assertGreaterEqual(len(cash_system["products"]), 1)
                self.assertGreaterEqual(len(cash_system["services"]), 1)
                self.assertTrue(Path(artifacts["markdown"]).exists())
                self.assertTrue(Path(artifacts["json"]).exists())
                self.assertIn("One-Page Offer", Path(artifacts["markdown"]).read_text(encoding="utf-8"))
            finally:
                if previous_db is None:
                    os.environ.pop("LEXI_MEMORY_DB", None)
                else:
                    os.environ["LEXI_MEMORY_DB"] = previous_db
                importlib.reload(memory)
                importlib.reload(autonomous_core)


class ProjectMonitorTests(unittest.TestCase):
    def test_check_in_snapshots_and_reports_meaningful_changes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "project"
            project.mkdir()
            (project / "a.md").write_text("# Alpha\nOriginal body", encoding="utf-8")
            (project / "c.md").write_text("# Charlie\nWill be removed", encoding="utf-8")

            previous_db = os.environ.get("LEXI_MEMORY_DB")
            os.environ["LEXI_MEMORY_DB"] = str(root / "memory.db")

            import brain.memory as memory
            import lexi_app.project_monitor as project_monitor

            try:
                importlib.reload(memory)
                importlib.reload(project_monitor)

                baseline = project_monitor.ProjectMonitor(
                    roots=[str(project)],
                    max_files=10,
                ).check_in()

                self.assertEqual(baseline["status"], "baseline")
                self.assertEqual(baseline["summary"]["total_changes"], 0)
                self.assertEqual(baseline["summary"]["current_file_count"], 2)

                (project / "a.md").write_text("# Alpha changed\nOriginal body", encoding="utf-8")
                (project / "b.md").write_text("# Bravo\nNew file", encoding="utf-8")
                (project / "c.md").unlink()

                checkin = project_monitor.ProjectMonitor(
                    roots=[str(project)],
                    max_files=10,
                ).check_in()

                self.assertEqual(checkin["status"], "changed")
                self.assertEqual(checkin["summary"]["added_count"], 1)
                self.assertEqual(checkin["summary"]["modified_count"], 1)
                self.assertEqual(checkin["summary"]["removed_count"], 1)
                self.assertEqual(checkin["summary"]["total_changes"], 3)
                self.assertEqual(len(project_monitor.ProjectMonitor.recent_checkins(limit=5)), 2)
            finally:
                if previous_db is None:
                    os.environ.pop("LEXI_MEMORY_DB", None)
                else:
                    os.environ["LEXI_MEMORY_DB"] = previous_db
                importlib.reload(memory)
                importlib.reload(project_monitor)


if __name__ == "__main__":
    unittest.main()
