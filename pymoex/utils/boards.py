def select_best_board(
    sec_rows: list[dict], md_rows: list[dict], priority_boards: list[str]
) -> str:
    active_boards = {
        row["BOARDID"]
        for row in md_rows
        if row.get("LAST") is not None
        or row.get("LCLOSEPRICE") is not None
        or row.get("LCURRENTPRICE") is not None
    }

    for board in priority_boards:
        if board in active_boards:
            return board

    if active_boards:
        return list(active_boards)[0]

    priority_in_sec = [
        r["BOARDID"] for r in sec_rows if r["BOARDID"] in priority_boards
    ]
    return priority_in_sec[0] if priority_in_sec else sec_rows[0]["BOARDID"]
