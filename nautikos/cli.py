from typing import TypedDict

import typer

from .nautikos import EnvironmentConfig, apply_new_tag
from .yaml import yaml

app = typer.Typer()


class ConfigData(TypedDict):
    environments: list[EnvironmentConfig]


@app.command()
def main(
    repository: str,
    tag: str,
    env: str = typer.Option(None),
    dry_run: bool = typer.Option(False, "--dry-run"),
    config: str = typer.Option("nautikos.yaml"),
):
    with open(config, "r") as f:
        config_data: ConfigData = yaml.load(f)
        environment: EnvironmentConfig = None
        for env in config_data["environments"]:
            if env["name"] == env:
                environment = env
                break
        if not environment:
            raise Exception(f"Environment '{env}' not found in config file")
        apply_new_tag(environment, repository, tag, dry_run)
