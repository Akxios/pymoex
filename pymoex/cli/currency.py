from typing import Annotated

import typer

from pymoex import get_currency
from pymoex.cli.output import print_error
from pymoex.utils.aliases import resolve_currency_secid

currency_app = typer.Typer()


@currency_app.command(name="")
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

        typer.secho(
            message=f"Данные по {query.upper()} ({real_secid}):",
            fg=typer.colors.CYAN,
        )
        typer.secho(message=str(currency_model), fg=typer.colors.GREEN)

    except Exception as e:
        print_error(f"Валюта '{query}' (secid: {real_secid}) не найдена. Причина: {e}")
