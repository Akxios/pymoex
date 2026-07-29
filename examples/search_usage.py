import asyncio

from pymoex import MoexClient
from pymoex.models.enums import InstrumentType
from pymoex.utils.format_value import format_search


async def main() -> None:
    query = "Сбербанк"

    async with MoexClient() as client:
        all_results = await client.find(query)
        format_search(f"Все инструменты по запросу: {query}", all_results)

        shares = await client.find(query, instrument_type=InstrumentType.SHARE)
        format_search(f"Акции по запросу: {query}", shares)

        bonds = await client.find(query, instrument_type=InstrumentType.BOND)
        format_search(f"Облигации по запросу: {query}", bonds)

        funds = await client.find("SBMX", instrument_type="fund")
        format_search("Фонды по запросу: SBMX", funds)

        currencies = await client.find("CNY", instrument_type=InstrumentType.CURRENCY)
        format_search("Валюты по запросу: CNY", currencies)


if __name__ == "__main__":
    asyncio.run(main())
