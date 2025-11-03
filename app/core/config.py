from pydantic_settings import BaseSettings
from pathlib import Path
from dotenv import load_dotenv

# --- Load .env robustly ---
env_path = Path(__file__).resolve().parents[2] / ".env"
if not env_path.exists():
    env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path, override=True)


# --- Settings Model ---
class Settings(BaseSettings):
    SECRET_KEY: str
    REFRESH_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    DATABASE_URL: str | None = None
    OPENAI_API_KEY: str | None = None

    model_config = {
        "env_file": env_path,
        "env_file_encoding": "utf-8",
    }


# --- Instantiate Once ---
settings = Settings()

# --- Sanity Check ---
if not all([settings.SECRET_KEY, settings.REFRESH_SECRET_KEY]):
    raise ValueError("SECRET_KEY or REFRESH_SECRET_KEY is missing in .env — app startup aborted.")
