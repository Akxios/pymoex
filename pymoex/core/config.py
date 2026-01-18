from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class MoexSettings(BaseSettings):
    """
    Настройки клиента MOEX, загружаемые из переменных окружения или .env файла.

    Поддерживаемые переменные:
    - MOEX_BASE_URL
    - MOEX_TIMEOUT
    - MOEX_USER_AGENT
    """

    base_url: str
    timeout: int
    user_agent: str

    model_config = SettingsConfigDict(
        env_prefix="MOEX_",
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
    )


# Глобальный экземпляр настроек
settings = MoexSettings()
