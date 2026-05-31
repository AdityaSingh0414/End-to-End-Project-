from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Healthcare AI CDSS"
    environment: str = "development"
    database_url: str = "postgresql://postgres:postgres@localhost:5432/healthcare_ai"
    ml_model_path: str = "ml/saved_models/symptom_model.joblib"
    rag_index_path: str = "rag/vector_db/faiss.index"
    rag_metadata_path: str = "rag/vector_db/metadata.json"
    fusion_ml_weight: float = 0.6
    fusion_dl_weight: float = 0.4

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()

