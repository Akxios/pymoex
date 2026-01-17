def parse_table(block: dict) -> list[dict]:
    columns = block["columns"]
    return [dict(zip(columns, row)) for row in block["data"]]


def first_row(block: dict) -> dict:
    if not block:
        return {}
    columns = block.get("columns", [])
    rows = block.get("data", [])
    if not rows:
        return {}
    return dict(zip(columns, rows[0]))
