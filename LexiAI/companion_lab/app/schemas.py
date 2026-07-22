from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class HealthResponse(BaseModel):
    status: str
    system: str
    ollama: bool
    model: str
    memory: bool
    labs: bool

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    conversation_id: str

class MemoryEntry(BaseModel):
    conversation_id: str
    role: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MemorySearchResponse(BaseModel):
    results: List[MemoryEntry]

class SystemStatusResponse(BaseModel):
    status: str
    description: str
    model: str
    ollama: bool
    last_checked: datetime = Field(default_factory=datetime.utcnow)

class LabCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    parameters: dict = Field(default_factory=dict)

class LabResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    parameters: dict
    logs: List[str]
    result_location: Optional[str]

class LabListResponse(BaseModel):
    labs: List[LabResponse]
