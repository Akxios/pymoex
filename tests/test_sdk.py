from datetime import date
from decimal import Decimal

import respx
from httpx import Response

import pymoex
from pymoex import (
    MoexClient,
    SyncMoexClient,
    find,
    find_bonds,
    find_currencies,
    find_funds,
    find_shares,
    get_amortizations,
    get_coupons,
    get_dividends,
    get_share,
)
from pymoex.core.config import MoexSettings
from pymoex.models.dividend import Dividend
from pymoex.models.share import Share
from tests.conftest import (
    MOEX_BONDIZATION_JSON,
    MOEX_DIVIDENDS_JSON,
    MOEX_SEARCH_JSON,
    MOEX_SHARE_JSON,
)


def test_public_sdk_exports_are_available() -> None:
    expected_exports = {
        "MoexClient",
        "SyncMoexClient",
        "find",
        "find_bonds",
        "find_currencies",
        "find_funds",
        "find_shares",
        "get_amortizations",
        "get_bond",
        "get_coupons",
        "get_currency",
        "get_dividends",
        "get_fund",
        "get_share",
    }

    assert expected_exports <= set(pymoex.__all__)

    for name in expected_exports:
        assert getattr(pymoex, name) is not None

    assert pymoex.MoexClient is MoexClient
    assert pymoex.SyncMoexClient is SyncMoexClient


def test_settings_do_not_expose_proxy_or_auth_fields() -> None:
    removed_fields = {
        "proxy_url",
        "username",
        "password",
    }

    assert removed_fields.isdisjoint(MoexSettings.model_fields)


def test_one_shot_sync_helpers_return_sdk_models() -> None:
    with respx.mock(base_url="https://iss.moex.com/iss") as mock:
        share_route = mock.get(
            "/engines/stock/markets/shares/securities/SBER.json"
        ).mock(return_value=Response(200, json=MOEX_SHARE_JSON))
        dividends_route = mock.get("/securities/SBER/dividends.json").mock(
            return_value=Response(200, json=MOEX_DIVIDENDS_JSON)
        )

        share = get_share("SBER")
        dividends = get_dividends("SBER")

    assert isinstance(share, Share)
    assert share.sec_id == "SBER"
    assert share.short_name == "Сбербанк"

    assert len(dividends) == 1
    assert isinstance(dividends[0], Dividend)
    assert dividends[0].registry_close_date == date(2025, 7, 18)
    assert dividends[0].value == Decimal("34.84")

    assert share_route.call_count == 1
    assert dividends_route.call_count == 1


def test_one_shot_sync_search_helpers_filter_results() -> None:
    with respx.mock(base_url="https://iss.moex.com/iss") as mock:
        route = mock.get("/securities.json").mock(
            return_value=Response(200, json=MOEX_SEARCH_JSON)
        )

        all_results = find("SBER")
        shares = find_shares("SBER")
        bonds = find_bonds("ОФЗ")
        funds = find_funds("SBMX")
        currencies = find_currencies("CNY")

    assert [item.sec_id for item in all_results] == ["SBER", "SBERP"]
    assert [item.sec_id for item in shares] == ["SBER", "SBERP"]
    assert [item.sec_id for item in bonds] == ["SU26238RMFS4"]
    assert [item.sec_id for item in funds] == ["SBMX"]
    assert [item.sec_id for item in currencies] == ["CNYRUB_TOM"]

    assert route.call_count == 5


def test_one_shot_sync_bond_event_helpers_return_typed_rows() -> None:
    with respx.mock(base_url="https://iss.moex.com/iss") as mock:
        route = mock.get("/securities/SU26238RMFS4/bondization.json").mock(
            return_value=Response(200, json=MOEX_BONDIZATION_JSON)
        )

        coupons = get_coupons("SU26238RMFS4")
        amortizations = get_amortizations("SU26238RMFS4")

    assert len(coupons) == 1
    assert coupons[0].coupon_date == date(2026, 6, 10)
    assert coupons[0].value == Decimal("35.4")

    assert len(amortizations) == 1
    assert amortizations[0].amort_date == date(2041, 5, 15)
    assert amortizations[0].value == Decimal("1000")

    assert route.call_count == 2


def test_sync_client_context_reuses_cache_between_calls() -> None:
    with respx.mock(base_url="https://iss.moex.com/iss") as mock:
        route = mock.get("/engines/stock/markets/shares/securities/SBER.json").mock(
            return_value=Response(200, json=MOEX_SHARE_JSON)
        )

        with SyncMoexClient() as client:
            first = client.share("SBER")
            second = client.share("sber")

    assert first.sec_id == "SBER"
    assert second.sec_id == "SBER"
    assert route.call_count == 1
