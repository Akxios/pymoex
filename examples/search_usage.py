import asyncio

from pymoex import MoexClient
from pymoex.models.enums import InstrumentType
from pymoex.models.search import Search


def print_results(title: str, results: list[Search], limit: int = 5) -> None:
    """
    Красиво печатает результаты поиска.
    """
    print(f"\n--- {title} ---")

    if not results:
        print("Ничего не найдено.")
        return

    for item in results[:limit]:
        name = item.name or item.short_name or "—"
        print(f" - {name} ({item.sec_id}) | group={item.group}")


async def main() -> None:
    query = "Сбербанк"

    async with MoexClient() as client:
        all_results = await client.find(query)
        print_results(f"Все инструменты по запросу: {query}", all_results)

        shares = await client.find(query, instrument_type=InstrumentType.SHARE)
        print_results(f"Акции по запросу: {query}", shares)

        bonds = await client.find(query, instrument_type=InstrumentType.BOND)
        print_results(f"Облигации по запросу: {query}", bonds)

        funds = await client.find("SBMX", instrument_type="fund")
        print_results("Фонды по запросу: SBMX", funds)

        currencies = await client.find("CNY", instrument_type=InstrumentType.CURRENCY)
        print_results("Валюты по запросу: CNY", currencies)


if __name__ == "__main__":
    asyncio.run(main())
