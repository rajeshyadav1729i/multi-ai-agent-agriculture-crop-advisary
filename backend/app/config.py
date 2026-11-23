import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings(BaseSettings):
    PROJECT_NAME: str = "Agricultural Advisory Control Room"
    PROJECT_GROUP: str = "Group 20 – Multi-Agent AI System"
    VERSION: str = "1.0.0"
    
    # API & Hosts
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Groq LLM Settings
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    GROQ_FALLBACK_MODEL: str = os.getenv("GROQ_FALLBACK_MODEL", "qwen/qwen3.8-27b")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/advisory_control_room.db")
    DB_PATH: Path = BASE_DIR / "advisory_control_room.db"
    
    # Knowledge Base
    KNOWLEDGE_BASE_DIR: Path = BASE_DIR / "knowledge_base" / "schemes"
    
    # External APIs
    OPEN_METEO_BASE_URL: str = os.getenv("OPEN_METEO_BASE_URL", "https://api.open-meteo.com/v1/forecast")
    GEOCODING_BASE_URL: str = os.getenv("GEOCODING_BASE_URL", "https://geocoding-api.open-meteo.com/v1/search")
    ENABLE_DEMO_FALLBACK: bool = os.getenv("ENABLE_DEMO_FALLBACK", "true").lower() in ("true", "1", "yes")

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
