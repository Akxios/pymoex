import pytest
from httpx import Response

from pymoex.exceptions import InstrumentNotFoundError

# Пример ответа для облигации (ОФЗ)
MOEX_BOND_JSON = {
    "securities": {
        "columns": ["SECID", "SHORTNAME", "ISIN", "BOARDID", "FACEVALUE", "MATDATE"],
        "data": [
            ["SU26238RMFS4", "ОФЗ 26238", "RU000A1038V6", "TQOB", 1000, "2041-05-15"]
        ],
    },
    "marketdata": {
        "columns": ["SECID", "LAST", "BOARDID"],
        "data": [["SU26238RMFS4", 68.5, "TQOB"]],
    },
    "marketdata_yields": {
        "columns": ["SECID", "EFFECTIVEYIELD", "BOARDID"],
        "data": [["SU26238RMFS4", 12.5, "TQOB"]],
    },
}


@pytest.mark.asyncio
async def test_get_bond_success(client, mock_moex):
    # Мокаем ответ
    mock_moex.get("/engines/stock/markets/bonds/securities/SU26238RMFS4.json").mock(
        return_value=Response(200, json=MOEX_BOND_JSON)
    )

    bond = await client.bond("SU26238RMFS4")

    assert bond.sec_id == "SU26238RMFS4"
    assert bond.short_name == "ОФЗ 26238"
    assert bond.last_price == 685.0
    assert bond.effective_yield == 12.5
    assert str(bond.mat_date) == "2041-05-15"


@pytest.mark.asyncio
async def test_get_bond_not_found(client, mock_moex):
    mock_moex.get("/engines/stock/markets/bonds/securities/UNKNOWN.json").mock(
        return_value=Response(200, json={"securities": {"data": []}})
    )

    with pytest.raises(InstrumentNotFoundError):
        await client.bond("UNKNOWN")
