from fastapi import APIRouter
from app.schemas import SystemStatusResponse
from app.services.ollama import ping

router = APIRouter(prefix="/system", tags=["system"])

@router.get("/status", response_model=SystemStatusResponse)
def system_status() -> SystemStatusResponse:
    return SystemStatusResponse(
        status="ok",
        description="Lexi.PHYS companion system status",
        model="lexi",
        ollama=ping(),
    )
