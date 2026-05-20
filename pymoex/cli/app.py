import typer
from typer.main import Typer

from pymoex.cli.bonds import bond_app
from pymoex.cli.currency import currency
from pymoex.cli.search import search
from pymoex.cli.shares import share_app

app: Typer = typer.Typer(help="Утилита для работы с данными Московской биржи")

app.add_typer(typer_instance=share_app, name="share")
app.add_typer(typer_instance=bond_app, name="bond")

_ = app.command(name="search")(search)
_ = app.command(name="currency")(currency)
