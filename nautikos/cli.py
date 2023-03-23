import typer

app = typer.Typer()


@app.command()
def main(
    repository: str,
    tag: str,
    env: str = typer.Option(None),
    dry_run: bool = typer.Option(False, "--dry-run"),
    config: str = typer.Option("nautikos.yaml"),
):
    ...
    
