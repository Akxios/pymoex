import asyncio
from decimal import Decimal

from pymoex import MoexClient
from pymoex.exceptions import InstrumentNotFoundError
from pymoex.models.bond import Bond
from pymoex.models.currency import Currency
from pymoex.models.share import Share


def format_value(value: object | None, suffix: str | None = None) -> str:
    """
    Красиво форматирует значение для вывода в консоль.
    """
    if value is None:
        return "—"

    if isinstance(value, Decimal):
        text = f"{value:.4f}".rstrip("0").rstrip(".")
    else:
        text = str(value)

    if suffix:
        return f"{text} {suffix}"

    return text


async def show_share(client: MoexClient, ticker: str) -> None:
    """
    Пример получения акции и дивидендов.
    """
    print("--- Акция ---")

    try:
        share: Share = await client.share(ticker)
    except InstrumentNotFoundError:
        print(f"Акция {ticker} не найдена.")
        return

    print(f"Тикер: {share.sec_id}")
    print(f"Название: {share.short_name}")
    print(f"Полное название: {share.name or '—'}")
    print(f"Режим торгов: {share.board_id or '—'}")
    print(f"Последняя цена: {format_value(share.last_price, share.currency_id)}")
    print(f"Цена открытия: {format_value(share.open_price, share.currency_id)}")
    print(f"Лот: {format_value(share.lot_size)} шт.")

    dividends = await client.dividends(ticker)

    print("\nПоследние дивиденды:")

    if not dividends:
        print("Дивиденды не найдены.")
        return

    for dividend in dividends[-5:]:
        amount = format_value(dividend.value, dividend.currency_id)
        print(f" - Отсечка {dividend.registry_close_date}: {amount}")


async def show_bond(client: MoexClient, ticker: str) -> None:
    """
    Пример получения облигации, купонов и амортизации.
    """
    print("\n--- Облигация ---")

    try:
        bond: Bond = await client.bond(ticker)
    except InstrumentNotFoundError:
        print(f"Облигация {ticker} не найдена.")
        return

    print(f"Тикер: {bond.sec_id}")
    print(f"Название: {bond.short_name}")
    print(f"Полное название: {bond.name or '—'}")
    print(f"Режим торгов: {bond.board_id or '—'}")
    print(f"Цена, % от номинала: {format_value(bond.price_percent, '%')}")
    print(f"Расчётная цена: {format_value(bond.last_price, bond.face_unit)}")
    print(f"НКД: {format_value(bond.accruedint, bond.face_unit)}")
    print(f"Грязная цена: {format_value(bond.last_dirty_price, bond.face_unit)}")
    print(f"Эффективная доходность: {format_value(bond.effective_yield, '%')}")
    print(f"Ближайший купон: {bond.next_coupon or '—'}")
    print(f"Размер купона: {format_value(bond.coupon_value, bond.face_unit)}")
    print(f"Дата погашения: {bond.mat_date or '—'}")

    coupons = await client.coupons(ticker)

    print("\nБлижайшие купоны:")

    if not coupons:
        print("Купоны не найдены.")
    else:
        for coupon in coupons[:5]:
            amount = format_value(coupon.value, coupon.face_unit)
            print(f" - {coupon.coupon_date}: {amount}")

    amortizations = await client.amortizations(ticker)

    print("\nГрафик амортизации:")

    if not amortizations:
        print("Без амортизации или данные не найдены.")
    else:
        for amortization in amortizations:
            amount = format_value(amortization.value, amortization.face_unit)
            print(f" - {amortization.amort_date}: {amount}")


async def show_currency(client: MoexClient, ticker: str) -> None:
    """
    Пример получения валютного инструмента.
    """
    print("\n--- Валюта ---")

    try:
        currency: Currency = await client.currency(ticker)
    except InstrumentNotFoundError:
        print(f"Валюта {ticker} не найдена.")
        return

    print(f"Тикер: {currency.sec_id}")
    print(f"Название: {currency.short_name}")
    print(f"Полное название: {currency.name or '—'}")
    print(f"Режим торгов: {currency.board_id or '—'}")
    print(f"Последняя цена: {format_value(currency.last_price)}")
    print(f"Цена открытия: {format_value(currency.open_price)}")
    print(f"Лот: {format_value(currency.lot_size)}")


async def show_search(client: MoexClient, query: str) -> None:
    """
    Пример поиска инструментов.
    """
    print(f"\n--- Поиск: {query} ---")

    results = await client.find(query)

    if not results:
        print("Ничего не найдено.")
        return

    for item in results[:5]:
        print(f" - {item.name or item.short_name} ({item.sec_id}) | group={item.group}")


async def main() -> None:
    async with MoexClient() as client:
        await show_share(client, "SBER")
        await show_bond(client, "RU000A10DS74")
        await show_currency(client, "CNYRUB_TOM")
        await show_search(client, "Сбербанк")


if __name__ == "__main__":
    asyncio.run(main())
