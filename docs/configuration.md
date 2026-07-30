# Конфигурация

`pymoex` использует настройки `MoexSettings`.

Настройки могут подхватываться:

- из переменных окружения;
- из файла `.env`;
- через явное создание `MoexSettings`.

Все переменные окружения используют префикс `MOEX_`.

## Основные переменные окружения

| Переменная | Описание | Значение по умолчанию |
|---|---|---|
| `MOEX_BASE_URL` | Базовый URL MOEX ISS API | `https://iss.moex.com/iss` |
| `MOEX_TIMEOUT` | Таймаут HTTP-запросов в секундах | `10.0` |
| `MOEX_USER_AGENT` | User-Agent клиента | `pymoex-sdk/0.1.9` |
| `MOEX_LOG_LEVEL` | Уровень логирования | `WARNING` |
| `MOEX_REQUEST_DELAY` | Базовая задержка между запросами | `0.05` |
| `MOEX_REQUEST_JITTER` | Случайная добавка к задержке | `0.5` |
| `MOEX_RETRY_ATTEMPTS` | Количество попыток запроса | `3` |
| `MOEX_RETRY_MIN_WAIT` | Минимальная пауза между retry | `1` |
| `MOEX_RETRY_MAX_WAIT` | Максимальная пауза между retry | `10` |

## Rate limit

`MOEX_REQUEST_DELAY` задаёт базовую задержку между HTTP-запросами.

```env
MOEX_REQUEST_DELAY=0.1
```

`MOEX_REQUEST_JITTER` добавляет случайную задержку.

```env
MOEX_REQUEST_JITTER=0.5
```

Это помогает не отправлять запросы слишком ровно и часто.

## Отключение задержки

Для тестов или локальной отладки можно отключить задержки:

```env
MOEX_REQUEST_DELAY=0
MOEX_REQUEST_JITTER=0
```

В обычном использовании лучше оставлять небольшую задержку.

## Retry

Клиент повторяет запросы при временных сетевых ошибках и ошибках MOEX 5xx.

```env
MOEX_RETRY_ATTEMPTS=3
MOEX_RETRY_MIN_WAIT=1
MOEX_RETRY_MAX_WAIT=10
```

## Настройка через код

Можно создать `MoexSettings` вручную и передать его в `MoexSession`.

```python
import asyncio

from pymoex.client import MoexClient
from pymoex.core.config import MoexSettings
from pymoex.core.session import MoexSession


async def main() -> None:
    settings = MoexSettings(
        timeout=15,
        request_delay=0.1,
        request_jitter=0,
    )

    session = MoexSession(settings=settings)

    async with MoexClient(session=session) as client:
        share = await client.share("SBER")
        print(share)


if __name__ == "__main__":
    asyncio.run(main())
```

## Preferred boards

Клиент выбирает подходящий режим торгов на основе приоритетов.

По умолчанию:

```python
preferred_share_boards = ["TQBR", "TQTF", "FQBR", "TQTD"]
preferred_bond_boards = ["TQOB", "TQCB", "TQOD", "TQIR"]
preferred_currency_boards = ["CETS", "CNGD", "SNDX"]
```

Пример изменения через код:

```python
settings = MoexSettings(
    preferred_share_boards=["TQBR", "TQTF"],
    preferred_bond_boards=["TQOB"],
    preferred_currency_boards=["CETS"],
)
```