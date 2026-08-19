def main() -> None:
    try:
        from pymoex.cli.app import app
    except ModuleNotFoundError as exc:
        if exc.name == "typer":
            raise SystemExit(
                'CLI dependencies are not installed.\nRun: uv add "pymoex[cli]"'
            ) from exc

        raise

    app()


if __name__ == "__main__":
    main()
