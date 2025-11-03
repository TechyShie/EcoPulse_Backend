from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv
from pathlib import Path

# --- Load environment variables ---
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path, override=True)

# --- Default to local SQLite if DATABASE_URL not set ---
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    BASE_DIR = Path(__file__).resolve().parents[2]
    DATABASE_URL = f"sqlite:///{BASE_DIR / 'ecopulse.db'}"

# --- Configure engine for SQLite (thread safety) ---
engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

# --- Create engine, session, and base ---
engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Dependency for FastAPI ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
