import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional
from sqlmodel import SQLModel, Field, Session, select
from app.database import get_session

class LabStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class Lab(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str
    description: str | None = None
    status: LabStatus = LabStatus.PENDING
    parameters: dict = Field(sa_column_kwargs={"default": "{}"})
    logs: list[str] = Field(sa_column_kwargs={"default": "[]"})
    result_location: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


def create_lab(name: str, description: str | None, parameters: dict) -> Lab:
    with get_session() as session:
        lab = Lab(name=name, description=description, parameters=parameters)
        session.add(lab)
        session.commit()
        session.refresh(lab)
        return lab


def list_labs() -> List[Lab]:
    with get_session() as session:
        statement = select(Lab)
        return session.exec(statement).all()


def get_lab(lab_id: str) -> Lab | None:
    with get_session() as session:
        return session.get(Lab, lab_id)


def update_lab(lab: Lab) -> Lab:
    lab.updated_at = datetime.utcnow()
    with get_session() as session:
        session.add(lab)
        session.commit()
        session.refresh(lab)
        return lab
