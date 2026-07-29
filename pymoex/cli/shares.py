from typing import Annotated

import typer
from typer.main import Typer

from pymoex.api import find_shares, get_dividends, get_share
from pymoex.cli.output import print_error, print_items, print_success
from pymoex.models.dividend import Dividend
from pymoex.models.search import Search
from pymoex.models.share import Share
from pymoex.utils.format_value import format_value

share_app: Typer = typer.Typer(help="Работа с акциями")


@share_app.command(name="info")
def share_info(
    query: Annotated[
        str,
        typer.Argument(help="Тикер, название, ISIN, эмитент"),
    ],
) -> None:
    """
    Получение данных об акции по строке.
    """

    try:
        share: Share = get_share(ticker=query)
        print_success(share)
    except Exception:
        print_error(f"Акция '{query}' не найдена.")


@share_app.command(name="find")
def share_find(
    query: Annotated[
        str,
        typer.Argument(..., help="Тикер, название, ISIN, эмитент"),
    ],
) -> None:
    """
    Синхронный поиск акций по строке.
    """

    results: list[Search] = find_shares(query)
    print_items(results)


@share_app.command(name="divs")
def share_divs(
    query: Annotated[
        str,
        typer.Argument(..., help="Тикер, название, ISIN, эмитент"),
    ],
) -> None:
    """
    Синхронный поиск дивидендов по строке.
    """

    dividends: list[Dividend] = get_dividends(ticker=query)

    if not dividends:
        print("Дивиденды не выплачивались или данные отсутствуют.")
        return

    for dividend in dividends[-5:]:
        amount = format_value(dividend.value, dividend.currency_id)
        print(f" - Отсечка {dividend.registry_close_date}: {amount}")
