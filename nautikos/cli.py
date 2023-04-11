import sys

import typer

from .nautikos import Nautikos

app = typer.Typer()

nautikos = Nautikos()


@app.command()
def main(
    repository: str,
    tag: str,
    env: str = typer.Option(None),
    labels: str = typer.Option(None),
    config: str = typer.Option("nautikos.yaml"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    s = f"Updating '{repository}' to '{tag}'"
    if env:
        s += f" in '{env}'"
    else:
        s += " in all environments"
    if labels:
        s += f" with labels '{labels}'"
    print(s)

    nautikos.set_dry_run(dry_run)
    nautikos.load_config(config)
    nautikos.update_manifests(
        repository, tag, environment=env, labels=labels.split(",") if labels else None
    )

    # Print modified files
    count_updated_img = 0
    for mod in nautikos.modifications:
        print(mod)
        if mod.updated:
            count_updated_img += 1

    # Determine output
    if len(nautikos.modifications) == 0:
        exit_msg = "ERROR - Didn't find any images to modify"
        exit_code = 1
    else:
        exit_msg = f"Updated {count_updated_img} out of {len(nautikos.modifications)} discovered occurances of '{repository}' to '{tag}'"  # noqa: E501
        exit_code = 0
    print(exit_msg)
    sys.exit(exit_code)
