# app/app_config.py

from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Literal
from pathlib import Path

class Settings(BaseSettings):
    API_AUTH_TOKEN: str
    GROQ_API_KEY: str = "llama3-70b-8192"
    OPENAI_API_KEY: str = ""
    GROQ_MODEL_NAME: Literal["llama3-70b-8192", "llama3-8b-8192"] = "llama3-70b-8192"
    OPENAI_MODEL_NAME: str = "gpt-3.5-turbo"
    TEMPERATURE: float = 0.2
    MAX_TOKENS: int = 1024
    provider: Literal["groq", "openai"] = "groq"

    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50

    DEBUG: bool = True
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "DEBUG"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    USE_PINECONE: bool = False

    UPLOAD_DIR: Path = Path("temp_docs")

    @field_validator("UPLOAD_DIR", mode="before")
    @classmethod
    def create_upload_dir(cls, v: Path) -> Path:
        path = Path(v)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        return path

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
