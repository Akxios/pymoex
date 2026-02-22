import asyncio

from pymoex import MoexClient


async def main():
    async with MoexClient() as client:
        query = "Сбербанк"

        # Поиск только среди акций
        print(f"--- Ищем акции по запросу: {query} ---")
        shares = await client.find(query, instrument_type="share")

        for r in shares[:3]:
            print(r)

        # Поиск только среди облигаций
        print(f"\n--- Ищем облигации по запросу: {query} ---")
        bonds = await client.find(query, instrument_type="bond")

        for r in bonds[:3]:
            print(r)


if __name__ == "__main__":
    asyncio.run(main())
