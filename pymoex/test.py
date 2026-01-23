import asyncio
from pymoex import MoexClient


async def main():
    async with MoexClient() as client:
        # Акции
        share = await client.share("SBER")
        print("Share:", share.last_price)

        # Поиск (облигации и акции)
        results = await client.find("Сбербанк", instrument_type="share")

        for r in results:
            print(r)

        # Конкретная облигация
        bond = await client.bond("RU000A10DS74")
        print(bond)


if __name__ == "__main__":
    asyncio.run(main())
