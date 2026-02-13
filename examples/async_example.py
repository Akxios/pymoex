import asyncio
import logging

from pymoex import MoexClient

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


async def main():
    async with MoexClient(use_cache=True) as client:  # use_cache=False
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
