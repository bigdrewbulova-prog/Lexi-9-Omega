import sys
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from lexi_app.autonomous_core import BlueprintBuildRequest, CashSystemRequest, LexiAutonomousCore
from lexi_app.lead_pipeline import LeadPipeline
from lexi_core.llm import ask_lexi
from lexi_core.search import search_files
from lexi_core.memory import save_memory, load_recent_memory

ROOT = Path(__file__).resolve().parents[1]
app = FastAPI(title="Lexi.AI Invention Lab Dashboard")
app.mount("/static", StaticFiles(directory=str(ROOT / "dashboard" / "static")), name="static")
app.mount("/avatars", StaticFiles(directory=str(ROOT / "avatars"), check_dir=False), name="avatars")
blueprint_core = LexiAutonomousCore.from_disk()
lead_pipeline = LeadPipeline()

class ChatIn(BaseModel):
    message: str

class BlueprintIn(BaseModel):
    idea: str
    depth: str = "prototype"
    write_artifacts: bool = True
    use_model_notes: bool = False
    max_files: int = 200

class CashSystemIn(BaseModel):
    idea: str
    market: str = "creators, builders, and small businesses"
    offer_type: str = "content-product-service"
    speed: str = "minutes"
    write_artifacts: bool = True
    use_model_notes: bool = False
    max_files: int = 200

class LeadCaptureIn(BaseModel):
    email: str
    name: str = ""
    source: str = "proof-page-waitlist"
    offer: str = "Lexi.AI Cash System early access"
    interest: str = "cash-system generation, blueprint reports, prototype planning"
    stage: str = "Waitlist"
    notes: str = ""
    tags: list[str] | None = None

class GrowthAutomationIn(BaseModel):
    goal: str = "Build Lexi.AI from ground zero to a large company sales machine"
    channels: list[str] = ["Facebook", "Instagram", "TikTok", "YouTube", "X", "LinkedIn"]
    stage: str = "ground-zero"

@app.get("/health")
def health():
    elite_profile = blueprint_core.elite_profile()
    return {
        "status": "online",
        "system": "Lexi.AI creative engineering core",
        "positioning": "AI companion, invention lab, blueprint generator",
        "elite_profile": elite_profile.get("name", "Lexi.PHYS Elite"),
    }

@app.get("/identity/lexi-phys")
def lexi_phys_identity():
    return blueprint_core.elite_profile()

@app.get("/avatar-model")
def avatar_model():
    model_path = ROOT / "avatars" / "models" / "avatar.glb"
    return {"url": "/avatars/models/avatar.glb" if model_path.exists() else None}

@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)

@app.get("/", response_class=HTMLResponse)
def home():
    return (ROOT / "dashboard" / "static" / "index.html").read_text(encoding="utf-8")

@app.post("/chat")
def chat(payload: ChatIn):
    msg = payload.message.strip()
    save_memory("user", msg)
    chunks = search_files(msg, limit=5)
    memory = load_recent_memory(limit=20)
    reply = ask_lexi(msg, context_chunks=chunks, recent_memory=memory)
    save_memory("assistant", reply)
    return {"reply": reply, "sources": [{"path": c.get("path"), "name": c.get("name")} for c in chunks]}

@app.post("/blueprint")
def blueprint(payload: BlueprintIn):
    try:
        result = blueprint_core.generate_blueprint(
            BlueprintBuildRequest(
                idea=payload.idea,
                depth=payload.depth,
                write_artifacts=payload.write_artifacts,
                use_model_notes=payload.use_model_notes,
                max_files=payload.max_files,
                roots=[str(PROJECT_ROOT)],
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    save_memory("user", f"Blueprint idea: {payload.idea}")
    save_memory("assistant", result["result"]["summary"])
    return result

@app.post("/cash-system")
def cash_system(payload: CashSystemIn):
    try:
        result = blueprint_core.generate_cash_system(
            CashSystemRequest(
                idea=payload.idea,
                market=payload.market,
                offer_type=payload.offer_type,
                speed=payload.speed,
                write_artifacts=payload.write_artifacts,
                use_model_notes=payload.use_model_notes,
                max_files=payload.max_files,
                roots=[str(PROJECT_ROOT)],
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    save_memory("user", f"Cash System idea: {payload.idea}")
    save_memory("assistant", result["result"]["summary"])
    return result

@app.post("/leads")
def capture_lead(payload: LeadCaptureIn):
    try:
        lead = lead_pipeline.capture_lead(
            email=payload.email,
            name=payload.name,
            source=payload.source,
            offer=payload.offer,
            interest=payload.interest,
            stage=payload.stage,
            notes=payload.notes,
            tags=payload.tags,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    save_memory("user", f"Proof page waitlist lead: {lead['email']}")
    save_memory("assistant", "Captured the lead in the Lexi.AI server-side pipeline.")
    return {
        "status": "captured",
        "lead": lead,
        "summary": lead_pipeline.summary(),
        "export_paths": {
            "json": str(lead_pipeline.json_path),
            "csv": str(lead_pipeline.csv_path),
        },
    }

@app.get("/leads")
def leads(limit: int = 100):
    all_rows = lead_pipeline.list_leads()
    rows = all_rows[: max(0, int(limit))]
    return {
        "status": "success",
        "summary": lead_pipeline.summary(all_rows),
        "leads": rows,
        "export_paths": {
            "json": str(lead_pipeline.json_path),
            "csv": str(lead_pipeline.csv_path),
        },
    }

@app.get("/leads/export.csv")
def leads_export_csv():
    return Response(
        lead_pipeline.export_csv_text(),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="lexi_leads.csv"'},
    )

@app.get("/leads/export.json")
def leads_export_json():
    return Response(
        lead_pipeline.export_json_text(),
        media_type="application/json",
        headers={"Content-Disposition": 'attachment; filename="lexi_leads.json"'},
    )

@app.post("/growth-automation")
def growth_automation(payload: GrowthAutomationIn):
    goal = payload.goal.strip() or "Build Lexi.AI from ground zero to a large company sales machine"
    channels = [channel.strip() for channel in payload.channels if channel.strip()]
    if not channels:
        channels = ["Facebook", "Instagram", "TikTok", "YouTube", "X", "LinkedIn"]

    plan = {
        "goal": goal,
        "stage": payload.stage,
        "guardrails": [
            "No bank credentials, social passwords, or private tokens are collected by this dashboard.",
            "Social media actions stay as drafts, queues, and approval-gated tasks unless official platform APIs are added later.",
            "Boosting sales means better content, offers, follow-up, analytics, and compliant paid-campaign planning.",
            "Money movement and wallet actions require the user to open the provider directly and approve every step.",
        ],
        "company_stages": [
            {
                "name": "Ground zero",
                "target": "Prove one painful buyer problem and one paid promise.",
                "automation": ["Generate Cash System pack", "Publish proof posts", "Track replies", "Log every sale"],
                "metric": "5 qualified replies or 1 paid test",
            },
            {
                "name": "First sales",
                "target": "Sell a productized sprint before building a large product.",
                "automation": ["DM follow-up queue", "Offer page copy", "Sales call checklist", "Delivery checklist"],
                "metric": "3 paid customers and delivery under 48 hours",
            },
            {
                "name": "Repeatable engine",
                "target": "Turn delivery assets into products and recurring campaigns.",
                "automation": ["Weekly content calendar", "Objection bank", "Case study builder", "Referral prompts"],
                "metric": "10 sales, 2 repeatable offers, clear conversion rate",
            },
            {
                "name": "Small team",
                "target": "Separate marketing, sales, fulfillment, support, and finance dashboards.",
                "automation": ["Role handoff checklists", "Quality review", "Pipeline stages", "Weekly KPI review"],
                "metric": "Consistent weekly revenue and documented fulfillment",
            },
            {
                "name": "Scale",
                "target": "Run channel-specific campaigns with analytics and approval gates.",
                "automation": ["Campaign briefs", "Creative variants", "Retargeting plan", "Forecast dashboard"],
                "metric": "Channel ROI, CAC, conversion rate, and fulfillment capacity",
            },
            {
                "name": "Large company status",
                "target": "Operate with departments, dashboards, compliance, and strategic planning.",
                "automation": ["Executive scorecard", "Revenue ops", "Customer success loops", "Audit logs"],
                "metric": "Predictable pipeline, retention, margins, and accountable owners",
            },
        ],
        "social_sales_boosters": [
            {
                "channel": channel,
                "daily_action": f"Publish one proof post and one offer-aware story on {channel}.",
                "weekly_action": f"Review {channel} comments, replies, clicks, booked calls, and sales.",
                "automation_queue": [
                    "Draft three hooks",
                    "Create one proof asset",
                    "Queue follow-up messages for manual approval",
                    "Log conversion signals",
                ],
            }
            for channel in channels
        ],
        "sales_pipeline": [
            "Lead captured",
            "Problem qualified",
            "Offer sent",
            "Call booked",
            "Invoice or checkout sent",
            "Paid",
            "Delivered",
            "Proof captured",
            "Upsell or referral requested",
        ],
        "next_actions": [
            "Link Chime and wallet references in the local dashboard without entering credentials.",
            "Add three test sales to calibrate the chart.",
            "Generate one Cash System pack for the flagship offer.",
            "Publish three Facebook/social proof posts and track replies.",
            "Use the first buyer signal to choose the first paid productized service.",
        ],
    }

    save_memory("user", f"Growth automation goal: {goal}")
    save_memory("assistant", "Generated a ground-zero-to-large-company sales automation plan.")
    return {"status": "planned", "plan": plan}
