from collections.abc import Mapping, Sequence


def select_best_board(
    sec_rows: Sequence[Mapping[str, object]],
    md_rows: Sequence[Mapping[str, object]],
    priority_boards: Sequence[str],
) -> str:
    """
    Выбирает оптимальный режим торгов (board) на основе рыночных данных.

    Логика:
    1. Ищет приоритетные площадки среди тех, где есть цены (active).
    2. Если приоритетных нет, берет первую активную (сохраняя порядок биржи).
    3. Если активных нет вообще, ищет приоритетную в базовом списке (sec_rows).
    4. Фолбэк: берет первую доступную из sec_rows.

    Raises:
        ValueError: Если не удалось найти ни одной площадки (пустые данные).
    """

    active_boards: list[str] = []

    for row in md_rows:
        board_id = row.get("BOARDID")
        if not isinstance(board_id, str):
            continue

        has_price = (
            row.get("LAST") is not None
            or row.get("LCLOSEPRICE") is not None
            or row.get("LCURRENTPRICE") is not None
        )

        if has_price and board_id not in active_boards:
            active_boards.append(board_id)

    for board in priority_boards:
        if board in active_boards:
            return board

    if active_boards:
        return active_boards[0]

    sec_boards: list[str] = [
        str(r.get("BOARDID")) for r in sec_rows if isinstance(r.get("BOARDID"), str)
    ]

    for board in priority_boards:
        if board in sec_boards:
            return board

    if sec_boards:
        return sec_boards[0]

    raise ValueError(
        "Невозможно выбрать board: данные sec_rows и md_rows пусты или некорректны."
    )
