from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    MONGO_URI: str
    DATABASE_NAME: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    MODEL_PATH: str
    MODEL_AUTO_DOWNLOAD: bool = False
    MODEL_DOWNLOAD_URL: Optional[str] = None
    MODEL_DOWNLOAD_TIMEOUT_SECONDS: int = 300
    MODEL_SHA256: Optional[str] = None
    ALLOW_API_START_WITHOUT_MODEL: bool = True
    DETECTION_METHOD: str = "local"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_TIMEOUT_SECONDS: int = 45
    GEMINI_DETECTION_CONFIG_PATH: str = "app/configs/gemini_detection_config.json"
    UPLOAD_DIR: str = "uploads"
    PARALLEL_BACKEND_SAVE_ENABLED: bool = True
    PARALLEL_BACKEND_SAVE_DIR: str = "uploads_backend_copy"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
