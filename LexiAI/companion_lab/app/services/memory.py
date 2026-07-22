from datetime import datetime
from typing import List
from sqlmodel import SQLModel, Field, Session, select
from app.database import get_session
from pydantic import BaseModel

class Memory(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    conversation_id: str
    role: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


def save_message(conversation_id: str, role: str, content: str) -> Memory:
    with get_session() as session:
        memory = Memory(conversation_id=conversation_id, role=role, content=content)
        session.add(memory)
        session.commit()
        session.refresh(memory)
        return memory


def search_memory(query: str) -> List[Memory]:
    with get_session() as session:
        statement = select(Memory).where(Memory.content.contains(query))
        results = session.exec(statement).all()
        return results


def list_memory() -> List[Memory]:
    with get_session() as session:
        statement = select(Memory)
        return session.exec(statement).all()
