import httpx
from pymoex.core.config import MoexSettings

class MoexSession:
    def __init__(self):
        self.settings = MoexSettings()

        self.client = httpx.AsyncClient(
            base_url=self.settings.base_url,
            timeout=self.settings.timeout,
            headers={
                "User-Agent": self.settings.user_agent
            }
        )

    async def get(self, path: str, params: dict | None = None) -> dict:
        response = await self.client.get(path, params=params)
        response.raise_for_status()
        return response.json()

    async def close(self):
        await self.client.aclose()
