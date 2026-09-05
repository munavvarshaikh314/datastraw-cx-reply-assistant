from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import close_database
from app.api.routes.replies import router as replies_router
from app.api.routes.conversations import router as conversations_router
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_database()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://datastraw-cx-reply-assistant.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    conversations_router,
    prefix="/api",
)

app.include_router(
    replies_router,
    prefix=settings.api_prefix,
)

@app.get("/health/db")
async def database_health_check(
    session: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    await session.execute(text("SELECT 1"))
    return {
        "status": "ok",
        "database": "connected",
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.app_name,
    }