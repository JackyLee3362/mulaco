import typer

cli = typer.Typer()


@cli.command()
def hello(name: str):
    print(f"hello, {name}")


@cli.command(name="path-info")
def info():
    print(f"hello, this {__name__}")
