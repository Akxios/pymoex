from typing import Annotated

import typer
from typer.main import Typer

from pymoex.api import find_bonds, get_amortizations, get_bond, get_coupons
from pymoex.cli.output import print_error, print_items, print_success
from pymoex.models.bond import Bond
from pymoex.models.bondization import Amortization, Coupon
from pymoex.models.search import Search
from pymoex.utils.format_value import format_value

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

    coupons: list[Coupon] = get_coupons(ticker=query)

    if not coupons:
        print("Купоны не найдены.")
    else:
        for coupon in coupons:
            amount = format_value(coupon.value, coupon.face_unit)
            print(f" - {coupon.coupon_date}: {amount}")


@bond_app.command(name="amortizations")
def bond_amortizations(
    query: Annotated[
        str,
        typer.Argument(..., help="Тикер, название, ISIN, эмитент"),
    ],
) -> None:
    """
    Синхронный поиск амортизаций облигации по строке.
    """

    amortizations: list[Amortization] = get_amortizations(ticker=query)

    if not amortizations:
        print("Без амортизации или данные не найдены.")
    else:
        for amortization in amortizations:
            amount = format_value(amortization.value, amortization.face_unit)
            print(f" - {amortization.amort_date}: погашение {amount}")
