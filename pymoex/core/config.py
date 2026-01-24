from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Корень проекта (используется для поиска .env)
BASE_DIR = Path(__file__).resolve().parents[2]


class MoexSettings(BaseSettings):
    """
    Конфигурация клиента MOEX ISS API.

    Настройки автоматически подхватываются:
    - из переменных окружения
    - из файла .env в корне проекта

    Поддерживаемые переменные окружения:
    - MOEX_BASE_URL      (базовый URL ISS API)
    - MOEX_TIMEOUT       (таймаут HTTP-запросов в секундах)
    - MOEX_USER_AGENT    (User-Agent клиента)
    """

    # Базовый URL API Московской биржи
    base_url: str = "https://iss.moex.com/iss"

    # Таймаут сетевых запросов (секунды)
    timeout: int = 10

    # User-Agent для идентификации SDK
    user_agent: str = "pymoex-sdk/0.1.1"

    # Конфигурация pydantic-settings
    model_config = SettingsConfigDict(
        env_prefix="MOEX_",  # префикс переменных окружения
        env_file=BASE_DIR / ".env",  # путь к .env файлу
        env_file_encoding="utf-8",  # кодировка файла
    )


# Глобальный синглтон настроек.
# Используется всеми сервисами и сессиями SDK.
settings = MoexSettings()
