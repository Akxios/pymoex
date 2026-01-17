from pymoex.core.session import MoexSession
from pymoex.services.shares import SharesService
from pymoex.services.search import SearchService
from pymoex.services.bonds import BondsService


class MoexClient:
    """Асинхронный клиент для работы с ISS API Московской биржи."""
    def __init__(self):
        self.session = MoexSession()
        self.shares = SharesService(self.session)
        self.search = SearchService(self.session)
        self.bonds = BondsService(self.session)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def close(self):
        await self.session.close()

    async def share(self, ticker: str):
        return await self.shares.get_share(ticker)

    async def find(self, query: str, instrument_type: str | None = None):
        return await self.search.find(query, instrument_type)

    async def bond(self, ticker: str):
        return await self.bonds.get_bond(ticker)
