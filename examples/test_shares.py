import asyncio

from pymoex import MoexClient


async def main():
    ticker = "SBER"

    async with MoexClient() as client:
        # Получаем основные данные по акции
        share = await client.share(ticker)

        print(f"Название: {share.short_name}")
        print(f"Текущая цена: {share.last_price} {share.currency_id}")
        print(f"Объем торгов: {share.volume_today} шт.\n")

        # Получаем историю дивидендов
        print("Последние дивиденды:")
        dividends = await client.dividends(ticker)

        if dividends:
            # Выводим 5 самых свежих выплат (Мосбиржа отдает их по возрастанию даты,
            # поэтому берем с конца списка)
            for div in dividends[-5:]:
                print(
                    f" - Отсечка {div.registry_close_date}: Выплата {div.value} {div.currency_id}"
                )
        else:
            print("Дивиденды не выплачивались или данные отсутствуют.")


if __name__ == "__main__":
    asyncio.run(main())
