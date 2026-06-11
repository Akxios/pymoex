# Обработка ошибок

`pymoex` использует собственные исключения, чтобы код приложения мог отдельно обрабатывать разные типы ошибок.

## Базовая иерархия

```text
MoexError
├── InstrumentNotFoundError
├── MoexAPIError
│   └── MoexResponseParseError
└── MoexNetworkError
    ├── MoexHTTPError
    │   ├── MoexBadRequestError
    │   ├── MoexAuthError
    │   ├── MoexNotFoundError
    │   ├── MoexRateLimitError
    │   └── MoexServerError
    └── MoexTimeoutError
```

---

## Основные исключения

| Исключение | Когда возникает |
|---|---|
| `InstrumentNotFoundError` | Инструмент не найден в ответе MOEX |
| `MoexBadRequestError` | HTTP 400 |
| `MoexAuthError` | HTTP 401 или 403 |
| `MoexNotFoundError` | HTTP 404 |
| `MoexRateLimitError` | HTTP 429 |
| `MoexServerError` | HTTP 5xx |
| `MoexHTTPError` | Другой HTTP-статус 4xx/5xx |
| `MoexTimeoutError` | Таймаут запроса |
| `MoexNetworkError` | Сетевая ошибка |
| `MoexResponseParseError` | Невалидный JSON или неожиданный формат ответа |
| `MoexAPIError` | Базовая ошибка API |
| `MoexError` | Базовая ошибка SDK |

---

## Пример обработки ошибки инструмента

```python
from pymoex import get_share
from pymoex.exceptions import InstrumentNotFoundError


try:
    share = get_share("UNKNOWN")
except InstrumentNotFoundError:
    print("Инструмент не найден")
```

---

## Пример общей обработки ошибок SDK

```python
from pymoex import get_share
from pymoex.exceptions import MoexError


try:
    share = get_share("SBER")
except MoexError as error:
    print(f"Ошибка pymoex: {error}")
```

---

## Рекомендуемый шаблон

Для пользовательских приложений обычно удобно обрабатывать:

```python
from pymoex import get_share
from pymoex.exceptions import (
    InstrumentNotFoundError,
    MoexNetworkError,
    MoexRateLimitError,
    MoexServerError,
    MoexError,
)


try:
    share = get_share("SBER")
except InstrumentNotFoundError:
    print("Инструмент не найден")
except MoexRateLimitError:
    print("Слишком много запросов к MOEX")
except MoexServerError:
    print("Ошибка на стороне MOEX")
except MoexNetworkError:
    print("Проблема с сетью")
except MoexError as error:
    print(f"Другая ошибка SDK: {error}")
```

---

## Async-пример

```python
import asyncio

from pymoex import MoexClient
from pymoex.exceptions import InstrumentNotFoundError, MoexError


async def main() -> None:
    async with MoexClient() as client:
        try:
            share = await client.share("SBER")
            print(share)
        except InstrumentNotFoundError:
            print("Акция не найдена")
        except MoexError as error:
            print(f"Ошибка pymoex: {error}")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Retry

Клиент автоматически повторяет запросы при:

- сетевых ошибках;
- таймаутах;
- HTTP 500, 502, 503, 504.

Количество попыток и задержки настраиваются через `MOEX_RETRY_*`.

Подробнее: [Конфигурация](../docs/configuration.md).
