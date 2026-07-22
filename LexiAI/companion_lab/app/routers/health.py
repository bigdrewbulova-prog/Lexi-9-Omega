from fastapi import APIRouter
from app.schemas import HealthResponse
from app.services.ollama import ping

router = APIRouter(prefix="/health", tags=["health"])

@router.get("", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="online",
        system="LEXI.PHYS Companion Lab",
        ollama=ping(),
        model="lexi",
        memory=True,
        labs=True,
    )
