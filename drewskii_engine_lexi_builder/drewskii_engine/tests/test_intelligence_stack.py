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


class PackServerPathTests(unittest.TestCase):
    def test_form_html_renders(self) -> None:
        from brain.pack_server import _render_form

        html = _render_form()
        self.assertIn("Brand Blueprint", html)
        self.assertIn('action="/api/pack"', html)
        self.assertIn('name="name"', html)
        self.assertIn("/library", html)
        self.assertIn('name="customer_name"', html)
        self.assertIn("/orders", html)

    def test_list_brand_packs_and_library_html(self) -> None:
        from brain.pack_server import _render_library, list_brand_packs

        items = list_brand_packs(limit=10)
        self.assertIsInstance(items, list)
        html = _render_library()
        self.assertIn("Pack", html)
        self.assertIn("/library", html)
        self.assertIn("New pack", html)
        if items:
            self.assertIn("Download", html)
            self.assertTrue(items[0].get("download_url", "").startswith("/download/"))
            self.assertTrue(items[0].get("filename", "").endswith(".zip") or "zip" in (items[0].get("zip") or ""))


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
                ),
                customer_name="Ada Founder",
                customer_note="Discord DM",
                amount_usd=50,
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
            self.assertIsNotNone(out.get("order_id"))
            order = out.get("order") or {}
            self.assertEqual(order.get("customer_name"), "Ada Founder")
            self.assertEqual(order.get("status"), "generated")
            self.assertEqual(order.get("amount_usd"), 50)

    def test_invalid_intake_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stack = LocalFirstIntelligenceStack(memory=Memory(Path(tmp) / "t.db"))
            with self.assertRaises(ValueError):
                stack.brand_pack(BrandIntake(name="", vibe="", audience="", offer=""))


class PackOrderLedgerTests(unittest.TestCase):
    def test_order_status_lifecycle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mem = Memory(Path(tmp) / "orders.db")
            stack = LocalFirstIntelligenceStack(memory=mem)
            out = stack.brand_pack(
                BrandIntake(name="Ledger Co", vibe="clean", audience="ops", offer="pack"),
                customer_name="Bea",
                customer_note="Venmo later",
            )
            oid = out["order_id"]
            updated = stack.set_order_status(oid, "paid_manual", note="Venmo $50")
            self.assertEqual(updated["status"], "paid_manual")
            listed = stack.list_orders()
            self.assertGreaterEqual(listed["stats"]["orders"], 1)
            self.assertEqual(listed["stats"]["paid_manual_usd"], 50.0)
            with self.assertRaises(ValueError):
                stack.set_order_status(oid, "not_a_status")


if __name__ == "__main__":
    unittest.main()
