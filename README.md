# pymoex

[![Tests](https://github.com/Akxios/pymoex/actions/workflows/tests.yml/badge.svg)](https://github.com/Akxios/pymoex/actions/workflows/tests.yml)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/)
![Lint](https://img.shields.io/badge/lint-ruff-red)
![Type Checked](https://img.shields.io/badge/type--checked-basedpyright-blue)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

`pymoex` — типизированный Python SDK для работы с MOEX ISS API.

Библиотека предоставляет асинхронный клиент, синхронную обёртку, поиск инструментов, получение данных по акциям, облигациям, валютам, дивидендам, купонам и амортизациям.

---

## 📚 Документация по API

Для удобства разработки я подготовил подробные справочники полей, которые возвращает библиотека `pymoex` из MOEX ISS:

- **[Командная строка (CLI)](docs/cli.md)** - Быстрое взаимодействие с библиотекой.
- **[Конфигурация .env](docs/configuration.md)** - Описание полей окружения библиотеки.
- **[Исключения](docs/errors.md)** - Обработка исключений
- **[Справочник по облигациям](docs/bonds.md)** - НКД, доходность, оферты и купоны.
- **[Справочник по акциям](docs/shares.md)** - Дивиденды, лотность и капитализация.
- **[Справочник по поиску](docs/search.md)** - Глобальный поиск по тикеру, ISIN и эмитенту.

---

## Возможности

- Асинхронный API на базе `httpx` и `asyncio`
- Синхронный API для простых скриптов
- Pydantic-модели для ответов MOEX ISS
- Поиск акций, облигаций, фондов и валют
- Получение дивидендов, купонов и амортизаций
- In-memory кэш с TTL и защитой от одинаковых параллельных запросов
- Настройка через переменные окружения `MOEX_*`

---

## Установка

Требуется Python 3.12+.

Через [uv](https://github.com/astral-sh/uv) (рекомендуется):
```bash
uv add https://github.com/Akxios/pymoex.git
```

Через pip:
```bash
pip install https://github.com/Akxios/pymoex.git
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

## 🧠 Кэширование

Библиотека имеет встроенную продвинутую систему кэширования с защитой от **Cache Stampede** (Request Coalescing). Это означает, что если 1000 пользователей одновременно запросят данные по одной акции, библиотека сделает **только один** запрос к бирже.

### Режимы работы

#### 1. In-Memory (по умолчанию): Используется быстрый MemoryCache внутри процесса.
Для большинства проектов ничего настраивать не нужно. Библиотека использует быстрый кэш в памяти.

```python
client = MoexClient(use_cache=True)
```

#### 2. Отключение кэша: Прямые запросы к API без сохранения данных.
Полезно для отладки или если вам нужны гарантированно свежие данные каждое мгновение.
```python
client = MoexClient(use_cache=False)

```

#### 3. Внешний кэш (Redis / Memcached): Вы можете подключить любое внешнее хранилище, передав объект, реализующий интерфейс ICache.

Для продакшена и распределенных систем (например, бот запущен в нескольких Docker-контейнерах) вы можете подключить любой внешний кэш.

Для этого нужно реализовать интерфейс ICache. Пример для Redis:
```python
from pymoex import MoexClient
from my_project.adapters import RedisCache # Ваша реализация ICache

async def main():
    cache = RedisCache(redis_url="redis://localhost:6379/0")
    
    async with MoexClient(cache=cache) as client:
        share = await client.share("SBER")
```

---

## Примеры
```bash
uv run python -m examples.async_usage
uv run python -m examples.sync_usage
uv run python -m examples.benchmark
```

---

## Разработка
```bash
uv sync --group dev
uv run pytest tests/ -v
uv run ruff check .
uv run ruff format .
```

---

## 🛠 Структура проекта
- pymoex/client.py: Точка входа, класс MoexClient.
- pymoex/services/: Логика работы с конкретными типами инструментов.
- pymoex/models/: Pydantic-модели ответов.
- pymoex/core/: Базовые компоненты (сессия, кеш, конфиг).
- pymoex/cli/: CLI.
- pymoex/utils/: Утилиты для работоспособности.
- docs/: Документация библиотеки.
- tests/: Тесты.
- examples/: Примеры кода.

---

## 📄 Лицензия
Проект распространяется под лицензией MIT.
