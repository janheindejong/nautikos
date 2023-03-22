import abc
from enum import Enum
from typing import TextIO, TypedDict

import typer
from rich import print
from ruamel.yaml import YAML

app = typer.Typer()

yaml = YAML()
yaml.default_flow_style = False
yaml.preserve_quotes = True


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
        data = yaml.load(f.read())
    return data


class AbstractManifest(abc.ABC):
    def load(self, stream: TextIO) -> None:
        self._data = yaml.load(stream)

    def write(self, stream: TextIO) -> None:
        yaml.dump(self.data, stream)

    @property
    def data(self) -> str:
        if self._data:
            return self._data
        else:
            raise Exception("You must first load a manifest")

    @abc.abstractmethod
    def modify(self, repository: str, new_tag: str) -> str:
        ...

    @abc.abstractmethod
    def get_images(self) -> list[Image]:
        ...


KubernetesImage = str


class KubernetesManifest(AbstractManifest):
    def modify(self, repository: str, new_tag: str) -> None:
        for container in self._get_containers():
            if repository == self._parse_image(container["image"])["repository"]:
                container["image"] = self._unparse_image(
                    {"repository": repository, "tag": new_tag}
                )

    def get_images(self) -> list[Image]:
        return [
            self._parse_image(container["image"])
            for container in self._get_containers()
        ]

    def _get_containers(self) -> list[KubernetesContainer]:
        return self.data["spec"]["template"]["spec"]["containers"]

    def _parse_image(self, image: KubernetesImage) -> Image:
        if ":" in image:
            repository, tag = tuple(image.split(":"))
        else:
            repository, tag = image, None
        return {"repository": repository, "tag": tag}

    def _unparse_image(self, image: Image) -> str:
        return f"{image['repository']}:{image['tag']}"


class KustomizeImage(TypedDict):
    name: str
    newTag: str


class KustomizeManifest(AbstractManifest):
    def modify(self, repository: str, new_tag: str) -> None:
        for kustomize_image in self._data["images"]:
            if repository == kustomize_image["name"]:
                kustomize_image["newTag"] = new_tag

    def get_images(self) -> list[Image]:
        return [self._parse_image(image) for image in self._data["images"]]

    def _parse_image(self, image: KustomizeImage) -> Image:
        return {"repository": image["name"], "tag": image["newTag"]}
