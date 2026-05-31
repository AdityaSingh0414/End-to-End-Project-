from __future__ import annotations

from fastapi import APIRouter

from backend.models.schemas import ChatPayload
from backend.services.rag_service import answer_medical_query


router = APIRouter(prefix="/api/v1/chat", tags=["RAG Chatbot"])


@router.post("/query")
async def chat_query(payload: ChatPayload) -> dict:
    return answer_medical_query(payload.query)

