import asyncio

from pymoex import MoexClient


async def main():
    async with MoexClient() as client:
        cny = await client.currency("CNYRUB_TOM")
        print(f"Юань: {cny.last_price}")

        usd = await client.currency("USDRUBTOMOTC")
        print(f"Доллар: {usd.last_price}")

        gld = await client.currency("GLDRUB_TOM")
        print(f"Золото: {gld.last_price}")


if __name__ == "__main__":
    asyncio.run(main())
