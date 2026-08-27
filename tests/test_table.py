import pytest

from pymoex.exceptions import MoexResponseParseError
from pymoex.utils.table import first_row, parse_table


def test_parse_table_returns_empty_list_for_valid_empty_table() -> None:
    assert parse_table({"columns": ["SECID"], "data": []}) == []


@pytest.mark.parametrize(
    ("block", "message"),
    [
        ({}, "Expected 'columns' to be a list"),
        (
            {"columns": None, "data": None},
            "Expected 'columns' to be a list",
        ),
        (
            {"columns": ["SECID"], "data": None},
            "Expected 'data' to be a list",
        ),
        (
            {"columns": ["SECID", 1], "data": []},
            "Expected all column names to be strings",
        ),
        (
            {"columns": ["SECID"], "data": ["SBER"]},
            "Row 0 is not a list",
        ),
        (
            {"columns": ["SECID", "LAST"], "data": [["SBER"]]},
            "Row 0 has 1 values, expected 2",
        ),
        (
            {"columns": ["SECID"], "data": [["SBER", 310.15]]},
            "Row 0 has 2 values, expected 1",
        ),
    ],
)
def test_parse_table_rejects_invalid_table(
    block: dict[str, object],
    message: str,
) -> None:
    with pytest.raises(MoexResponseParseError, match=message):
        _ = parse_table(block)


def test_parse_table_maps_complete_row() -> None:
    assert parse_table(
        {
            "columns": ["SECID", "LAST"],
            "data": [["SBER", 310.15]],
        }
    ) == [{"SECID": "SBER", "LAST": 310.15}]


def test_first_row_uses_strict_table_validation() -> None:
    with pytest.raises(MoexResponseParseError):
        _ = first_row({})
