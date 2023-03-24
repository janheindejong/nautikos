import typer

from .nautikos import Nautikos

app = typer.Typer()


@app.command()
def main(
    repository: str,
    tag: str,
    env: str = typer.Option(None),
    config: str = typer.Option("nautikos.yaml"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    nautikos = Nautikos()
    nautikos.set_dry_run(dry_run)
    nautikos.load_config(config)
    nautikos.update_manifests(env, repository, tag)
