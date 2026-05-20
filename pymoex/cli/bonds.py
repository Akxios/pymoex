from typing import Annotated

import typer
from typer.main import Typer

from pymoex.api import find_bonds, get_bond, get_coupons
from pymoex.cli.output import print_error, print_items, print_success
from pymoex.models.bond import Bond
from pymoex.models.bondization import Coupon
from pymoex.models.search import Search

bond_app: Typer = typer.Typer(help="Работа с облигациями")


@bond_app.command(name="info")
def bond_info(
    query: Annotated[
        str,
        typer.Argument(..., help="Тикер, название, ISIN, эмитент"),
    ],
) -> None:
    """
    Синхронный поиск информации об облигации по строке.
    """

    try:
        bond: Bond = get_bond(ticker=query)
        print_success(bond)
    except Exception:
        print_error(f"Облигация '{query}' не найдена.")


@bond_app.command(name="find")
def bond_find(
    query: Annotated[
        str,
        typer.Argument(..., help="Тикер, название, ISIN, эмитент"),
    ],
) -> None:
    """
    Синхронный поиск облигаций по строке.
    """

    results: list[Search] = find_bonds(query)
    print_items(results)


@bond_app.command(name="coupons")
def bond_coupons(
    query: Annotated[
        str,
        typer.Argument(..., help="Тикер, название, ISIN, эмитент"),
    ],
) -> None:
    """
    Синхронный поиск купонов облигации по строке.
    """

    results: list[Coupon] = get_coupons(ticker=query)
    print_items(results)
