import asyncio
from pymoex import MoexClient


async def main():
    async with MoexClient() as client:
        # Акции
        share = await client.share("SBER")
        print("Share:", share)

        # Поиск (облигации и акции)
        search_example1 = await client.find_shares("сбербанк")
        print("Search bonds:", search_example1)

        search_example2 = await client.find_bonds("сбербанк")
        print("Search bonds:", search_example2)

        search_example3 = await client.find("сбербанк", "bond") # or share
        print("Search bonds:", search_example3)

        # Конкретная облигация
        bond = await client.bond("RU000A10DS74")
        print("Bond:", bond)


if __name__ == "__main__":
    asyncio.run(main())
