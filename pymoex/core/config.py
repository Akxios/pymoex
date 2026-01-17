from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]


class MoexSettings(BaseSettings):
    base_url: str
    timeout: int
    user_agent: str

    model_config = SettingsConfigDict(
        env_prefix="MOEX_",
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
    )


settings = MoexSettings()
