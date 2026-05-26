from pydantic import BaseModel
from typing import Optional
import os


class Settings(BaseModel):
    APP_NAME: str = "RSOD Detection Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    STATIC_DIR: str = "static"
    UPLOAD_DIR: str = "static/uploads"
    RESULT_DIR: str = "static/results"

    YOLO_MODEL_PATH: str = "app/models/best.pt"
    CONFIDENCE_THRESHOLD: float = 0.5
    IOU_THRESHOLD: float = 0.45

    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]

    JWT_SECRET: str = os.getenv("JWT_SECRET", "rsod-platform-secret-key-2026-secure-xyz")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")

    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")

    # SMTP Settings
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.qq.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 465))
    SMTP_USER: str = os.getenv("SMTP_USER", "1183209167@qq.com")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "cbspquvlxkpbjffe")
    SMTP_FROM_NAME: str = os.getenv("SMTP_FROM_NAME", "RSOD Platform")

    # MinIO Settings
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_SECURE: bool = os.getenv("MINIO_SECURE", "False").lower() == "true"
    MINIO_BUCKET_NAME: str = os.getenv("MINIO_BUCKET_NAME", "rsod-platform")


def get_settings() -> Settings:
    settings = Settings()

    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    try:
                        key, value = line.split("=", 1)
                        # 兼容不同命名的环境变量
                        if key == "MINIO_BUCKET":
                            key = "MINIO_BUCKET_NAME"
                            
                        if hasattr(settings, key):
                            current_val = getattr(settings, key)
                            if isinstance(current_val, bool):
                                setattr(settings, key, value.lower() == "true")
                            else:
                                setattr(settings, key, type(current_val)(value))
                    except (ValueError, IndexError):
                        pass

    return settings


settings = get_settings()