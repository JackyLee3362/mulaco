import typer

import mulaco

cli = typer.Typer()


@cli.command()
def hello(name: str):
    print(f"hello, {name}")


@cli.command(name="path-info")
def info():
    print(mulaco.PACKAGE_PATH)
    print(mulaco.SRC_PATH)
    print(mulaco.DEFAULT_CONFIG_PATH)
    print(mulaco.DEFAULT_CWD_PATH)
    print(mulaco.DEFAULT_LOG_PATH)
    print(mulaco.DEFAULT_DB_PATH)
