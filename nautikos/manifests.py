import abc
import pathlib
from dataclasses import dataclass
from typing import Any, TypedDict

from .yaml import yaml


class Image(TypedDict):
    repository: str
    tag: str | None


@dataclass
class Modification:
    path: str
    repository: str
    previous: str
    new: str

    @property
    def updated(self) -> bool:
        return self.previous != self.new

    def __str__(self) -> str:
        return f"{self.path} -> modified '{self.repository}' (was '{self.previous}')"


class AbstractManifest(abc.ABC):
    def __init__(self, path: str | pathlib.Path) -> None:
        self._path = path
        self._modifications: list[Modification] = []

    @property
    def modifications(self) -> list[Modification]:
        return self._modifications

    def load(self) -> None:
        with open(self._path, "r") as f:
            self._data = yaml.load(f)

    def write(self) -> None:
        with open(self._path, "w") as f:
            yaml.dump(self._data, f)

    @property
    def data(self) -> Any:
        if self._data:
            return self._data
        else:
            raise Exception("You must first load a manifest")

    def _record_modification(
        self, repository: str, old_tag: str | None, new_tag: str
    ) -> None:
        if not old_tag:
            old_tag = ""
        m = Modification(
            path=str(self._path),
            repository=repository,
            previous=str(old_tag),
            new=str(new_tag),
        )
        self._modifications.append(m)

    @abc.abstractmethod
    def modify(self, repository: str, new_tag: str) -> None:
        ...


KubernetesImageDefinition = str


class KubernetesContainer(TypedDict):
    image: KubernetesImageDefinition


class KubernetesManifest(AbstractManifest):
    def modify(self, repository: str, new_tag: str) -> None:
        for container in self._get_containers():
            parsed_image = self._parse_image(container["image"])
            if repository == parsed_image["repository"]:
                container["image"] = self._unparse_image(
                    {"repository": repository, "tag": new_tag}
                )
                self._record_modification(repository, parsed_image["tag"], new_tag)

    def _get_containers(self) -> list[KubernetesContainer]:
        return self.data["spec"]["template"]["spec"]["containers"]

    def _parse_image(self, image: KubernetesImageDefinition) -> Image:
        if ":" in image:
            repository, tag = tuple(image.split(":"))
        else:
            repository, tag = image, None
        return {"repository": repository, "tag": tag}

    def _unparse_image(self, image: Image) -> str:
        return f"{image['repository']}:{image['tag']}"


class KustomizeImageDefinition(TypedDict):
    name: str
    newTag: str


class KustomizeManifest(AbstractManifest):
    def modify(self, repository: str, new_tag: str) -> None:
        if "images" in self._data:
            for kustomize_image in self.data["images"]:
                if repository == kustomize_image["name"]:
                    old_tag = kustomize_image["newTag"]
                    kustomize_image["newTag"] = new_tag
                    self._record_modification(repository, old_tag, new_tag)

    def _parse_image(self, image: KustomizeImageDefinition) -> Image:
        return {"repository": image["name"], "tag": image["newTag"]}


def get_manifest(
    path: str | pathlib.Path, type: str, workdir: str | pathlib.Path | None = None
) -> AbstractManifest:
    if workdir:
        path = pathlib.Path(workdir) / pathlib.Path(path)
    if type == "kubernetes":
        return KubernetesManifest(path)
    elif type == "kustomize":
        return KustomizeManifest(path)
    elif type == "helm":
        raise Exception("Helm manifests are not yet implemented.")
    else:
        raise Exception(f"'{type}' is not a correct manifest type.")
