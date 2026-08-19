# pymoex

[![Tests](https://github.com/Akxios/pymoex/actions/workflows/ci.yml/badge.svg)](https://github.com/Akxios/pymoex/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

`pymoex` — типизированный Python SDK для работы с MOEX ISS API.

Предоставляет асинхронный и синхронный API для получения данных об акциях, облигациях, валютах, дивидендах, купонах и амортизациях, а также поиска финансовых инструментов.

---

## Документация

Полная документация доступна в [`docs/`](docs/README.md).

- [Быстрый старт](#быстрый-старт)
- [Конфигурация](docs/configuration.md)
- [Кэширование](docs/caching.md)
- [Обработка ошибок](docs/errors.md)
- [Акции](docs/shares.md)
- [Облигации](docs/bonds.md)
- [Поиск инструментов](docs/search.md)
- [CLI](docs/cli.md)

---

## Возможности

- Асинхронный API на базе `httpx` и `asyncio`
- Синхронный API для простых скриптов
- Типизированные Pydantic-модели для ответов MOEX ISS
- Поиск акций, облигаций, фондов и валют
- Получение дивидендов, купонов и амортизаций
- In-memory кэш с TTL и защитой от одинаковых параллельных запросов
- Опциональный CLI для работы с MOEX из терминала
- Настройка через переменные окружения `MOEX_*`

---

## Установка

Требуется Python 3.12+.

### SDK

Если нужен только Python API без CLI-зависимостей:

Через [uv](https://github.com/astral-sh/uv) (рекомендуется):

```bash
uv add https://github.com/Akxios/pymoex.git
```

Через pip:

```bash
pip install https://github.com/Akxios/pymoex.git
```

### SDK + CLI

Для установки SDK вместе с командным интерфейсом:

Через [uv](https://github.com/astral-sh/uv) (рекомендуется):

```bash
uv add "pymoex[cli] @ git+https://github.com/Akxios/pymoex.git"
```

Через pip:

```bash
pip install "pymoex[cli] @ git+https://github.com/Akxios/pymoex.git"
```

После установки CLI доступна команда:

```bash
moex --help
```

---

## Быстрый старт

### Async API

```python
import asyncio

from pymoex import MoexClient


async def main() -> None:
    async with MoexClient() as client:
        share = await client.share("SBER")
        bond = await client.bond("SU26238RMFS4")
        results = await client.find("Сбербанк")

        print(share.short_name, share.last_price)
        print(bond.short_name, bond.effective_yield)
        print(results[:3])


if __name__ == "__main__":
    asyncio.run(main())
```

### Sync API

```python
from pymoex import get_bond, get_share


share = get_share("SBER")
bond = get_bond("SU26238RMFS4")

print(share.short_name, share.last_price)
print(bond.short_name, bond.effective_yield)
```

---

## Кэширование

`pymoex` поддерживает встроенный in-memory кэш с TTL и защитой от Cache Stampede (Request Coalescing). Одновременные одинаковые запросы объединяются, уменьшая количество обращений к MOEX ISS.

По умолчанию кэш включён:

```python
client = MoexClient(use_cache=True)
```

Кэш можно отключить:

```python
client = MoexClient(use_cache=False)
```

Для распределённых приложений можно использовать собственный backend, реализующий интерфейс `ICache`.

Подробнее: [Кэширование](docs/caching.md).

---

## Примеры

```bash
uv run python -m examples.async_usage
uv run python -m examples.sync_usage
uv run python -m examples.benchmark
```

---

## Разработка

Установка зависимостей:

```bash
uv sync --all-extras --dev
```

Запуск проверок:

```bash
uv run pytest tests/ -v
uv run ruff format --check .
uv run ruff check .
uv run basedpyright
```

Форматирование:

```bash
uv run ruff format .
```

---

## Лицензия

Проект распространяется под лицензией MIT.
