# pyright: reportPrivateUsage=false, reportUnknownArgumentType=false, reportUnknownLambdaType=false, reportUnknownMemberType=false

from collections.abc import Iterator
from itertools import chain, repeat

import pytest

from pymoex.core.config import MoexSettings
from pymoex.core.session import MoexSession


@pytest.mark.asyncio
async def test_apply_rate_limit_uses_jitter(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Проверка: rate limit учитывает базовую задержку и jitter.

    Было:
    - последний запрос в 10.0;
    - текущий момент 10.02;
    - delay = 0.1;
    - jitter = 0.03.

    Нужно ждать:
    target_delay - elapsed = (0.1 + 0.03) - 0.02 = 0.11.
    """
    settings = MoexSettings(
        request_delay=0.1,
        request_jitter=0.05,
    )
    session = MoexSession(settings=settings)
    session._last_request_time = 10.0

    sleep_calls: list[float] = []

    async def fake_sleep(seconds: float) -> None:
        sleep_calls.append(seconds)

    time_values: Iterator[float] = chain([10.02, 10.12], repeat(10.12))

    monkeypatch.setattr("pymoex.core.session.random.uniform", lambda a, b: 0.03)
    monkeypatch.setattr("pymoex.core.session.time.monotonic", lambda: next(time_values))
    monkeypatch.setattr("pymoex.core.session.asyncio.sleep", fake_sleep)

    try:
        await session._apply_rate_limit()

        assert sleep_calls == [pytest.approx(0.11)]
        assert session._last_request_time == pytest.approx(10.12)
    finally:
        await session.close()


@pytest.mark.asyncio
async def test_apply_rate_limit_allows_zero_jitter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Проверка: если jitter = 0, random.uniform не вызывается.

    Было:
    - последний запрос в 20.0;
    - текущий момент 20.02;
    - delay = 0.1;
    - jitter = 0.

    Нужно ждать:
    0.1 - 0.02 = 0.08.
    """
    settings = MoexSettings(
        request_delay=0.1,
        request_jitter=0,
    )
    session = MoexSession(settings=settings)
    session._last_request_time = 20.0

    sleep_calls: list[float] = []

    async def fake_sleep(seconds: float) -> None:
        sleep_calls.append(seconds)

    def fail_uniform(_start: float, _stop: float) -> float:
        raise AssertionError("random.uniform should not be called when jitter=0")

    time_values: Iterator[float] = chain([20.02, 20.10], repeat(20.10))

    monkeypatch.setattr("pymoex.core.session.random.uniform", fail_uniform)
    monkeypatch.setattr("pymoex.core.session.time.monotonic", lambda: next(time_values))
    monkeypatch.setattr("pymoex.core.session.asyncio.sleep", fake_sleep)

    try:
        await session._apply_rate_limit()

        assert sleep_calls == [pytest.approx(0.08)]
        assert session._last_request_time == pytest.approx(20.10)
    finally:
        await session.close()


@pytest.mark.asyncio
async def test_apply_rate_limit_does_not_sleep_when_delay_already_elapsed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Проверка: если с прошлого запроса прошло достаточно времени, sleep не вызывается.
    """
    settings = MoexSettings(
        request_delay=0.1,
        request_jitter=0,
    )
    session = MoexSession(settings=settings)
    session._last_request_time = 30.0

    sleep_calls: list[float] = []

    async def fake_sleep(seconds: float) -> None:
        sleep_calls.append(seconds)

    time_values: Iterator[float] = chain([30.2, 30.2], repeat(30.2))

    monkeypatch.setattr("pymoex.core.session.asyncio.sleep", fake_sleep)
    monkeypatch.setattr("pymoex.core.session.time.monotonic", lambda: next(time_values))

    try:
        await session._apply_rate_limit()

        assert sleep_calls == []
        assert session._last_request_time == pytest.approx(30.2)
    finally:
        await session.close()


@pytest.mark.asyncio
async def test_apply_rate_limit_returns_immediately_when_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Проверка: если delay <= 0 и jitter <= 0, rate limit полностью отключён.
    """
    settings = MoexSettings(
        request_delay=0,
        request_jitter=0,
    )
    session = MoexSession(settings=settings)
    session._last_request_time = 40.0

    async def fail_sleep(_seconds: float) -> None:
        raise AssertionError(
            "asyncio.sleep should not be called when rate limit is disabled"
        )

    monkeypatch.setattr("pymoex.core.session.asyncio.sleep", fail_sleep)

    try:
        await session._apply_rate_limit()

        assert session._last_request_time == pytest.approx(40.0)
    finally:
        await session.close()


@pytest.mark.asyncio
async def test_apply_rate_limit_uses_jitter_even_when_delay_is_zero(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Проверка: если delay = 0, но jitter > 0, задержка всё равно применяется.
    """
    settings = MoexSettings(
        request_delay=0,
        request_jitter=0.05,
    )
    session = MoexSession(settings=settings)
    session._last_request_time = 50.0

    sleep_calls: list[float] = []

    async def fake_sleep(seconds: float) -> None:
        sleep_calls.append(seconds)

    time_values: Iterator[float] = chain([50.01, 50.05], repeat(50.05))

    monkeypatch.setattr("pymoex.core.session.random.uniform", lambda a, b: 0.03)
    monkeypatch.setattr("pymoex.core.session.time.monotonic", lambda: next(time_values))
    monkeypatch.setattr("pymoex.core.session.asyncio.sleep", fake_sleep)

    try:
        await session._apply_rate_limit()

        assert sleep_calls == [pytest.approx(0.02)]
        assert session._last_request_time == pytest.approx(50.05)
    finally:
        await session.close()
