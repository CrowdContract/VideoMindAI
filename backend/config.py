"""Central config — reads from environment variables."""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "VideoMind AI"
    DEBUG: bool = False
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")

    # MongoDB
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB: str = os.getenv("MONGODB_DB", "videomind")

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # Mistral
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
    MISTRAL_MODEL: str = os.getenv("MISTRAL_MODEL", "mistral-small-latest")

    # Whisper
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")

    # Sarvam
    SARVAM_API_KEY: str = os.getenv("SARVAM_API_KEY", "")
    SARVAM_STT_MODEL: str = os.getenv("SARVAM_STT_MODEL", "saaras:v2.5")

    # Qdrant
    QDRANT_URL: str = os.getenv("QDRANT_URL", "")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")

    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "jwt-secret-change-me")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Google OAuth
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")

    # Rate limits
    ANON_PROCESS_LIMIT: str = "3/hour"
    AUTH_PROCESS_LIMIT: str = "10/hour"
    ANON_CHAT_LIMIT: str = "10/hour"
    AUTH_CHAT_LIMIT: str = "50/hour"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
