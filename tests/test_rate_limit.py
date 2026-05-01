from itertools import chain, repeat

import pytest

from pymoex.core.session import MoexSession


@pytest.mark.asyncio
async def test_apply_rate_limit_uses_jitter(monkeypatch):
    session = MoexSession()
    session.settings.request_delay = 0.1
    session.settings.request_jitter = 0.05
    session._last_request_time = 10.0

    sleep_calls = []

    async def fake_sleep(seconds: float):
        sleep_calls.append(seconds)

    time_values = chain([10.02, 10.12], repeat(10.12))

    monkeypatch.setattr("pymoex.core.session.random.uniform", lambda a, b: 0.03)
    monkeypatch.setattr("pymoex.core.session.time.monotonic", lambda: next(time_values))
    monkeypatch.setattr("pymoex.core.session.asyncio.sleep", fake_sleep)

    await session._apply_rate_limit()

    assert sleep_calls == [pytest.approx(0.11)]
    assert session._last_request_time == pytest.approx(10.12)

    await session.close()


@pytest.mark.asyncio
async def test_apply_rate_limit_allows_zero_jitter(monkeypatch):
    session = MoexSession()
    session.settings.request_delay = 0.1
    session.settings.request_jitter = 0
    session._last_request_time = 20.0

    sleep_calls = []

    async def fake_sleep(seconds: float):
        sleep_calls.append(seconds)

    time_values = chain([20.02, 20.10], repeat(20.10))

    def fail_uniform(*_args, **_kwargs):
        raise AssertionError("random.uniform should not be called when jitter=0")

    monkeypatch.setattr("pymoex.core.session.random.uniform", fail_uniform)
    monkeypatch.setattr("pymoex.core.session.time.monotonic", lambda: next(time_values))
    monkeypatch.setattr("pymoex.core.session.asyncio.sleep", fake_sleep)

    await session._apply_rate_limit()

    assert sleep_calls == [pytest.approx(0.08)]
    assert session._last_request_time == pytest.approx(20.10)

    await session.close()
