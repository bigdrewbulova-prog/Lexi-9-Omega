from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from datetime import datetime
from brain.memory import init_memory, save_memory, recent_memories
from lexi_app.autonomous_core import AutonomousRun, BlueprintBuildRequest, CashSystemRequest, LexiAutonomousCore
from lexi_app.lead_pipeline import LeadPipeline
from lexi_app.lexi_backend import BigDaddyDrewBackendError, OllamaBigDaddyDrewClient

app = FastAPI(title="Lexi.AI Creative Engineering Core", version="0.5")

autonomous_core = LexiAutonomousCore.from_disk()
lead_pipeline = LeadPipeline()

class ChatMessage(BaseModel):
    message: str
    use_model: bool = True


class AutonomousRunRequest(BaseModel):
    goal: str
    mode: str = "auto"
    autonomy: str = "supervised"
    max_files: int = 250
    roots: list[str] | None = None


class ScanRequest(BaseModel):
    roots: list[str] | None = None
    max_files: int = 500
    query: str = ""


class MonitorCheckInRequest(BaseModel):
    roots: list[str] | None = None
    max_files: int = 500
    query: str = ""


class BlueprintRequest(BaseModel):
    idea: str
    depth: str = "prototype"
    write_artifacts: bool = True
    use_model_notes: bool = False
    max_files: int = 200
    roots: list[str] | None = None


class CashSystemAPIRequest(BaseModel):
    idea: str
    market: str = "creators, builders, and small businesses"
    offer_type: str = "content-product-service"
    speed: str = "minutes"
    write_artifacts: bool = True
    use_model_notes: bool = False
    max_files: int = 200
    roots: list[str] | None = None


class LeadCaptureRequest(BaseModel):
    email: str
    name: str = ""
    source: str = "proof-page-waitlist"
    offer: str = "Lexi.AI Cash System early access"
    interest: str = "cash-system generation, blueprint reports, prototype planning"
    stage: str = "Waitlist"
    notes: str = ""
    tags: list[str] | None = None


@app.on_event("startup")
def startup():
    init_memory()

@app.get("/")
def home():
    elite_profile = autonomous_core.elite_profile()
    return {
        "status": "LEXI.AI ONLINE",
        "core": "Lexi.AI Creative Engineering Core",
        "mode": "creative engineering intelligence platform",
        "positioning": "part AI companion, part invention lab, part futuristic blueprint generator",
        "elite_profile": elite_profile.get("name", "Lexi.PHYS Elite"),
        "elite_summary": elite_profile.get("summary", ""),
        "capabilities": [item["name"] for item in autonomous_core.capabilities()],
        "time": datetime.now().isoformat()
    }


@app.get("/health")
def health():
    return {
        "ok": True,
        "service": "Lexi.AI creative engineering core",
        "version": app.version,
        "time": datetime.now().isoformat(),
    }


@app.post("/chat")
def chat(data: ChatMessage):
    msg = data.message.strip()
    if not msg:
        raise HTTPException(status_code=400, detail="message cannot be empty")

    response = None
    if data.use_model:
        try:
            client = OllamaBigDaddyDrewClient.from_disk()
            response = client.chat([{"role": "user", "content": msg}])
        except BigDaddyDrewBackendError as exc:
            response = (
                "The configured model backend is not reachable, so I saved the message and kept the core online. "
                f"Backend detail: {exc}"
            )

    if response is None:
        response = (
            "Lexi.AI has received your command. "
            "Companion memory, project scanning, invention planning, and blueprint generation are online."
        )

    save_memory(msg, response)

    return {
        "user": msg,
        "lexi": response,
        "bigdaddydrew": response,
        "memory_saved": True
    }

@app.get("/memory")
def memory():
    rows = recent_memories()
    return {
        "recent_memory": [
            {
                "user_input": r[0],
                "lexi_response": r[1],
                "created_at": r[2]
            }
            for r in rows
        ]
    }


@app.get("/autonomous/tools")
def autonomous_tools():
    return {"tools": autonomous_core.capabilities()}


@app.get("/identity/lexi-phys")
def lexi_phys_identity():
    return autonomous_core.elite_profile()


@app.post("/autonomous/scan")
def autonomous_scan(data: ScanRequest):
    return autonomous_core.scan_projects(
        roots=data.roots,
        max_files=data.max_files,
        query=data.query,
    )


@app.post("/autonomous/monitor/check-in")
def autonomous_monitor_check_in(data: MonitorCheckInRequest):
    return autonomous_core.monitor_projects(
        roots=data.roots,
        max_files=data.max_files,
        query=data.query,
    )


@app.get("/autonomous/monitor/check-ins")
def autonomous_monitor_check_ins(limit: int = 10):
    return {"checkins": autonomous_core.recent_monitor_checkins(limit=limit)}


@app.post("/autonomous/run")
def autonomous_run(data: AutonomousRunRequest):
    try:
        return autonomous_core.run(
            AutonomousRun(
                goal=data.goal,
                mode=data.mode,
                autonomy=data.autonomy,
                max_files=data.max_files,
                roots=data.roots,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/blueprint")
def blueprint(data: BlueprintRequest):
    try:
        return autonomous_core.generate_blueprint(
            BlueprintBuildRequest(
                idea=data.idea,
                depth=data.depth,
                write_artifacts=data.write_artifacts,
                use_model_notes=data.use_model_notes,
                max_files=data.max_files,
                roots=data.roots,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/cash-system")
def cash_system(data: CashSystemAPIRequest):
    try:
        return autonomous_core.generate_cash_system(
            CashSystemRequest(
                idea=data.idea,
                market=data.market,
                offer_type=data.offer_type,
                speed=data.speed,
                write_artifacts=data.write_artifacts,
                use_model_notes=data.use_model_notes,
                max_files=data.max_files,
                roots=data.roots,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/leads")
def capture_lead(data: LeadCaptureRequest):
    try:
        lead = lead_pipeline.capture_lead(
            email=data.email,
            name=data.name,
            source=data.source,
            offer=data.offer,
            interest=data.interest,
            stage=data.stage,
            notes=data.notes,
            tags=data.tags,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

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


@app.get("/autonomous/runs")
def autonomous_runs(limit: int = 10):
    return {"runs": autonomous_core.recent_runs(limit=limit)}
