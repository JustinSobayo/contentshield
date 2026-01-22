import os
from pydantic_settings import BaseSettings

from typing import Optional

class Settings(BaseSettings):
    GEMINI_API_KEY: Optional[str] = None
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL") or os.getenv("REDISURL") or "redis://redis:6379/0"
    ENVIRONMENT: str = os.getenv("RAILWAY_ENVIRONMENT", "development")
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
        extra = "ignore"

settings = Settings()
