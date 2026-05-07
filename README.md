# pymoex

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Tests](https://github.com/Akxios/pymoex/actions/workflows/tests.yml/badge.svg)](https://github.com/Akxios/pymoex/actions/workflows/tests.yml)

pymoex - это современная, быстрая и типизированная асинхронная библиотека для взаимодействия с Московской Биржей (MOEX ISS API).

Библиотека написана на **Python 3.12**, использует **Pydantic** для валидации данных и **HTTPX** для сетевых запросов. Включает в себя продвинитую систему кэширования и автоматический выбор наиболее ликвидного режима торгов.

---

## 📚 Документация по API

Для удобства разработки я подготовил подробные справочники полей, которые возвращает библиотека `pymoex` из MOEX ISS:

* 📈 **[Справочник по облигациям](docs/bonds.md)** — НКД, доходность, оферты и купоны.
* 📊 **[Справочник по акциям](docs/shares.md)** — Дивиденды, лотность и капитализация.
* 🔍 **[Справочник по поиску](docs/search.md)** — Глобальный поиск по тикеру, ISIN и эмитенту.

## ✨ Особенности
- 🚀 **Полная асинхронность:** Построена на базе httpx и asyncio.
- 🛡️ **Строгая типизация:** Все ответы API валидируются и преобразуются в удобные Pydantic-модели (Share, Bond, Search).
- 🧠 **Умное кэширование:** Встроенный TTLCache с поддержкой Request Coalescing (защита от Cache Stampede — одновременные одинаковые запросы выполняются как один HTTP-запрос).
- 🎯 **Авто-выбор режима торгов:** Библиотека сама находит актуальный BOARDID (например, TQBR для акций), проверяя активность торгов, чтобы вам не пришлось указывать его вручную.
- 🔄 **Sync Wrapper:** Поддержка синхронного вызова методов для простых скриптов или работы в консоли (через pymoex.api).
- ⚙️ **Конфигурация:** Удобная настройка через переменные окружения.
- 🔍 **Удобный поиск:** Поиск инструментов по тикеру, названию или ISIN.

---

## 📦 Установка
Требуется **Python 3.12** или выше.
Через pip:
```bash
pip install https://github.com/Akxios/pymoex.git
```
Через [uv](https://github.com/astral-sh/uv) (рекомендуется):
```bash
uv add https://github.com/Akxios/pymoex.git
```

---

## 🚀 Быстрый старт
### Асинхронный режим
Шаблон для начала работы:
```python
import asyncio

from pymoex import MoexClient


async def main():
    async with MoexClient() as client:
        # Получаем акцию
        share = await client.share("SBER")
        print("Share:", share)  # Выводим результат

        # Получаем облигацию
        bond = await client.bond("RU000A10DS74")
        print(bond)  # Выводим результат

        # Выполняем поиск по ключевому слову
        results = await client.find(
            "Сбербанк", instrument_type="share"
        )  # instrument_type="bond"

        for r in results:
            print(r)  # Выводим результат


if __name__ == "__main__":
    asyncio.run(main())
```

### Синхронный режим
Шаблон для начала работы:
```python
from pymoex import find, get_bond, get_share


def main():

    # Получаем акцию
    share = get_share("SBER")
    print(share)  # Выводим результат

    # Получаем облигацию
    bond = get_bond("RU000A10DS74")
    print(bond)  # Выводим результат

    # Выполняем поиск по ключевому слову
    results = find("Сбербанк", instrument_type="share")  # instrument_type="bond"

    for r in results:
        print(r)  # Выводим результат


if __name__ == "__main__":
    main()
```
**Важно:** Синхронные функции нельзя вызывать внутри уже запущенного asyncio цикла. В таких случаях используйте MoexClient.

---

## 💻 Командная строка (CLI)

Библиотека предоставляет удобный консольный интерфейс. Подробнее см. в [Справочнике по CLI](docs/cli.md).

Примеры:
```bash
moex search "Сбербанк"
moex share info SBER
moex bond coupons SU26238RMFS4
```

---

## Переменные окружения

Поддерживаются настройки через префикс `MOEX_` (из окружения или `.env`):

- `MOEX_BASE_URL` — базовый URL API (по умолчанию `https://iss.moex.com/iss`).
- `MOEX_TIMEOUT` — таймаут HTTP-запросов в секундах (по умолчанию `10`).
- `MOEX_USER_AGENT` — User-Agent клиента.
- `MOEX_REQUEST_DELAY` — минимальная базовая пауза между запросами в секундах (по умолчанию `0.1`).
- `MOEX_REQUEST_JITTER` — дополнительная случайная пауза `random.uniform(0, jitter)` в секундах (по умолчанию `0.05`). Чтобы отключить jitter, установите `0`.

Пример:

```bash
MOEX_REQUEST_DELAY=0.1
MOEX_REQUEST_JITTER=0
```

---

## ⚠️ Обработка ошибок

`pymoex` выбрасывает специализированные исключения для разных HTTP-статусов и сценариев ошибок:

| Статус / сценарий | Исключение |
|---|---|
| HTTP 400 | `MoexBadRequestError` |
| HTTP 401 / 403 | `MoexAuthError` |
| HTTP 404 | `MoexNotFoundError` |
| HTTP 429 | `MoexRateLimitError` |
| HTTP 5xx | `MoexServerError` |
| Другие HTTP 4xx/5xx | `MoexHTTPError` |
| Таймаут (`httpx.TimeoutException`) | `MoexTimeoutError` |
| Ошибка сети (`httpx.RequestError`) | `MoexNetworkError` |
| Ошибка JSON/формата ответа | `MoexResponseParseError` |

---

## 🧠 Кэширование

Библиотека имеет встроенную продвинутую систему кэширования с защитой от **Cache Stampede** (Request Coalescing). Это означает, что если 1000 пользователей одновременно запросят данные по одной акции, библиотека сделает **только один** запрос к бирже.

### Режимы работы

#### 1. In-Memory (по умолчанию): Используется быстрый MemoryCache внутри процесса.
Для большинства проектов ничего настраивать не нужно. Библиотека использует быстрый кэш в памяти.

```python
client = MoexClient(use_cache=True)  # use_cache=False
# Кэш: MemoryCache (TTL=60s, MaxSize=1000)
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
    # Подключаем кастомный Redis-адаптер
    cache = RedisCache(redis_url="redis://localhost:6379/0")
    
    async with MoexClient(cache=cache) as client:
        share = await client.share("SBER")
```

---

## 🧪 Разработка и Тестирование
Проект использует **uv** для управления зависимостями и **pytest** для тестов.
1. Установите зависимости;
```bash
uv sync
```
2. Запустите тесты:
```bash
uv run pytest
```
Тесты используют respx для мокирования ответов API MOEX, что позволяет проверять логику без реальных сетевых запросов к бирже.

---

## 🛠 Структура проекта
- pymoex/client.py: Точка входа, класс MoexClient.
- pymoex/services/: Логика работы с конкретными типами инструментов.
- pymoex/models/: Pydantic-модели ответов.
- pymoex/core/: Базовые компоненты (сессия, кеш, конфиг).
- docs/: Справочники полей.
- tests/: Тесты.
- examples/: Примеры кода.

---

## 📄 Лицензия
Проект распространяется под лицензией MIT.
