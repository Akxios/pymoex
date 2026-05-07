from unittest import result

import typer

from pymoex.api import (
    find,
    find_bonds,
    find_shares,
    get_bond,
    get_coupons,
    get_dividends,
    get_share,
)

app = typer.Typer(help="Утилита для работы с данными Московской биржи")

share_app = typer.Typer(help="Работа с акциями (поиск, информация, дивиденды)")
bond_app = typer.Typer(help="Работа с облигациями (поиск, купоны, амортизация)")

app.add_typer(share_app, name="share")
app.add_typer(bond_app, name="bond")


# ПОИСК
@app.command()
def search(query: str = typer.Argument(..., help="Общий поиск")):
    """
    Синхронный поиск по строке.
    """
    results = find(query)

    if not results:
        typer.secho("Ничего не найдено.", fg=typer.colors.YELLOW)
        raise typer.Exit()

    typer.secho(f"Найдено {len(results)} записей:", fg=typer.colors.GREEN)
    for result in results:
        typer.echo(f" - {result}")


# АКЦИИ
@share_app.command("info")
def share_info(query: str = typer.Argument(..., help="Тикер, название, ISIN, эмитент")):
    """
    Получение данных об акции по строке.
    """

    try:
        share = get_share(query)
        typer.secho(share, fg=typer.colors.GREEN)
    except Exception:
        typer.secho(f"Акция '{query}' не найдена.", fg=typer.colors.YELLOW)
        raise typer.Exit(code=1)


@share_app.command("find")
def share_find(query: str = typer.Argument(..., help="Тикер, название, ISIN, эмитент")):
    """
    Синхронный поиск акций по строке.
    """
    results = find_shares(query)

    if not results:
        typer.secho("Ничего не найдено.", fg=typer.colors.YELLOW)
        raise typer.Exit()

    typer.secho(f"Найдено {len(results)} записей:", fg=typer.colors.GREEN)
    for result in results:
        typer.echo(f" - {result}")


@share_app.command("divs")
def share_divs(query: str = typer.Argument(..., help="Тикер, название, ISIN, эмитент")):
    """
    Синхронный поиск дивидендов по строке.
    """
    results = get_dividends(query)

    if not results:
        typer.secho("Дивиденды не найдены.", fg=typer.colors.YELLOW)
        raise typer.Exit()

    typer.secho(f"Найдено {len(results)} записей:", fg=typer.colors.GREEN)
    for div in results:
        typer.echo(f" - {div}")


# ОБЛИГАЦИИ
@bond_app.command("info")
def bond_info(query: str = typer.Argument(..., help="Тикер, название, ISIN, эмитент")):
    """
    Синхронный поиск информации об облигации по строке.
    """

    try:
        bond = get_bond(query)
        typer.secho(bond, fg=typer.colors.GREEN)
    except Exception:
        typer.secho(f"Облигация '{query}' не найдена.", fg=typer.colors.YELLOW)
        raise typer.Exit(code=1)


@bond_app.command("find")
def bond_find(query: str = typer.Argument(..., help="Тикер, название, ISIN, эмитент")):
    """
    Синхронный поиск облигаций по строке.
    """
    results = find_bonds(query)

    if not results:
        typer.secho("Ничего не найдено.", fg=typer.colors.YELLOW)
        raise typer.Exit()

    typer.secho(f"Найдено {len(results)} записей:", fg=typer.colors.GREEN)
    for result in results:
        typer.echo(f" - {result}")


@bond_app.command("coupons")
def bond_coupons(
    query: str = typer.Argument(..., help="Тикер, название, ISIN, эмитент"),
):
    """
    Синхронный поиск купонов облигации по строке.
    """
    results = get_coupons(query)

    if not results:
        typer.secho("Купоны не найдены.", fg=typer.colors.YELLOW)
        raise typer.Exit()

    typer.secho(f"Найдено {len(results)} записей:", fg=typer.colors.GREEN)
    for result in results:
        typer.echo(f" - {result}")


if __name__ == "__main__":
    app()
