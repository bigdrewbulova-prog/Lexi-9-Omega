from sqlmodel import SQLModel, create_engine, Session
from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

def init_db() -> None:
    from app.services import memory as memory_service
    from app.services import lab_runner as lab_runner_service
    
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    return Session(engine)
