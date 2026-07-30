from typing import ClassVar

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from pymoex._version import __version__


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
    - MOEX_RETRY_ATTEMPTS (число попыток)
    - MOEX_RETRY_MIN_WAIT (минимальное ожидание, сек)
    - MOEX_RETRY_MAX_WAIT (максимальное ожидание, сек)

    """

    base_url: str = "https://iss.moex.com/iss"
    timeout: float = Field(default=10.0, gt=0)
    user_agent: str = f"pymoex-sdk/{__version__}"
    log_level: str = "WARNING"

    request_delay: float = Field(default=0.1, ge=0)
    request_jitter: float = Field(default=0.05, ge=0)

    preferred_share_boards: list[str] = Field(
        default_factory=lambda: ["TQBR", "TQTF", "FQBR", "TQTD"]
    )
    preferred_bond_boards: list[str] = Field(
        default_factory=lambda: ["TQOB", "TQCB", "TQOD", "TQIR"]
    )
    preferred_currency_boards: list[str] = Field(
        default_factory=lambda: ["CETS", "CNGD", "SNDX"]
    )

    retry_attempts: int = Field(default=3, ge=1)
    retry_min_wait: float = Field(default=1.0, ge=0)
    retry_max_wait: float = Field(default=10.0, ge=0)

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_prefix="MOEX_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = MoexSettings()
