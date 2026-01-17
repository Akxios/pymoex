import asyncio
from pymoex import MoexClient


async def main():
    client = MoexClient()

    example1 = await client.share("SBER")
    print(example1)

    example2 = await client.find("сбер", "share")
    print(example2)

    example3 = await client.bond("SU26238RMFS4")
    print(example3)


if __name__ == "__main__":
    asyncio.run(main())
