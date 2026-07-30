from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "CORE STRENGTH API"
    app_env: str = "development"
    # Dùng APP_DEBUG thay vì DEBUG để tránh xung đột với biến môi trường
    # chung của VS Code/Code Runner và các công cụ trên Windows.
    app_debug: bool = Field(default=True, validation_alias="APP_DEBUG")
    api_prefix: str = "/api"
    host: str = "0.0.0.0"
    port: int = 8000
    timezone: str = "Asia/Ho_Chi_Minh"

    database_url: str = (
        "mysql+pymysql://root:@127.0.0.1:3306/gym_db?charset=utf8mb4"
    )

    secret_key: str = "CHANGE_ME_TO_A_LONG_RANDOM_SECRET_KEY_AT_LEAST_32_CHARACTERS"
    qr_secret_key: str = "CHANGE_ME_TO_A_DIFFERENT_LONG_RANDOM_QR_SECRET"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30
    qr_token_expire_seconds: int = 30
    password_reset_otp_minutes: int = 10

    cors_origins: List[str] | str = Field(default_factory=lambda: ["*"])

    outbox_enabled: bool = True
    outbox_poll_seconds: float = 1.0
    outbox_batch_size: int = 100

    upload_dir: str = "uploads"
    public_base_url: str = "http://127.0.0.1:8000"
    max_avatar_size_mb: int = 5


    @field_validator("app_debug", mode="before")
    @classmethod
    def parse_app_debug(cls, value: object) -> bool | object:
        """Cho phép cả true/false và các tên môi trường phổ biến."""
        if isinstance(value, bool):
            return value
        if value is None:
            return True
        text = str(value).strip().lower()
        if text in {"1", "true", "yes", "on", "debug", "development", "dev"}:
            return True
        if text in {"0", "false", "no", "off", "release", "production", "prod"}:
            return False
        return value

    @property
    def debug(self) -> bool:
        """Giữ tương thích với code cũ đang gọi settings.debug."""
        return self.app_debug

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> list[str]:
        if value is None:
            return ["*"]
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        text = str(value).strip()
        if not text:
            return ["*"]
        return [part.strip() for part in text.split(",") if part.strip()]

    @property
    def upload_path(self) -> Path:
        path = Path(self.upload_dir)
        return path if path.is_absolute() else BASE_DIR / path

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
