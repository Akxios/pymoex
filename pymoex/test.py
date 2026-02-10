import asyncio
import logging

from pymoex import MoexClient

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


async def main():
    async with MoexClient() as client:
        # Акции
        share = await client.share("SBER")
        print("Share:", share)

        # Поиск (облигации и акции)
        results = await client.find("Сбербанк", instrument_type="share")

        for r in results:
            print(r)

        # Конкретная облигация
        bond = await client.bond("RU000A10DS74")
        print(bond)


if __name__ == "__main__":
    asyncio.run(main())
