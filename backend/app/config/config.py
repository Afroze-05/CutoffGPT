from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import os

class Settings(BaseSettings):
    GROQ_API_KEY: str
    DATABASE_URL: str = "sqlite:///./collegepath.db"
    JWT_SECRET: str = "your_super_secret_jwt_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200
    CHROMA_DB_PATH: str = "./chroma_db"
    UPLOADS_DIR: str = "./uploads"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()

# Ensure directories exist
os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)
