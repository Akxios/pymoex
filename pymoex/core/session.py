import asyncio
import logging
import random
import time
from collections.abc import Mapping
from types import TracebackType
from typing import Self, cast

import httpx
from tenacity import (
    AsyncRetrying,
    before_sleep_log,
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

type QueryValue = str | int | float | bool | None
type QueryParams = Mapping[str, QueryValue] | None


def _is_retryable_error(exception: BaseException) -> bool:
    """
    Определяет, нужно ли повторять запрос.
    Повторяем только при проблемах с сетью или 5xx ошибках сервера.
    """

    if isinstance(exception, httpx.TimeoutException):
        return True

    if isinstance(exception, httpx.NetworkError):
        return True

    if isinstance(exception, httpx.HTTPStatusError):
        return exception.response.status_code in {500, 502, 503, 504}

    return False


class MoexSession:
    """
    Асинхронная HTTP-сессия для работы с MOEX ISS API.
    Оборачивает httpx.AsyncClient и инкапсулирует базовые настройки и механизм Retry.
    """

    def __init__(self, settings: MoexSettings | None = None) -> None:
        self.settings: MoexSettings = settings or MoexSettings()

        self.client: httpx.AsyncClient = httpx.AsyncClient(
            base_url=self.settings.base_url,
            timeout=self.settings.timeout,
            headers={
                "User-Agent": self.settings.user_agent,
            },
        )

        self._rate_limit_lock: asyncio.Lock = asyncio.Lock()
        self._last_request_time: float = 0.0

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()

    async def _apply_rate_limit(self) -> None:
        """
        Гарантирует, что между отправкой запросов проходит не менее request_delay секунд
        Выстраивает конкурентные запросы в честную очередь.
        """
        delay = self.settings.request_delay
        jitter = self.settings.request_jitter

        if delay <= 0 and jitter <= 0:
            return

        async with self._rate_limit_lock:
            now = time.monotonic()
            elapsed = now - self._last_request_time

            jitter_part = random.uniform(0, jitter) if jitter > 0 else 0.0
            target_delay = max(delay, 0.0) + jitter_part

            if elapsed < target_delay:
                await asyncio.sleep(target_delay - elapsed)

            self._last_request_time = time.monotonic()

    async def _execute_request(
        self,
        path: str,
        params: QueryParams = None,
    ) -> httpx.Response:
        retryer = AsyncRetrying(
            retry=retry_if_exception(_is_retryable_error),
            stop=stop_after_attempt(self.settings.retry_attempts),
            wait=wait_exponential(
                multiplier=1,
                min=self.settings.retry_min_wait,
                max=self.settings.retry_max_wait,
            ),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            reraise=True,
        )

        async for attempt in retryer:
            with attempt:
                return await self._send_request(path, params)

        raise MoexAPIError("Retry loop exited unexpectedly")

    async def _send_request(
        self,
        path: str,
        params: QueryParams = None,
    ) -> httpx.Response:
        await self._apply_rate_limit()

        query = (
            {key: value for key, value in params.items() if value is not None}
            if params
            else None
        )

        response = await self.client.get(path, params=query)
        _ = response.raise_for_status()
        return response

    async def get(self, path: str, params: QueryParams = None) -> dict[str, object]:
        """
        Выполнить GET-запрос к MOEX ISS API.

        :param path: относительный путь (например, '/securities.json')
        :param params: query-параметры запроса
        :return: JSON-ответ, преобразованный в dict
        """

        logger.debug("GET %s params=%s", path, params)

        try:
            response = await self._execute_request(path, params)

        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            logger.error("HTTP %s error requesting %s", status_code, path)
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
            logger.error("Timeout requesting %s: %s", path, e)
            raise MoexTimeoutError(f"Timeout while accessing {path}: {e}") from e
        except httpx.RequestError as e:
            logger.error("Network error requesting %s: %s", path, e)
            raise MoexNetworkError(f"Network error accessing {path}: {e}") from e

        try:
            raw_data = cast(object, response.json())
        except ValueError as e:
            logger.error("Response parse error for %s: %s", path, e)
            raise MoexResponseParseError(
                f"Invalid JSON response for {path}: {e}"
            ) from e

        if not isinstance(raw_data, dict):
            logger.error(
                "Unexpected response format for %s: expected dict, got %s",
                path,
                type(raw_data).__name__,
            )
            raise MoexResponseParseError(
                f"Expected JSON object for {path}, got {type(raw_data).__name__}"
            )

        return cast(dict[str, object], raw_data)

    async def close(self) -> None:
        """Корректно закрываем HTTP-сессию."""
        await self.client.aclose()
