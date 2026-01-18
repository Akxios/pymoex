import asyncio
from pymoex import MoexClient


async def main():
    async with MoexClient() as client:
        # Акции
        share = await client.share("SBER")
        print("Share:", share)

        # Поиск (только облигации)
        bonds = await client.find("сбербанк", instrument_type="bond") # or share
        print("Search bonds:", bonds)

        # Конкретная облигация
        bond = await client.bond("RU000A10DS74")
        print("Bond:", bond)


if __name__ == "__main__":
    asyncio.run(main())
