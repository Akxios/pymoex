import typer

from pymoex.api import (
    find_bonds,
    find_shares,
)

app = typer.Typer()


# CLI поиск облигации
@app.command()
def find_bond(query: str = typer.Argument(..., help="Тикер, название, ISIN, эмитент")):
    """
    Синхронный поиск облигаций по строке.
    """
    results = find_bonds(query)

    if not results:
        typer.secho("Облигации не найдены.", fg=typer.colors.YELLOW)
        raise typer.Exit()

    typer.secho(f"Найдено {len(results)} записей:", fg=typer.colors.GREEN)
    for bond in results:
        typer.echo(f" - {bond}")


# CLI поиск акции
@app.command()
def find_share(query: str = typer.Argument(..., help="Тикер, название, ISIN, эмитент")):
    """
    Синхронный поиск акций по строке.
    """
    results = find_shares(query)

    if not results:
        typer.secho("Акции не найдены.", fg=typer.colors.YELLOW)
        raise typer.Exit()

    typer.secho(f"Найдено {len(results)} записей:", fg=typer.colors.GREEN)
    for share in results:
        typer.echo(f" - {share}")


if __name__ == "__main__":
    app()
