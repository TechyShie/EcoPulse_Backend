# app/core/config.py
import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "EcoPulse"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    # Database - Use absolute path
    DATABASE_URL: str = f"sqlite:///{os.path.join(os.path.dirname(__file__), '..', '..', 'ecopulse.db')}"

    # JWT
    SECRET_KEY: str = "CQfRxJAfut1O7inECy0LWRpOKos5CoHfXREYH2ATOWc"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # AI Services
    OPENROUTER_API_KEY: Optional[str] = None

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }

def get_database_url():
    # Use the absolute path from settings
    database_url = os.getenv("DATABASE_URL", Settings().DATABASE_URL)
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    return database_url

settings = Settings()
settings.DATABASE_URL = get_database_url()