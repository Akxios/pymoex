import asyncio
import logging
import random
import time
from typing import Any

import httpx
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from pymoex.core.config import MoexSettings
from pymoex.exceptions import (
    MoexAPIError,
    MoexAuthError,
    MoexBadRequestError,
    MoexHTTPError,
    MoexNetworkError,
    MoexNotFoundError,
    MoexRateLimitError,
    MoexResponseParseError,
    MoexServerError,
    MoexTimeoutError,
)

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

        self._rate_limit_lock = asyncio.Lock()
        self._last_request_time = 0.0

    async def _apply_rate_limit(self) -> None:
        """
        Гарантирует, что между отправкой запросов проходит не менее request_delay секунд.
        Выстраивает конкурентные запросы в честную очередь.
        """
        delay = self.settings.request_delay

        jitter = self.settings.request_jitter

        if delay <= 0 and jitter <= 0:
            return

        async with self._rate_limit_lock:
            now = time.monotonic()
            elapsed = now - self._last_request_time

            # Базовая пауза + случайный джиттер
            jitter_part = random.uniform(0, jitter) if jitter > 0 else 0.0
            target_delay = max(delay, 0.0) + jitter_part

            # Если с прошлого запроса прошло меньше времени, чем положено, спим остаток
            if elapsed < target_delay:
                await asyncio.sleep(target_delay - elapsed)

            # Обновляем время (уже после возможного сна)
            self._last_request_time = time.monotonic()

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
        self, path: str, params: dict[str, Any] | None = None
    ) -> httpx.Response:
        """Внутренний метод для выполнения запроса с механизмом повторных попыток."""

        await self._apply_rate_limit()

        response = await self.client.get(path, params=params)
        response.raise_for_status()
        return response

    async def get(
        self, path: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
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

        except httpx.HTTPStatusError as e:
            # Сюда попадут 4xx ошибки сразу, а 5xx — если исчерпаны все попытки ретраев
            status_code = e.response.status_code
            logger.error(f"HTTP {status_code} error requesting {path}")
            if status_code == 400:
                raise MoexBadRequestError(f"HTTP 400 for {path}") from e
            if status_code in {401, 403}:
                raise MoexAuthError(f"HTTP {status_code} for {path}") from e
            if status_code == 404:
                raise MoexNotFoundError(f"HTTP 404 for {path}") from e
            if status_code == 429:
                raise MoexRateLimitError(f"HTTP 429 for {path}") from e
            if status_code >= 500:
                raise MoexServerError(f"HTTP {status_code} for {path}") from e
            raise MoexHTTPError(f"HTTP {status_code} for {path}") from e
        except httpx.TimeoutException as e:
            logger.error(f"Timeout requesting {path}: {e}")
            raise MoexTimeoutError(f"Timeout while accessing {path}: {e}") from e
        except httpx.RequestError as e:
            # Исчерпаны все попытки при сетевых сбоях
            logger.error(f"Network error requesting {path}: {e}")
            raise MoexNetworkError(f"Network error accessing {path}: {e}") from e

        try:
            return response.json()
        except ValueError as e:
            logger.error(f"Response parse error for {path}: {e}")
            raise MoexResponseParseError(
                f"Invalid JSON response for {path}: {e}"
            ) from e
        except TypeError as e:
            logger.error(f"Unexpected response format for {path}: {e}")
            raise MoexResponseParseError(
                f"Unexpected response format for {path}: {e}"
            ) from e
        except Exception as e:
            logger.exception(f"Unexpected error requesting {path}")
            raise MoexAPIError(f"Unexpected error: {e}") from e

    async def close(self) -> None:
        """Корректно закрываем HTTP-сессию."""
        await self.client.aclose()
