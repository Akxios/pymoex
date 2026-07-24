import asyncio

import pytest

from pymoex.core.cache import MemoryCache, NullCache


@pytest.mark.asyncio
async def test_null_cache_get_always_returns_none() -> None:
    """
    NullCache ничего не хранит.

    Даже если вызвать set(), get() всё равно должен вернуть None.
    """
    cache = NullCache()

    await cache.set("key", "value")

    assert await cache.get("key") is None


@pytest.mark.asyncio
async def test_null_cache_always_calls_factory() -> None:
    """
    NullCache не кэширует результат get_or_set().

    Поэтому factory вызывается каждый раз.
    """
    cache = NullCache()
    calls = 0

    async def factory() -> str:
        nonlocal calls
        calls += 1
        return "data"

    first = await cache.get_or_set("key", factory)
    second = await cache.get_or_set("key", factory)

    assert first == "data"
    assert second == "data"
    assert calls == 2


@pytest.mark.asyncio
async def test_memory_cache_get_and_set() -> None:
    """
    MemoryCache должен сохранять значение через set()
    и возвращать его через get().
    """
    cache = MemoryCache()

    await cache.set("key", "value")

    assert await cache.get("key") == "value"


@pytest.mark.asyncio
async def test_memory_cache_get_or_set_caches_value() -> None:
    """
    get_or_set() должен вызвать factory только один раз.

    Второй вызов с тем же ключом должен вернуть значение из кэша.
    """
    cache = MemoryCache()
    calls = 0

    async def factory() -> str:
        nonlocal calls
        calls += 1
        return "cached-data"

    first = await cache.get_or_set("key", factory)
    second = await cache.get_or_set("key", factory)

    assert first == "cached-data"
    assert second == "cached-data"
    assert calls == 1


@pytest.mark.asyncio
async def test_memory_cache_ttl_expiration(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Значение должно исчезать после истечения TTL.
    """
    current_time = 100.0

    monkeypatch.setattr("pymoex.core.cache._now", lambda: current_time)

    cache = MemoryCache(ttl=10)

    await cache.set("key", "value")

    assert await cache.get("key") == "value"

    current_time = 111.0

    assert await cache.get("key") is None


@pytest.mark.asyncio
async def test_memory_cache_custom_ttl_overrides_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    TTL из set(..., ttl=...) должен переопределять дефолтный TTL кэша.
    """
    current_time = 100.0

    monkeypatch.setattr("pymoex.core.cache._now", lambda: current_time)

    cache = MemoryCache(ttl=60)

    await cache.set("key", "value", ttl=5)

    current_time = 104.0
    assert await cache.get("key") == "value"

    current_time = 106.0
    assert await cache.get("key") is None


@pytest.mark.asyncio
async def test_memory_cache_lru_eviction() -> None:
    """
    MemoryCache должен вытеснять самый давно использованный ключ.

    Сценарий:
    - кладём A и B;
    - читаем A, чтобы сделать его недавно использованным;
    - кладём C;
    - B должен быть вытеснен.
    """
    cache = MemoryCache(maxsize=2)

    await cache.set("A", 1)
    await cache.set("B", 2)

    assert await cache.get("A") == 1

    await cache.set("C", 3)

    assert await cache.get("A") == 1
    assert await cache.get("B") is None
    assert await cache.get("C") == 3


def test_memory_cache_rejects_non_positive_maxsize() -> None:
    with pytest.raises(ValueError, match="maxsize must be greater than zero"):
        _ = MemoryCache(maxsize=0)


@pytest.mark.asyncio
async def test_memory_cache_clear_removes_values() -> None:
    """
    clear() должен полностью очищать сохранённые значения.
    """
    cache = MemoryCache()

    await cache.set("A", 1)
    await cache.set("B", 2)

    await cache.clear()

    assert await cache.get("A") is None
    assert await cache.get("B") is None


@pytest.mark.asyncio
async def test_memory_cache_cancellation_unblocks_waiters() -> None:
    cache = MemoryCache()
    factory_started = asyncio.Event()
    release_factory = asyncio.Event()

    async def slow_factory() -> str:
        _ = factory_started.set()
        _ = await release_factory.wait()
        return "loaded"

    initiator = asyncio.create_task(cache.get_or_set("key", slow_factory))
    _ = await factory_started.wait()
    waiter = asyncio.create_task(cache.get_or_set("key", slow_factory))
    await asyncio.sleep(0)

    _ = initiator.cancel()

    with pytest.raises(asyncio.CancelledError):
        _ = await initiator
    with pytest.raises(asyncio.CancelledError):
        _ = await waiter

    async def replacement_factory() -> str:
        return "replacement"

    assert await cache.get_or_set("key", replacement_factory) == "replacement"


@pytest.mark.asyncio
async def test_memory_cache_coalescing() -> None:
    """
    Проверка защиты от Cache Stampede.

    Если много запросов одновременно просят один ключ,
    factory должен выполниться только один раз.
    """
    cache = MemoryCache()
    factory_calls = 0

    async def slow_factory() -> str:
        nonlocal factory_calls
        factory_calls += 1
        await asyncio.sleep(0.01)
        return "heavy_data"

    tasks = [cache.get_or_set("heavy_key", slow_factory) for _ in range(100)]

    results = await asyncio.gather(*tasks)

    assert results == ["heavy_data"] * 100
    assert factory_calls == 1


@pytest.mark.asyncio
async def test_memory_cache_factory_error_propagates_to_waiters() -> None:
    """
    Если factory падает, все ожидающие запросы должны получить ту же ошибку.
    """
    cache = MemoryCache()
    factory_calls = 0

    async def failing_factory() -> str:
        nonlocal factory_calls
        factory_calls += 1
        await asyncio.sleep(0.01)
        raise ValueError("Network Down")

    tasks = [cache.get_or_set("bad_key", failing_factory) for _ in range(5)]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    assert factory_calls == 1

    for result in results:
        assert isinstance(result, ValueError)
        assert str(result) == "Network Down"


@pytest.mark.asyncio
async def test_memory_cache_retries_factory_after_error() -> None:
    """
    После ошибки factory ключ должен быть удалён из pending.

    Проверяем это не через приватное поле _pending, а через поведение:
    следующий вызов должен снова запустить factory.
    """
    cache = MemoryCache()
    factory_calls = 0

    async def failing_factory() -> str:
        nonlocal factory_calls
        factory_calls += 1
        raise ValueError("Network Down")

    with pytest.raises(ValueError, match="Network Down"):
        _ = await cache.get_or_set("bad_key", failing_factory)

    with pytest.raises(ValueError, match="Network Down"):
        _ = await cache.get_or_set("bad_key", failing_factory)

    assert factory_calls == 2
