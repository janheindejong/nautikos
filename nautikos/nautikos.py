from typing import Any, TypedDict

import typer
import yaml

app = typer.Typer()


class Environment(TypedDict):
    name: str
    manifests: list[str]


class Image(TypedDict):
    repository: str
    environments: list[Environment]


class Config(TypedDict):
    images: list[Image]


@app.command()
def main(
    image: str,
    tag: str,
    env: str = typer.Option(None),
    dry_run: bool = typer.Option(False, "--dry-run"),
    config: str = typer.Option("nautikos.yaml"),
):
    config_data = _parse_yaml(config)
    print(config_data)

    # For image in images:
    # For environment
    # For file in files
    # Detect type
    # Replace or print


def _read_config(config: str) -> Config:
    return _parse_yaml(config)


def _parse_yaml(filepath: str) -> Any:
    with open(filepath, "r") as f:
        data = yaml.safe_load(f.read())
    return data
