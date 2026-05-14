import httpx
import pytest
from httpx import Response

from pymoex.core.config import MoexSettings
from pymoex.core.session import MoexSession
from pymoex.exceptions import (
    MoexAuthError,
    MoexBadRequestError,
    MoexNetworkError,
    MoexNotFoundError,
    MoexRateLimitError,
    MoexResponseParseError,
    MoexServerError,
    MoexTimeoutError,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status_code", "expected_exception"),
    [
        (400, MoexBadRequestError),
        (401, MoexAuthError),
        (403, MoexAuthError),
        (404, MoexNotFoundError),
        (429, MoexRateLimitError),
        (500, MoexServerError),
        (502, MoexServerError),
        (503, MoexServerError),
        (504, MoexServerError),
    ],
)
async def test_session_maps_http_errors(
    mock_moex,
    status_code: int,
    expected_exception: type[Exception],
) -> None:
    """
    Проверка: HTTP-статусы мапятся в доменные исключения SDK.

    retry_attempts=1 нужен, чтобы 5xx не повторялись несколько раз
    в этом конкретном тесте. Здесь проверяем именно маппинг ошибок,
    а не retry-механику.
    """
    settings = MoexSettings(
        retry_attempts=1,
        retry_min_wait=0,
        retry_max_wait=0,
        request_delay=0,
        request_jitter=0,
    )

    async with MoexSession(settings=settings) as session:
        route = mock_moex.get("/test.json").mock(
            return_value=Response(status_code, json={"error": "boom"})
        )

        with pytest.raises(expected_exception):
            await session.get("/test.json")

        assert route.call_count == 1


@pytest.mark.asyncio
async def test_session_returns_dict_json(mock_moex) -> None:
    """
    Проверка: успешный JSON-объект возвращается как dict.
    """
    settings = MoexSettings(
        request_delay=0,
        request_jitter=0,
    )

    async with MoexSession(settings=settings) as session:
        route = mock_moex.get("/test.json").mock(
            return_value=Response(200, json={"data": "ok"})
        )

        result = await session.get("/test.json")

        assert result == {"data": "ok"}
        assert route.call_count == 1


@pytest.mark.asyncio
async def test_session_removes_none_from_params(mock_moex) -> None:
    """
    Проверка: параметры со значением None не должны улетать в запрос.
    """
    settings = MoexSettings(
        request_delay=0,
        request_jitter=0,
    )

    async with MoexSession(settings=settings) as session:
        route = mock_moex.get("/test.json").mock(
            return_value=Response(200, json={"data": "ok"})
        )

        await session.get(
            "/test.json",
            params={
                "iss.meta": "off",
                "limit": None,
                "start": 0,
            },
        )

        request = route.calls.last.request
        url = str(request.url)

        assert "iss.meta=off" in url
        assert "start=0" in url
        assert "limit" not in url


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "invalid_json_body",
    [
        "",
        "Just text",
    ],
)
async def test_session_invalid_json_raises_parse_error(
    mock_moex,
    invalid_json_body: str,
) -> None:
    """
    Проверка: если тело ответа невалидный JSON, кидаем MoexResponseParseError.
    """
    settings = MoexSettings(
        request_delay=0,
        request_jitter=0,
    )

    async with MoexSession(settings=settings) as session:
        route = mock_moex.get("/invalid.json").mock(
            return_value=Response(200, content=invalid_json_body.encode())
        )

        with pytest.raises(MoexResponseParseError):
            await session.get("/invalid.json")

        assert route.call_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "json_body",
    [
        [],
        [1, 2, 3],
        "text",
        123,
        None,
    ],
)
async def test_session_non_dict_json_raises_parse_error(
    mock_moex,
    json_body: object,
) -> None:
    """
    Проверка: если JSON валидный, но это не объект/dict,
    кидаем MoexResponseParseError.
    """
    settings = MoexSettings(
        request_delay=0,
        request_jitter=0,
    )

    async with MoexSession(settings=settings) as session:
        route = mock_moex.get("/non-dict.json").mock(
            return_value=Response(200, json=json_body)
        )

        with pytest.raises(MoexResponseParseError):
            await session.get("/non-dict.json")

        assert route.call_count == 1


@pytest.mark.asyncio
async def test_session_retries_5xx_errors(mock_moex) -> None:
    """
    Проверка: 5xx ошибки повторяются согласно retry_attempts.
    """
    settings = MoexSettings(
        retry_attempts=3,
        retry_min_wait=0,
        retry_max_wait=0,
        request_delay=0,
        request_jitter=0,
    )

    async with MoexSession(settings=settings) as session:
        route = mock_moex.get("/server-error.json").mock(
            return_value=Response(500, json={"error": "server error"})
        )

        with pytest.raises(MoexServerError):
            await session.get("/server-error.json")

        assert route.call_count == 3


@pytest.mark.asyncio
async def test_session_retries_then_succeeds(mock_moex) -> None:
    """
    Проверка: если первый запрос вернул 500, а второй 200,
    session.get() возвращает успешный JSON.
    """
    settings = MoexSettings(
        retry_attempts=3,
        retry_min_wait=0,
        retry_max_wait=0,
        request_delay=0,
        request_jitter=0,
    )

    async with MoexSession(settings=settings) as session:
        route = mock_moex.get("/unstable.json").mock(
            side_effect=[
                Response(500, json={"error": "temporary"}),
                Response(200, json={"data": "ok"}),
            ]
        )

        result = await session.get("/unstable.json")

        assert result == {"data": "ok"}
        assert route.call_count == 2


@pytest.mark.asyncio
async def test_session_timeout_error_is_mapped(mock_moex) -> None:
    """
    Проверка: httpx.TimeoutException превращается в MoexTimeoutError.
    """
    settings = MoexSettings(
        retry_attempts=1,
        request_delay=0,
        request_jitter=0,
    )

    async with MoexSession(settings=settings) as session:
        route = mock_moex.get("/timeout.json").mock(
            side_effect=httpx.ReadTimeout("timeout")
        )

        with pytest.raises(MoexTimeoutError):
            await session.get("/timeout.json")

        assert route.call_count == 1


@pytest.mark.asyncio
async def test_session_network_error_is_mapped(mock_moex) -> None:
    """
    Проверка: httpx.RequestError превращается в MoexNetworkError.
    """
    settings = MoexSettings(
        retry_attempts=1,
        request_delay=0,
        request_jitter=0,
    )

    async with MoexSession(settings=settings) as session:
        route = mock_moex.get("/network.json").mock(
            side_effect=httpx.ConnectError("network error")
        )

        with pytest.raises(MoexNetworkError):
            await session.get("/network.json")

        assert route.call_count == 1
