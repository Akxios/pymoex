from decimal import Decimal

import pytest

from pymoex.utils.types import parse_int


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("10", 10),
        ("10.0", 10),
        (" 10.0 ", 10),
        (Decimal("10.00"), 10),
        ("9007199254740993", 9007199254740993),
    ],
)
def test_parse_int_accepts_integral_values(value: object, expected: int) -> None:
    assert parse_int(value) == expected


@pytest.mark.parametrize(
    "value",
    [None, "", " ", "-", "—", "10.9", Decimal("1.5"), "nan", "inf", "-inf"],
)
def test_parse_int_rejects_missing_fractional_and_non_finite_values(
    value: object,
) -> None:
    assert parse_int(value) is None
