import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # SQLite Configuration
    SQLITE_DB_PATH = os.path.join("database", "sqlite", "sample.db")
    SQLITE_URI = f"sqlite:///{SQLITE_DB_PATH}"
    
    # Postgres Configuration
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT")
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    
    @classmethod
    def get_postgres_uri(cls):
        if all([cls.POSTGRES_USER, cls.POSTGRES_PASSWORD, cls.POSTGRES_HOST, cls.POSTGRES_PORT, cls.POSTGRES_DB]):
            return f"postgresql://{cls.POSTGRES_USER}:{cls.POSTGRES_PASSWORD}@{cls.POSTGRES_HOST}:{cls.POSTGRES_PORT}/{cls.POSTGRES_DB}"
        return None
