"""Stage-1 Local-First Intelligence Stack smoke tests."""
from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

from brain.intelligence_stack import BrandIntake, LocalFirstIntelligenceStack
from brain.memory import Memory


class BrandIntakeTests(unittest.TestCase):
    def test_validate_ok(self) -> None:
        intake = BrandIntake(name="Nova Thread", vibe="dark", audience="creators", offer="pack")
        self.assertEqual(intake.validate(), [])

    def test_validate_requires_name(self) -> None:
        intake = BrandIntake(name="  ", vibe="dark", audience="creators", offer="pack")
        self.assertTrue(any("name" in e for e in intake.validate()))


class BrandPackProductTests(unittest.TestCase):
    def test_brand_pack_creates_zip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mem = Memory(Path(tmp) / "test.db")
            stack = LocalFirstIntelligenceStack(memory=mem)
            out = stack.brand_pack(
                BrandIntake(
                    name="Test Pack Co",
                    vibe="clean technical",
                    audience="founders",
                    offer="$50 blueprint pack",
                )
            )
            self.assertTrue(out["quality_checklist"]["passed"])
            zip_path = out.get("zip")
            self.assertIsNotNone(zip_path)
            self.assertTrue(Path(zip_path).is_file())
            with zipfile.ZipFile(zip_path) as zf:
                names = set(zf.namelist())
            self.assertIn("README.md", names)
            self.assertIn("brand_pack.md", names)
            self.assertIn("brand_pack.html", names)
            self.assertIn("brand_pack.json", names)

    def test_invalid_intake_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stack = LocalFirstIntelligenceStack(memory=Memory(Path(tmp) / "t.db"))
            with self.assertRaises(ValueError):
                stack.brand_pack(BrandIntake(name="", vibe="", audience="", offer=""))


if __name__ == "__main__":
    unittest.main()
