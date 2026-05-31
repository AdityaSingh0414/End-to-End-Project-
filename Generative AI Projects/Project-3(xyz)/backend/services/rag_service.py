from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from rag.chatbot.rag_pipeline import LocalRAGPipeline


@lru_cache
def load_rag() -> LocalRAGPipeline:
    if not Path("rag/vector_db/faiss.index").exists() and not Path("rag/vector_db/tfidf.joblib").exists():
        raise FileNotFoundError("RAG index missing. Run python rag/chatbot/build_index.py first.")
    return LocalRAGPipeline()


def answer_medical_query(query: str) -> dict:
    return load_rag().answer(query)
