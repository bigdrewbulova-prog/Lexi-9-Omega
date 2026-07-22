from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field

class EventType(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

class Event(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    event_type: EventType
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
