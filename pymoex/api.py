import asyncio
from typing import Any
from pymoex.client import MoexClient


def _run_sync(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # нет запущенного цикла — можем использовать asyncio.run
        return asyncio.run(coro)
    else:
        # цикл уже запущен (например в Jupyter) — просим использовать async API
        raise RuntimeError("Event loop is already running; use async API instead")


def get_share(ticker: str) -> Any:
    async def _main():
        async with MoexClient() as client:
            return await client.share(ticker)
    return _run_sync(_main())


def get_bond(ticker: str) -> Any:
    async def _main():
        async with MoexClient() as client:
            return await client.bond(ticker)
    return _run_sync(_main())


def find_shares(query: str):
    async def _main():
        async with MoexClient() as client:
            return await client.find_shares(query)
    return _run_sync(_main())


def find_bonds(query: str):
    async def _main():
        async with MoexClient() as client:
            return await client.find_bonds(query)
    return _run_sync(_main())
