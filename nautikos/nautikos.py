import abc
from enum import Enum
from typing import TextIO, TypedDict

import typer
import yaml
from rich import print

app = typer.Typer()


class ManifestType(Enum):
    KUBERNETES = "kubernetes"
    KUSTOMIZE = "kustomize"
    HELM = "helm"


class Manifest(TypedDict):
    path: str
    type: ManifestType


class Environment(TypedDict):
    name: str
    manifests: list[str]


class ImageConfig(TypedDict):
    repository: str
    environments: list[Environment]


class Config(TypedDict):
    images: list[ImageConfig]


class Image(TypedDict):
    repository: str
    tag: str


class KubernetesContainer(TypedDict):
    image: str


@app.command()
def main(
    image: str,
    tag: str,
    env: str = typer.Option(None),
    dry_run: bool = typer.Option(False, "--dry-run"),
    config: str = typer.Option("nautikos.yaml"),
):
    config_data = _read_config(config)
    print(config_data)


def _read_config(filepath: str) -> Config:
    with open(filepath, "r") as f:
        data = yaml.safe_load(f.read())
    return data


class AbstractManifest(abc.ABC):
    def load(self, stream: TextIO) -> None:
        self._manifest = yaml.safe_load(stream)

    def write(self, stream: TextIO) -> None:
        stream.write(self.__str__())

    @property
    def manifest(self) -> str:
        if self._manifest:
            return self._manifest
        else:
            raise Exception("You must first load a manifest")

    @abc.abstractmethod
    def modify(self, repository: str, tag: str) -> str:
        ...

    @abc.abstractmethod
    def get_images(self) -> list[Image]:
        ...

    def __str__(self) -> str:
        return yaml.dump(self.manifest)


class KubernetesManifest(AbstractManifest):
    def modify(self, repository: str, tag: str) -> None:
        containers = self._get_containers()
        for container in containers:
            image = self._parse_image(container["image"])
            if image["repository"] == repository:
                image["tag"] = tag
                container["image"] = self._unparse_image(image)

    def get_images(self) -> list[Image]:
        return [
            self._parse_image(container["image"])
            for container in self._get_containers()
        ]

    def _get_containers(self) -> list[KubernetesContainer]:
        return self.manifest["spec"]["template"]["spec"]["containers"]

    def _parse_image(self, image: str) -> Image:
        if ":" in image: 
            repository, tag = tuple(image.split(":"))
        else: 
            repository, tag = image, None
        return Image(repository=repository, tag=tag)

    def _unparse_image(self, image: Image) -> str:
        return f"{image['repository']}:{image['tag']}"
