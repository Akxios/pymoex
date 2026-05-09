import asyncio

from pymoex import MoexClient
from pymoex.models.bond import Bond
from pymoex.models.bondization import Amortization, Coupon
from pymoex.models.search import Search


async def main() -> None:
    async with MoexClient() as client:
        # --- 1. РЫНОК АКЦИЙ ---
        share_ticker = "SBER"
        share = await client.share(ticker=share_ticker)

        print("--- Акции ---")
        print(f"Название: {share.short_name}")
        print(f"Текущая цена: {share.prev_price} {share.currency_id}")

        print("\nПоследние дивиденды:")
        dividends = await client.dividends(ticker=share_ticker)
        if dividends:
            for div in dividends[-5:]:  # Берем 5 самых свежих
                message: str = (
                    f" - Отсечка {div.registry_close_date}: "
                    f"Выплата {div.value} {div.currency_id}"
                )
                print(message)
        else:
            print("Дивиденды не найдены.")

        # --- 2. РЫНОК ОБЛИГАЦИЙ ---
        bond_ticker = "RU000A10DS74"
        bond: Bond = await client.bond(ticker=bond_ticker)

        print("\n--- Облигации ---")
        print(f"Название: {bond.short_name}")
        print(f"Текущая цена: {bond.price_percent}%")
        print(f"Доходность: {bond.effective_yield}%")
        print(
            f"Ближайший купон: {bond.next_coupon} ",
            f"({bond.coupon_value} {bond.face_unit})",
        )

        print("\nГрафик купонов:")
        coupons: list[Coupon] = await client.coupons(ticker=bond_ticker)
        for coupon in coupons[:3]:  # Выводим только первые 3
            print(f" - {coupon.coupon_date}: {coupon.value} {coupon.face_unit}")

        print("\nГрафик амортизации:")
        amortizations: list[Amortization] = await client.amortizations(
            ticker=bond_ticker
        )
        if amortizations:
            for amort in amortizations:
                print(
                    f" - {amort.amort_date}: Погашение {amort.value} {amort.face_unit}"
                )
        else:
            print("Без амортизации (номинал гасится в конце срока).")

        # --- 3. ГЛОБАЛЬНЫЙ ПОИСК ---
        query = "Сбербанк"
        print(f"\n--- Поиск: {query} ---")
        results: list[Search] = await client.find(query, instrument_type="share")

        for r in results[:3]:  # Показываем только Топ-3 результата
            print(f" - {r.name} ({r.sec_id}) | Рег. номер: {r.reg_number}")


if __name__ == "__main__":
    asyncio.run(main=main())
