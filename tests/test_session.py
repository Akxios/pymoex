import httpx
import pytest
import respx

from pymoex.core.session import MoexSession
from pymoex.exceptions import (
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


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status_code", "exc_type"),
    [
        (400, MoexBadRequestError),
        (401, MoexAuthError),
        (403, MoexAuthError),
        (404, MoexNotFoundError),
        (418, MoexHTTPError),
        (429, MoexRateLimitError),
        (500, MoexServerError),
        (503, MoexServerError),
    ],
)
async def test_session_maps_http_status_to_specific_exception(status_code, exc_type):
    session = MoexSession()
    try:
        with respx.mock:
            respx.get("https://iss.moex.com/iss/fail.json").mock(
                return_value=httpx.Response(status_code)
            )

            with pytest.raises(exc_type):
                await session.get("/fail.json")
    finally:
        await session.close()


@pytest.mark.asyncio
async def test_session_maps_timeout_to_moex_timeout_error():
    session = MoexSession()
    try:
        with respx.mock:
            request = httpx.Request("GET", "https://iss.moex.com/iss/timeout.json")
            respx.get("https://iss.moex.com/iss/timeout.json").mock(
                side_effect=httpx.ReadTimeout("boom", request=request)
            )

            with pytest.raises(MoexTimeoutError):
                await session.get("/timeout.json")
    finally:
        await session.close()


@pytest.mark.asyncio
async def test_session_maps_request_error_to_moex_network_error():
    session = MoexSession()
    try:
        with respx.mock:
            request = httpx.Request("GET", "https://iss.moex.com/iss/network.json")
            respx.get("https://iss.moex.com/iss/network.json").mock(
                side_effect=httpx.ConnectError("boom", request=request)
            )

            with pytest.raises(MoexNetworkError):
                await session.get("/network.json")
    finally:
        await session.close()


@pytest.mark.asyncio
async def test_session_maps_json_decode_to_response_parse_error():
    session = MoexSession()
    try:
        with respx.mock:
            respx.get("https://iss.moex.com/iss/bad-json.json").mock(
                return_value=httpx.Response(200, text="not-json")
            )

            with pytest.raises(MoexResponseParseError):
                await session.get("/bad-json.json")
    finally:
        await session.close()
