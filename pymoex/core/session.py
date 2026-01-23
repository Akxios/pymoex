import httpx
from pymoex.core.config import MoexSettings


class MoexSession:
    """
    Асинхронная HTTP-сессия для работы с MOEX ISS API.

    Оборачивает httpx.AsyncClient и инкапсулирует:
    - базовый URL API
    - таймауты
    - заголовки (User-Agent)
    - единый интерфейс для выполнения запросов

    Используется всеми сервисами (SharesService, BondsService, SearchService и т.д.).
    """

    def __init__(self):
        # Загружаем настройки из окружения / .env
        self.settings = MoexSettings()

        # Создаём асинхронный HTTP-клиент с общими параметрами
        self.client = httpx.AsyncClient(
            base_url=self.settings.base_url,   # https://iss.moex.com/iss
            timeout=self.settings.timeout,    # таймаут запросов в секундах
            headers={
                "User-Agent": self.settings.user_agent,  # идентификация SDK
            },
        )

    async def get(self, path: str, params: dict | None = None) -> dict:
        """
        Выполнить GET-запрос к MOEX ISS API.

        :param path: относительный путь (например, '/securities.json')
        :param params: query-параметры запроса
        :return: JSON-ответ, преобразованный в dict

        Исключения:
        - httpx.HTTPStatusError при неуспешном статусе ответа
        """
        response = await self.client.get(path, params=params)
        response.raise_for_status()  # пробрасываем ошибки 4xx/5xx
        return response.json()

    async def close(self) -> None:
        """
        Корректно закрыть HTTP-сессию.

        Вызывается в MoexClient.__aexit__ при выходе из async with.
        """
        await self.client.aclose()
