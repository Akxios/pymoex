import asyncio

from pymoex import MoexClient
from pymoex.exceptions import InstrumentNotFoundError
from pymoex.models.share import Share
from pymoex.utils.format_value import format_value


async def show_share(client: MoexClient, ticker: str) -> None:
    """
    Показать данные по акции и последние дивиденды.
    """
    try:
        share: Share = await client.share(ticker)
    except InstrumentNotFoundError:
        print(f"Акция {ticker} не найдена.")
        return

    print("--- Акция ---")
    print(f"Тикер: {share.sec_id}")
    print(f"Название: {share.short_name}")
    print(f"Полное название: {share.name or '—'}")
    print(f"Режим торгов: {share.board_id or '—'}")
    print(f"Последняя цена: {format_value(share.last_price, share.currency_id)}")
    print(f"Цена открытия: {format_value(share.open_price, share.currency_id)}")
    print(f"Предыдущая цена: {format_value(share.prev_price, share.currency_id)}")
    print(f"Объём торгов: {format_value(share.volume_today)} шт.")
    print(f"Лот: {format_value(share.lot_size)} шт.")

    dividends = await client.dividends(ticker)

    print("\nПоследние дивиденды:")

    if not dividends:
        print("Дивиденды не выплачивались или данные отсутствуют.")
        return

    for dividend in dividends[-5:]:
        amount = format_value(dividend.value, dividend.currency_id)
        print(f" - Отсечка {dividend.registry_close_date}: {amount}")


async def main() -> None:
    async with MoexClient() as client:
        await show_share(client, "SBER")


if __name__ == "__main__":
    asyncio.run(main())
