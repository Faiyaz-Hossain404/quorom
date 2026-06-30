"""Runtime configuration, loaded from environment / .env."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# quorum/.env lives three levels above this file (engine/app/config.py)
_ENV_FILE = Path(__file__).parent.parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE, env_file_encoding="utf-8", extra="ignore"
    )

    # Qwen / Model Studio (OpenAI-compatible)
    dashscope_api_key: str = ""
    dashscope_base_url: str = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    qwen_model_flash: str = "qwen-flash"
    qwen_model_max: str = "qwen-max"

    # MongoDB Atlas (used from Day 2)
    mongodb_uri: str = ""
    mongodb_db: str = "quorum"

    # Web
    web_origin: str = "http://localhost:3000"


settings = Settings()
