import typer


def print_not_found(message: str = "Ничего не найдено.") -> None:
    typer.secho(message=message, fg=typer.colors.YELLOW)
    raise typer.Exit()


def print_items[T](items: list[T], title: str = "Найдено") -> None:
    if not items:
        print_not_found()

    typer.secho(message=f"{title} {len(items)} записей:", fg=typer.colors.GREEN)

    for item in items:
        typer.echo(message=f" - {item}")


def print_error(message: str, code: int = 1) -> None:
    typer.secho(message=message, fg=typer.colors.YELLOW)
    raise typer.Exit(code=code)


def print_success(value: object) -> None:
    typer.secho(message=str(value), fg=typer.colors.GREEN)
