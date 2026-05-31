import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")
DEFAULT_DB_PATH = BASE_DIR / "data" / "healthcare_ai.db"
DEFAULT_DATABASE_URL = f"sqlite:///{DEFAULT_DB_PATH.as_posix()}"


class Settings(BaseSettings):
    app_name: str = "Healthcare AI Intelligence Platform"
    app_env: str = Field(default="development", alias="APP_ENV")
    database_url: str = Field(default=DEFAULT_DATABASE_URL, alias="DATABASE_URL")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    llm_model: str = Field(default="gpt-4o-mini", alias="LLM_MODEL")
    upload_dir: Path = BASE_DIR / "data" / "uploads"
    vector_store_path: Path = BASE_DIR / "rag" / "vector_db" / "index.pkl"
    seed_data_path: Path = BASE_DIR / "data" / "cleaned_data.csv"

    model_config = SettingsConfigDict(
        env_file=os.fspath(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )


settings = Settings()

if settings.database_url.endswith("news.db"):
    settings.database_url = DEFAULT_DATABASE_URL
