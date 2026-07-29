import asyncio

from pymoex import MoexClient
from pymoex.exceptions import InstrumentNotFoundError
from pymoex.models.currency import Currency
from pymoex.utils.format_value import format_value


async def show_currency(client: MoexClient, ticker: str, title: str) -> None:
    """
    Показать данные по валютному инструменту.
    """
    try:
        currency: Currency = await client.currency(ticker)
    except InstrumentNotFoundError:
        print(f"{title}: инструмент {ticker} не найден.")
        return

    print(f"\n--- {title} ---")
    print(f"Тикер: {currency.sec_id}")
    print(f"Название: {currency.short_name}")
    print(f"Полное название: {currency.name or '—'}")
    print(f"Режим торгов: {currency.board_id or '—'}")
    print(f"Последняя цена: {format_value(currency.last_price)}")
    print(f"Цена открытия: {format_value(currency.open_price)}")
    print(f"Максимум: {format_value(currency.high_price)}")
    print(f"Минимум: {format_value(currency.low_price)}")
    print(f"Объём: {format_value(currency.volume_today)}")
    print(f"Сделок: {format_value(currency.num_trades)}")


async def main() -> None:
    instruments = [
        ("CNYRUB_TOM", "Юань"),
        ("USDRUBTOMOTC", "Доллар"),
        ("GLDRUB_TOM", "Золото"),
    ]

    async with MoexClient() as client:
        for ticker, title in instruments:
            await show_currency(client, ticker, title)


if __name__ == "__main__":
    asyncio.run(main())
