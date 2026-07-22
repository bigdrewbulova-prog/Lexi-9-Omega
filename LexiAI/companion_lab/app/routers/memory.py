from typing import List
from fastapi import APIRouter, Query
from app.schemas import MemoryEntry, MemorySearchResponse
from app.services.memory import list_memory, search_memory

router = APIRouter(prefix="/memory", tags=["memory"])

@router.post("", response_model=MemoryEntry)
def create_memory(conversation_id: str, role: str, content: str) -> MemoryEntry:
    entry = list_memory()  # placeholder for actual store logic
    raise NotImplementedError("Direct memory creation endpoint is not supported yet.")

@router.get("/search", response_model=MemorySearchResponse)
def memory_search(q: str = Query(..., description="Search query")) -> MemorySearchResponse:
    results = search_memory(q)
    return MemorySearchResponse(results=[MemoryEntry(conversation_id=item.conversation_id, role=item.role, content=item.content, created_at=item.created_at) for item in results])
