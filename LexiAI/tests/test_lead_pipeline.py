from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from lexi_app.lead_pipeline import LeadPipeline


class LeadPipelineTests(unittest.TestCase):
    def test_capture_lead_writes_json_csv_and_dedupes_email(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pipeline = LeadPipeline(root=Path(tmp) / "leads")

            first = pipeline.capture_lead(
                email=" Buyer@Example.COM ",
                source="proof-page-waitlist",
                offer="Lexi.AI Cash System early access",
                tags=["proof-page", "cash-system"],
            )
            second = pipeline.capture_lead(
                email="buyer@example.com",
                stage="Qualified",
                notes="Asked about blueprint reports.",
                tags=["blueprint", "cash-system"],
            )

            leads = pipeline.list_leads()
            payload = json.loads(pipeline.json_path.read_text(encoding="utf-8"))
            csv_text = pipeline.csv_path.read_text(encoding="utf-8")

            self.assertEqual(first["id"], second["id"])
            self.assertEqual(len(leads), 1)
            self.assertEqual(leads[0]["email"], "buyer@example.com")
            self.assertEqual(leads[0]["stage"], "Qualified")
            self.assertEqual(leads[0]["touch_count"], 2)
            self.assertIn("proof-page", leads[0]["tags"])
            self.assertIn("blueprint", leads[0]["tags"])
            self.assertEqual(len(payload["leads"]), 1)
            self.assertIn("buyer@example.com", csv_text)
            self.assertIn("Qualified", csv_text)

    def test_invalid_email_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pipeline = LeadPipeline(root=Path(tmp) / "leads")

            with self.assertRaises(ValueError):
                pipeline.capture_lead(email="not-an-email")


if __name__ == "__main__":
    unittest.main()
