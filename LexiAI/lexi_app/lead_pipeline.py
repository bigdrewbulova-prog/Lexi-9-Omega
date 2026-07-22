#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LEAD_ROOT = ROOT / "workspace" / "leads"

LEAD_FIELDS = [
    "id",
    "created_at",
    "updated_at",
    "email",
    "name",
    "stage",
    "source",
    "offer",
    "interest",
    "notes",
    "tags",
    "touch_count",
]

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_email(email: str) -> str:
    clean = (email or "").strip().lower()
    if not EMAIL_RE.match(clean):
        raise ValueError("A valid email address is required.")
    return clean


def lead_id_for_email(email: str) -> str:
    digest = hashlib.sha256(email.encode("utf-8")).hexdigest()[:16]
    return f"lead_{digest}"


def coerce_tags(tags: Optional[Iterable[str]]) -> List[str]:
    if not tags:
        return []
    clean_tags = []
    for tag in tags:
        clean = str(tag).strip()
        if clean and clean not in clean_tags:
            clean_tags.append(clean)
    return clean_tags


class LeadPipeline:
    """Server-side waitlist and lead pipeline persistence for Lexi.AI."""

    def __init__(self, root: Optional[str | Path] = None) -> None:
        self.root = Path(root) if root else DEFAULT_LEAD_ROOT
        self.json_path = self.root / "leads.json"
        self.csv_path = self.root / "leads.csv"

    def capture_lead(
        self,
        *,
        email: str,
        name: str = "",
        source: str = "proof-page-waitlist",
        offer: str = "Lexi.AI Cash System early access",
        interest: str = "cash-system generation, blueprint reports, prototype planning",
        stage: str = "Waitlist",
        notes: str = "",
        tags: Optional[Iterable[str]] = None,
    ) -> Dict[str, Any]:
        normalized_email = normalize_email(email)
        now = utc_now()
        leads = self.list_leads()
        lead = next((item for item in leads if item.get("email") == normalized_email), None)
        clean_tags = coerce_tags(tags)

        if lead is None:
            lead = {
                "id": lead_id_for_email(normalized_email),
                "created_at": now,
                "updated_at": now,
                "email": normalized_email,
                "name": name.strip(),
                "stage": stage.strip() or "Waitlist",
                "source": source.strip() or "proof-page-waitlist",
                "offer": offer.strip(),
                "interest": interest.strip(),
                "notes": notes.strip(),
                "tags": clean_tags,
                "touch_count": 1,
            }
            leads.append(lead)
        else:
            lead["updated_at"] = now
            lead["touch_count"] = int(lead.get("touch_count") or 0) + 1
            self._update_text_field(lead, "name", name)
            self._update_text_field(lead, "stage", stage)
            self._update_text_field(lead, "source", source)
            self._update_text_field(lead, "offer", offer)
            self._update_text_field(lead, "interest", interest)
            self._update_text_field(lead, "notes", notes)
            existing_tags = coerce_tags(lead.get("tags") or [])
            lead["tags"] = existing_tags + [tag for tag in clean_tags if tag not in existing_tags]

        leads.sort(key=lambda item: item.get("updated_at", ""), reverse=True)
        self._write(leads)
        return dict(lead)

    def list_leads(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        leads = self._read()
        leads.sort(key=lambda item: item.get("updated_at", ""), reverse=True)
        if limit is not None:
            return leads[: max(0, int(limit))]
        return leads

    def summary(self, leads: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        rows = leads if leads is not None else self.list_leads()
        return {
            "total": len(rows),
            "waitlist": sum(1 for row in rows if row.get("stage") == "Waitlist"),
            "qualified": sum(1 for row in rows if row.get("stage") == "Qualified"),
            "offer_sent": sum(1 for row in rows if row.get("stage") == "Offer Sent"),
            "paid": sum(1 for row in rows if row.get("stage") == "Paid"),
            "json_export": str(self.json_path),
            "csv_export": str(self.csv_path),
        }

    def export_json_text(self) -> str:
        payload = {
            "updated_at": utc_now(),
            "summary": self.summary(),
            "leads": self.list_leads(),
        }
        return json.dumps(payload, indent=2, ensure_ascii=True) + "\n"

    def export_csv_text(self) -> str:
        return self._csv_text_for(self.list_leads())

    def _csv_text_for(self, leads: List[Dict[str, Any]]) -> str:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=LEAD_FIELDS)
        writer.writeheader()
        for lead in leads:
            writer.writerow(self._csv_row(lead))
        return output.getvalue()

    def _read(self) -> List[Dict[str, Any]]:
        if not self.json_path.exists():
            return []
        try:
            raw = json.loads(self.json_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
        if isinstance(raw, list):
            leads = raw
        else:
            leads = raw.get("leads", [])
        normalized = []
        for item in leads:
            if not isinstance(item, dict):
                continue
            try:
                normalized.append(self._normalize_record(item))
            except ValueError:
                continue
        return normalized

    def _write(self, leads: List[Dict[str, Any]]) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        payload = {"updated_at": utc_now(), "leads": [self._normalize_record(item) for item in leads]}
        temp_json = self.json_path.with_suffix(".json.tmp")
        temp_json.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
        temp_json.replace(self.json_path)

        temp_csv = self.csv_path.with_suffix(".csv.tmp")
        temp_csv.write_text(self._csv_text_for(payload["leads"]), encoding="utf-8")
        temp_csv.replace(self.csv_path)

    def _normalize_record(self, item: Dict[str, Any]) -> Dict[str, Any]:
        email = normalize_email(str(item.get("email", "")))
        created_at = str(item.get("created_at") or item.get("updated_at") or utc_now())
        updated_at = str(item.get("updated_at") or created_at)
        return {
            "id": str(item.get("id") or lead_id_for_email(email)),
            "created_at": created_at,
            "updated_at": updated_at,
            "email": email,
            "name": str(item.get("name") or ""),
            "stage": str(item.get("stage") or "Waitlist"),
            "source": str(item.get("source") or "proof-page-waitlist"),
            "offer": str(item.get("offer") or "Lexi.AI Cash System early access"),
            "interest": str(item.get("interest") or ""),
            "notes": str(item.get("notes") or ""),
            "tags": coerce_tags(item.get("tags") or []),
            "touch_count": int(item.get("touch_count") or 1),
        }

    def _csv_row(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        row = self._normalize_record(lead)
        row["tags"] = "; ".join(row["tags"])
        return row

    @staticmethod
    def _update_text_field(lead: Dict[str, Any], key: str, value: str) -> None:
        clean = (value or "").strip()
        if clean:
            lead[key] = clean
