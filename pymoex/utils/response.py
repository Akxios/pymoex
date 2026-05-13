from typing import cast


def normalize_ticker(ticker: str) -> str:
    return ticker.strip().upper()


def get_table(data: dict[str, object], name: str) -> dict[str, object]:
    table = data.get(name)

    if isinstance(table, dict):
        return cast(dict[str, object], table)

    return {}


def find_row_by_board(
    rows: list[dict[str, object]],
    board_id: object,
) -> dict[str, object] | None:
    return next(
        (row for row in rows if row.get("BOARDID") == board_id),
        None,
    )
