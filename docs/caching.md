# Кэширование

`pymoex` поддерживает встроенное кэширование запросов к MOEX ISS API.

По умолчанию используется `MemoryCache` - in-memory кэш с TTL, ограничением размера и защитой от Cache Stampede.

---

## Содержание

* [Как работает кэширование](#как-работает-кэширование)
* [`MemoryCache`](#memorycache)
* [Отключение кэша](#отключение-кэша)
* [Собственная реализация](#собственная-реализация)
* [`ICache`](#icache)

## Как работает кэширование

При повторном запросе одних и тех же данных `pymoex` может вернуть сохранённый результат без дополнительного обращения к MOEX ISS.

Встроенный `MemoryCache` использует:

* **TTL (Time to Live)** - определяет время жизни значения в кэше;
* **LRU (Least Recently Used)** - удаляет давно не использовавшиеся значения при достижении максимального размера;
* **Request Coalescing** - объединяет одновременно выполняемые одинаковые запросы.

Если несколько корутин одновременно запрашивают одни и те же данные, только первая выполняет запрос к MOEX ISS. Остальные ожидают его результат.

## `MemoryCache`

`MemoryCache` используется как стандартная реализация кэша и хранит данные в памяти текущего процесса.

Для большинства приложений дополнительная настройка не требуется:

```python
from pymoex import MoexClient

client = MoexClient(use_cache=True)
```

### Параметры

`MemoryCache` принимает два параметра:

| Параметр  | Тип   | По умолчанию | Описание                        |
| --------- | ----- | ------------ | ------------------------------- |
| `ttl`     | `int` | `60`         | Время жизни значения в секундах |
| `maxsize` | `int` | `1000`       | Максимальное количество записей |

Пример собственной конфигурации:

```python
from pymoex import MoexClient
from pymoex.core.cache import MemoryCache

cache = MemoryCache(ttl=120, maxsize=5000)

client = MoexClient(cache=cache)
```

При достижении `maxsize` удаляется запись, которая не использовалась дольше остальных.

> `MemoryCache` является локальным для процесса. Несколько процессов или экземпляров приложения не используют общее хранилище автоматически.

## Отключение кэша

Кэширование можно полностью отключить:

```python
from pymoex import MoexClient

client = MoexClient(use_cache=False)
```

В этом режиме используется `NullCache`: значения не сохраняются, а каждый запрос выполняется заново.

Это может быть полезно при отладке или когда необходимо всегда получать данные непосредственно из MOEX ISS.

## Собственная реализация

Для распределённых приложений можно подключить собственный backend кэширования.

Например, несколько экземпляров приложения могут использовать общее хранилище на базе Redis или Memcached вместо отдельных `MemoryCache`.

Для этого необходимо реализовать протокол `ICache` и передать экземпляр реализации в `MoexClient`:

```python
from pymoex import MoexClient
from my_project.adapters import RedisCache


async def main() -> None:
    cache = RedisCache(redis_url="redis://localhost:6379/0")

    async with MoexClient(cache=cache) as client:
        share = await client.share("SBER")
        print(share.short_name)
```

`RedisCache` в этом примере является пользовательской реализацией и не входит в `pymoex`.

> Для сохранения защиты от Cache Stampede собственная реализация должна корректно реализовывать семантику `get_or_set()`.

## `ICache`

Все реализации кэша должны соответствовать протоколу `ICache`:

```python
from collections.abc import Awaitable, Callable
from typing import Protocol


class ICache(Protocol):
    async def get(self, key: str) -> object | None: ...

    async def set(
        self,
        key: str,
        value: object,
        ttl: int | None = None,
    ) -> None: ...

    async def get_or_set[T](
        self,
        key: str,
        factory: Callable[[], Awaitable[T]],
        ttl: int | None = None,
    ) -> T: ...

    async def clear(self) -> None: ...
```

### Методы

| Метод                           | Описание                                                                           |
| ------------------------------- | ---------------------------------------------------------------------------------- |
| `get(key)`                      | Возвращает сохранённое значение или `None`, если значение отсутствует или устарело |
| `set(key, value, ttl)`          | Сохраняет значение с указанным TTL                                                 |
| `get_or_set(key, factory, ttl)` | Возвращает значение из кэша или получает его через `factory` и сохраняет           |
| `clear()`                       | Полностью очищает кэш                                                              |

Если `ttl=None`, реализация может использовать собственное значение TTL по умолчанию.

### `get_or_set()`

`get_or_set()` является основным методом для атомарного получения или создания кэшируемого значения.

`factory` - асинхронная функция, которая вызывается при отсутствии значения в кэше:

```python
async def load_share():
    return await fetch_share("SBER")


share = await cache.get_or_set(
    "share:SBER",
    load_share,
    ttl=60,
)
```

Для `MemoryCache` одновременно выполняемые вызовы `get_or_set()` с одинаковым ключом объединяются: `factory` выполняется один раз, а остальные вызовы ожидают тот же результат.
