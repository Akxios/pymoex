import asyncio

from pymoex import MoexClient
from pymoex.exceptions import InstrumentNotFoundError
from pymoex.models.bond import Bond
from pymoex.utils.format_value import format_value


async def show_bond(client: MoexClient, ticker: str) -> None:
    """
    Показать данные по облигации, купоны и амортизацию.
    """
    try:
        bond: Bond = await client.bond(ticker)
    except InstrumentNotFoundError:
        print(f"Облигация {ticker} не найдена.")
        return

    print("--- Облигация ---")
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

    print("Все купоны:")

    if not coupons:
        print("Купоны не найдены.")
    else:
        for coupon in coupons:
            amount = format_value(coupon.value, coupon.face_unit)
            print(f" - {coupon.coupon_date}: {amount}")

    amortizations = await client.amortizations(ticker)

    print("\nГрафик амортизации:")

    if not amortizations:
        print("Без амортизации или данные не найдены.")
    else:
        for amortization in amortizations:
            amount = format_value(amortization.value, amortization.face_unit)
            print(f" - {amortization.amort_date}: погашение {amount}")


async def main() -> None:
    async with MoexClient() as client:
        await show_bond(client, "RU000A10DS74")


if __name__ == "__main__":
    asyncio.run(main())
