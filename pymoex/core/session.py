import httpx
from pymoex.core.config import MoexSettings


class MoexSession:
    """
    Асинхронная сессия для работы с ISS API Московской биржи.
    Оборачивает httpx.AsyncClient и использует настройки из MoexSettings.
    """

    def __init__(self):
        self.settings = MoexSettings()

        self.client = httpx.AsyncClient(
            base_url=self.settings.base_url,
            timeout=self.settings.timeout,
            headers={
                "User-Agent": self.settings.user_agent,
            },
        )

    async def get(self, path: str, params: dict | None = None) -> dict:
        """
        Выполняет GET-запрос к ISS API и возвращает JSON-ответ.

        :param path: путь к ресурсу (например, /securities.json)
        :param params: query-параметры
        :return: ответ в виде словаря
        """
        response = await self.client.get(path, params=params)
        response.raise_for_status()
        return response.json()

    async def close(self) -> None:
        """Закрывает HTTP-сессию."""
        await self.client.aclose()
