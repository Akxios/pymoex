import asyncio

from pymoex import MoexClient


async def main():
    async with MoexClient() as client:
        # Обычный юань
        cny = await client.currency("CNY")
        print(f"Юань: {cny.last_price}")

        # Внебиржевой (актуальный) доллар
        usd = await client.currency("USDCB")
        print(f"Доллар (внебиржа): {usd.last_price}")

        # Золото
        gld = await client.currency("GLD")
        print(f"Золото: {gld.last_price}")


if __name__ == "__main__":
    asyncio.run(main())
