from fastapi import FastAPI
from app.routers import chat, health, memory, labs, system

app = FastAPI(title="LEXI.PHYS Companion Lab")

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(memory.router)
app.include_router(labs.router)
app.include_router(system.router)
