import asyncio

from pymoex import MoexClient


async def main():
    ticker = "RU000A10DS74"

    async with MoexClient() as client:
        # Получаем основные данные по облигации
        bond = await client.bond(ticker)

        print(f"Название: {bond.short_name}")
        print(f"Текущая цена: {bond.price_percent}%")
        print(f"Доходность: {bond.effective_yield}%")
        print(
            f"Ближайший купон: {bond.next_coupon} ({bond.coupon_value} {bond.face_unit})\n"
        )

        # Получаем график купонов
        print("График купонов:")
        coupons = await client.coupons(ticker)
        for coupon in coupons[:3]:  # Выводим только первые 3
            print(f" - {coupon.coupon_date}: {coupon.value} {coupon.face_unit}")

        # Проверяем амортизацию
        print("\nГрафик амортизации:")
        amortizations = await client.amortizations(ticker)
        if amortizations:
            for amort in amortizations:
                print(
                    f" - {amort.amort_date}: Погашение {amort.value} {amort.face_unit}"
                )
        else:
            print("Без амортизации (номинал гасится в конце срока).")


if __name__ == "__main__":
    asyncio.run(main())
