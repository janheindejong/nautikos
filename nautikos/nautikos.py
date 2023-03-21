import typer
import yaml

app = typer.Typer()


@app.command()
def main(
    image: str, 
    tag: str, 
    env: str = typer.Option(None), 
    dry_run: bool = typer.Option(False, "--dry-run"),
    config: str = typer.Option("nautikos.yaml")
): 
    config_data = _parse_yaml(config) 
    print(config_data)



def _parse_yaml(filepath: str) -> dict:
    with open(filepath, "r") as f: 
        data = yaml.safe_load(f.read())
    return data 