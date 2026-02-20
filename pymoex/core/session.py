import logging

import httpx
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from pymoex.core.config import MoexSettings
from pymoex.exceptions import MoexAPIError, MoexNetworkError

logger = logging.getLogger(__name__)


def _is_retryable_error(exception: BaseException) -> bool:
    """
    Определяет, нужно ли повторять запрос.
    Повторяем только при проблемах с сетью или 5xx ошибках сервера.
    """
    if isinstance(exception, httpx.RequestError):
        return True  # Ошибки сети (таймауты, DNS, обрывы)
    if isinstance(exception, httpx.HTTPStatusError):
        return exception.response.status_code >= 500  # 500, 502, 503, 504 и т.д.
    return False


class MoexSession:
    """
    Асинхронная HTTP-сессия для работы с MOEX ISS API.
    Оборачивает httpx.AsyncClient и инкапсулирует базовые настройки и механизм Retry.
    """

    def __init__(self):
        self.settings = MoexSettings()

        self.client = httpx.AsyncClient(
            base_url=self.settings.base_url,
            timeout=self.settings.timeout,
            headers={
                "User-Agent": self.settings.user_agent,
            },
        )

    @retry(
        retry=retry_if_exception(_is_retryable_error),
        stop=stop_after_attempt(3),  # Максимум 3 попытки
        wait=wait_exponential(multiplier=1, min=1, max=10),  # Задержки: 1s, 2s, 4s...
        before_sleep=before_sleep_log(
            logger, logging.WARNING
        ),  # Логируем каждый ретрай
        reraise=True,  # Пробрасываем ошибку дальше, если попытки исчерпаны
    )
    async def _execute_request(
        self, path: str, params: dict | None = None
    ) -> httpx.Response:
        """Внутренний метод для выполнения запроса с механизмом повторных попыток."""
        response = await self.client.get(path, params=params)
        response.raise_for_status()
        return response

    async def get(self, path: str, params: dict | None = None) -> dict:
        """
        Выполнить GET-запрос к MOEX ISS API.

        :param path: относительный путь (например, '/securities.json')
        :param params: query-параметры запроса
        :return: JSON-ответ, преобразованный в dict
        """

        logger.debug(f"GET {path} params={params}")

        try:
            # Делегируем выполнение запроса методу с @retry
            response = await self._execute_request(path, params)
            return response.json()

        except httpx.HTTPStatusError as e:
            # Сюда попадут 4xx ошибки сразу, а 5xx — если исчерпаны все попытки ретраев
            logger.error(f"HTTP {e.response.status_code} error requesting {path}")
            raise MoexNetworkError(
                f"HTTP error {e.response.status_code} for {path}"
            ) from e
        except httpx.RequestError as e:
            # Исчерпаны все попытки при сетевых сбоях
            logger.error(f"Network error requesting {path}: {e}")
            raise MoexNetworkError(f"Network error accessing {path}: {e}") from e
        except Exception as e:
            logger.exception(f"Unexpected error requesting {path}")
            raise MoexAPIError(f"Unexpected error: {e}") from e

    async def close(self) -> None:
        """Корректно закрыть HTTP-сессию."""
        await self.client.aclose()
