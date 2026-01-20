ENGINE = "stock"
BASE = f"/engines/{ENGINE}/markets"


def share(ticker: str) -> str:
    return f"{BASE}/shares/securities/{ticker}.json"


def bond(ticker: str) -> str:
    return f"{BASE}/bonds/securities/{ticker}.json"


def search() -> str:
    return "/securities.json"
