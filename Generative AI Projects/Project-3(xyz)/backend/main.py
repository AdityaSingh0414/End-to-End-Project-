from __future__ import annotations

from fastapi import FastAPI

from backend.config.settings import get_settings
from backend.routes import chat, predict


settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    description="AI-powered clinical decision support portfolio project.",
    version="0.1.0",
)

app.include_router(predict.router)
app.include_router(chat.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}

