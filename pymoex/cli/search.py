from typing import Annotated

import typer

from pymoex.api import find
from pymoex.cli.output import print_items
from pymoex.models.enums import InstrumentType
from pymoex.models.search import Search


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

    print_items(results)
