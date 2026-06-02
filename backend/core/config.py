"""
CollegePath AI — Core Configuration
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = "CollegePath AI"
    app_env: str = "development"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    secret_key: str = "dev-secret-key-change-in-production-min-32-chars"

    # Groq
    groq_api_key: str = Field(default="", env="GROQ_API_KEY")
    groq_model: str = "llama-3.3-70b-versatile"

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/collegepath.db"

    # File storage
    upload_dir: str = "data/uploads"
    processed_dir: str = "data/processed"
    vectorstore_dir: str = "data/vectorstore"
    max_upload_size_mb: int = 20

    # Vector DB
    embedding_model: str = "all-MiniLM-L6-v2"
    chroma_persist_dir: str = "data/vectorstore/chroma"

    class Config:
        env_file = ".env"
        extra = "ignore"

    def ensure_dirs(self):
        for d in [self.upload_dir, self.processed_dir, self.vectorstore_dir, self.chroma_persist_dir]:
            Path(d).mkdir(parents=True, exist_ok=True)


@lru_cache()
def get_settings() -> Settings:
    s = Settings()
    s.ensure_dirs()
    return s
