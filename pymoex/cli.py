from typing import Annotated

import typer
from typer.main import Typer

from pymoex import get_currency
from pymoex.api import (
    find,
    find_bonds,
    find_shares,
    get_bond,
    get_coupons,
    get_dividends,
    get_share,
)
from pymoex.models.bond import Bond
from pymoex.models.bondization import Coupon
from pymoex.models.dividend import Dividend
from pymoex.models.enums import InstrumentType
from pymoex.models.search import Search
from pymoex.models.share import Share
from pymoex.utils.aliases import resolve_currency_secid

app: Typer = typer.Typer(help="Утилита для работы с данными Московской биржи")


share_app: Typer = typer.Typer(help="Работа с акциями")
bond_app: Typer = typer.Typer(help="Работа с облигациями")


app.add_typer(typer_instance=share_app, name="share")
app.add_typer(typer_instance=bond_app, name="bond")


# ПОИСК
@app.command()
def search(
    query: Annotated[
        str,
        typer.Argument(..., help="Строка для поиска"),
    ],
    instr_type: Annotated[
        InstrumentType | None,
        typer.Option("--type", "-t", help="Тип инструмента", case_sensitive=False),
    ] = None,
) -> None:
    """
    Синхронный поиск по строке.
    """

    type_val: str | None = instr_type.value if instr_type is not None else None

    results: list[Search] = find(query, type_val)

    if not results:
        typer.secho(message="Ничего не найдено.", fg=typer.colors.YELLOW)
        raise typer.Exit()

    typer.secho(message=f"Найдено {len(results)} записей:", fg=typer.colors.GREEN)
    for result in results:
        typer.echo(message=f" - {result}")


# АКЦИИ
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
        typer.secho(message=share, fg=typer.colors.GREEN)
    except Exception:
        typer.secho(message=f"Акция '{query}' не найдена.", fg=typer.colors.YELLOW)
        raise typer.Exit(code=1)


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

    if not results:
        typer.secho(message="Ничего не найдено.", fg=typer.colors.YELLOW)
        raise typer.Exit()

    typer.secho(message=f"Найдено {len(results)} записей:", fg=typer.colors.GREEN)
    for result in results:
        typer.echo(message=f" - {result}")


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
    results: list[Dividend] = get_dividends(ticker=query)

    if not results:
        typer.secho(message="Дивиденды не найдены.", fg=typer.colors.YELLOW)
        raise typer.Exit()

    typer.secho(message=f"Найдено {len(results)} записей:", fg=typer.colors.GREEN)
    for div in results:
        typer.echo(message=f" - {div}")


# ОБЛИГАЦИИ
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
        typer.secho(message=bond, fg=typer.colors.GREEN)
    except Exception:
        typer.secho(message=f"Облигация '{query}' не найдена.", fg=typer.colors.YELLOW)
        raise typer.Exit(code=1)


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

    if not results:
        typer.secho(message="Ничего не найдено.", fg=typer.colors.YELLOW)
        raise typer.Exit()

    typer.secho(message=f"Найдено {len(results)} записей:", fg=typer.colors.GREEN)
    for result in results:
        typer.echo(message=f" - {result}")


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

    if not results:
        typer.secho(message="Купоны не найдены.", fg=typer.colors.YELLOW)
        raise typer.Exit()

    typer.secho(message=f"Найдено {len(results)} записей:", fg=typer.colors.GREEN)
    for result in results:
        typer.echo(message=f" - {result}")


# ВАЛЮТА
@app.command("currency")
def currency(
    query: Annotated[
        str,
        typer.Argument(..., help="Код валюты"),
    ],
) -> None:
    """
    Получение курса валюты или металла.
    """

    real_secid = resolve_currency_secid(query)

    try:
        currency_model = get_currency(ticker=real_secid)

        typer.secho(f"Данные по {query.upper()} ({real_secid}):", fg=typer.colors.CYAN)
        typer.secho(str(currency_model), fg=typer.colors.GREEN)

    except Exception as e:  # <--- ДОБАВЛЕНО as e
        typer.secho(
            f"Валюта '{query}' (secid: {real_secid}) не найдена. Причина: {e}",  # <--- ВЫВОДИМ e
            fg=typer.colors.YELLOW,
        )
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
