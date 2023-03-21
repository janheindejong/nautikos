import typer

app = typer.Typer()


@app.callback()
def main(
    image: str, 
    env: str, 
    tag: str, 
    dry_run: bool = typer.Option(False, "--dry-run")
): 
    ... 
