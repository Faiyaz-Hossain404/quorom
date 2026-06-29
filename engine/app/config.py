"""Runtime configuration, loaded from environment / .env."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
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
