from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
import respx

from pymoex.client import MoexClient
from pymoex.core.config import MoexSettings

type MoexTable = dict[str, object]
type MoexResponse = dict[str, MoexTable]


@pytest.fixture
def moex_settings() -> MoexSettings:
    return MoexSettings(
        request_delay=0,
        request_jitter=0,
        retry_min_wait=0,
        retry_max_wait=0,
    )


@pytest.fixture
def mock_moex_api(moex_settings: MoexSettings):
    with respx.mock(base_url=moex_settings.base_url) as respx_mock:
        yield respx_mock


def moex_table(columns: list[str], data: list[list[object]]) -> MoexTable:
    return {
        "columns": columns,
        "data": data,
    }


EMPTY_SECURITIES_RESPONSE: MoexResponse = {
    "securities": moex_table(columns=[], data=[]),
}


MOEX_SHARE_JSON: MoexResponse = {
    "securities": moex_table(
        columns=[
            "SECID",
            "SHORTNAME",
            "LOTSIZE",
            "ISIN",
            "BOARDID",
            "SECNAME",
        ],
        data=[
            [
                "SBER",
                "Сбербанк",
                10,
                "RU0009029540",
                "TQBR",
                "Сбербанк России",
            ],
        ],
    ),
    "marketdata": moex_table(
        columns=[
            "SECID",
            "LAST",
            "OPEN",
            "BOARDID",
        ],
        data=[
            [
                "SBER",
                275.5,
                270.0,
                "TQBR",
            ],
        ],
    ),
    "marketdata_yields": moex_table(columns=[], data=[]),
}


MOEX_BOND_JSON: MoexResponse = {
    "securities": moex_table(
        columns=[
            "SECID",
            "SHORTNAME",
            "LOTSIZE",
            "ISIN",
            "BOARDID",
            "SECNAME",
            "FACEVALUE",
            "FACEUNIT",
            "COUPONVALUE",
            "COUPONPERCENT",
            "NEXTCOUPON",
            "COUPONPERIOD",
            "MATDATE",
        ],
        data=[
            [
                "SU26238RMFS4",
                "ОФЗ 26238",
                1,
                "RU000A1038V6",
                "TQOB",
                "ОФЗ-ПД 26238",
                1000,
                "RUB",
                35.4,
                7.1,
                "2026-06-10",
                182,
                "2041-05-15",
            ],
        ],
    ),
    "marketdata": moex_table(
        columns=[
            "SECID",
            "BOARDID",
            "LAST",
            "OPEN",
            "YIELD",
            "ACCRUEDINT",
        ],
        data=[
            [
                "SU26238RMFS4",
                "TQOB",
                72.5,
                72.0,
                14.2,
                12.3,
            ],
        ],
    ),
    "marketdata_yields": moex_table(
        columns=[
            "SECID",
            "BOARDID",
            "EFFECTIVEYIELD",
        ],
        data=[
            [
                "SU26238RMFS4",
                "TQOB",
                14.5,
            ],
        ],
    ),
}


MOEX_CURRENCY_JSON: MoexResponse = {
    "securities": moex_table(
        columns=[
            "SECID",
            "SHORTNAME",
            "BOARDID",
            "SECNAME",
            "LOTSIZE",
            "FACEVALUE",
            "MINSTEP",
        ],
        data=[
            [
                "CNYRUB_TOM",
                "CNY/RUB TOM",
                "CETS",
                "Китайский юань к российскому рублю",
                1000,
                1,
                0.0001,
            ],
        ],
    ),
    "marketdata": moex_table(
        columns=[
            "SECID",
            "BOARDID",
            "LAST",
            "OPEN",
            "HIGH",
            "LOW",
            "VOLTODAY",
            "VALTODAY",
            "NUMTRADES",
        ],
        data=[
            [
                "CNYRUB_TOM",
                "CETS",
                12.3456,
                12.3,
                12.4,
                12.2,
                1000000,
                12345600,
                100,
            ],
        ],
    ),
}


MOEX_SEARCH_JSON: MoexResponse = {
    "securities": moex_table(
        columns=[
            "secid",
            "shortname",
            "name",
            "group",
            "is_traded",
        ],
        data=[
            [
                "SBER",
                "Сбербанк",
                "ПАО Сбербанк",
                "stock_shares",
                1,
            ],
            [
                "SBERP",
                "Сбербанк-п",
                "ПАО Сбербанк прив.",
                "stock_shares",
                1,
            ],
            [
                "SU26238RMFS4",
                "ОФЗ 26238",
                "ОФЗ-ПД 26238",
                "stock_bonds",
                1,
            ],
            [
                "SBMX",
                "БПИФ SBMX",
                "БПИФ Сбер Индекс МосБиржи",
                "stock_ppif",
                1,
            ],
            [
                "CNYRUB_TOM",
                "CNY/RUB TOM",
                "Китайский юань к российскому рублю",
                "currency_selt",
                1,
            ],
        ],
    ),
}


MOEX_DIVIDENDS_JSON: MoexResponse = {
    "dividends": moex_table(
        columns=[
            "secid",
            "registryclosedate",
            "value",
            "currencyid",
        ],
        data=[
            [
                "SBER",
                "2025-07-18",
                34.84,
                "RUB",
            ],
        ],
    ),
}


MOEX_BONDIZATION_JSON: MoexResponse = {
    "coupons": moex_table(
        columns=[
            "secid",
            "isin",
            "coupondate",
            "recorddate",
            "value",
            "valueprc",
            "faceunit",
        ],
        data=[
            [
                "SU26238RMFS4",
                "RU000A1038V6",
                "2026-06-10",
                "2026-06-09",
                35.4,
                7.1,
                "RUB",
            ],
        ],
    ),
    "amortizations": moex_table(
        columns=[
            "secid",
            "isin",
            "amortdate",
            "value",
            "valueprc",
            "faceunit",
        ],
        data=[
            [
                "SU26238RMFS4",
                "RU000A1038V6",
                "2041-05-15",
                1000,
                100,
                "RUB",
            ],
        ],
    ),
}


@pytest_asyncio.fixture
async def client() -> AsyncIterator[MoexClient]:
    async with MoexClient() as moex_client:
        yield moex_client


@pytest_asyncio.fixture
async def mock_moex(client: MoexClient) -> AsyncIterator[respx.MockRouter]:
    with respx.mock(base_url=client.session.settings.base_url) as respx_mock:
        yield respx_mock
