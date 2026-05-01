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
    - MOEX_BASE_URL       (базовый URL ISS API)
    - MOEX_TIMEOUT        (таймаут HTTP-запросов в секундах)
    - MOEX_USER_AGENT     (User-Agent клиента)
    - MOEX_LOG_LEVEL      (уровень логирования)
    - MOEX_REQUEST_DELAY  (базовая задержка между запросами, сек)
    - MOEX_REQUEST_JITTER (случайный jitter к задержке, сек)

    """

    # Базовый URL API Московской биржи
    base_url: str = "https://iss.moex.com/iss"

    # Таймаут сетевых запросов (секунды)
    timeout: int = 10

    # User-Agent для идентификации SDK
    user_agent: str = "pymoex-sdk/0.1.6"

    log_level: str = "WARNING"

    # Учетные данные
    username: str | None = None
    password: str | None = None

    # Минимальная задержка между запросами (в секундах)
    # Чтобы не словить бан по IP
    request_delay: float = 0.1

    # Случайный jitter (в секундах), добавляемый к базовой задержке
    # Можно отключить, установив 0
    request_jitter: float = 0.05

    # Прокси для запросов
    proxy_url: str | None = None

    preferred_share_boards: list[str] = ["TQBR", "TQTF", "FQBR", "TQTD"]
    preferred_bond_boards: list[str] = ["TQOB", "TQCB", "TQOD", "TQIR"]
    preferred_currency_boards: list[str] = ["CETS", "CNGD", "SNDX"]

    # Конфигурация pydantic-settings
    model_config = SettingsConfigDict(
        env_prefix="MOEX_",  # префикс переменных окружения
        env_file=BASE_DIR / ".env",  # путь к .env файлу
        env_file_encoding="utf-8",  # кодировка файла
        extra="ignore",  # игнорировать неизвестные переменные окружения
    )


# Глобальный синглтон настроек.
# Используется всеми сервисами и сессиями SDK.
settings = MoexSettings()
