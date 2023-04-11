from __future__ import annotations

import pathlib
from typing import TypedDict

from .manifests import Modification, get_manifest
from .yaml import yaml


class ManifestConfig(TypedDict):
    path: str
    type: str
    labels: list[str]
    repositories: list[str]


class EnvironmentConfig(TypedDict):
    name: str
    manifests: list[ManifestConfig]


class ConfigData(TypedDict):
    environments: list[EnvironmentConfig]


class Nautikos:
    def __init__(self) -> None:
        self._workdir: pathlib.Path = pathlib.Path(".")
        self._dry_run: bool = False
        self._environments: list[EnvironmentConfig] = []
        self._modifications: list[Modification] = []

    @property
    def modifications(self) -> list[Modification]:
        return self._modifications

    def set_dry_run(self, dry_run: bool) -> None:
        self._dry_run = dry_run

    def load_config(self, path: str) -> None:
        self._workdir = pathlib.Path(path).parent
        with open(path, "r") as f:
            config_data: ConfigData = yaml.load(f)
        self._environments = config_data["environments"]

    def update_manifests(
        self,
        repository: str,
        new_tag: str,
        environment: str | None = None,
        labels: list[str] | None = None,
    ) -> None:
        """Updates image tags of given repository to new tag

        If environment is passed, only environments with matching name are modified;
        otherwise all environments are modified.

        If label is passed, only manifests with matching label are modified; otherwise
        all manifests in selected environments are modified.
        """
        # Get all relevant environments
        environments = self._get_environments(environment)

        # Get all relevant manifests
        manifests: list[ManifestConfig] = []
        for env in environments:
            manifests += self._get_manifests(env, labels)

        # Modify manifests
        for manifest_config in manifests:
            manifest = get_manifest(
                manifest_config["path"],
                manifest_config["type"],
                workdir=self._workdir,
            )
            manifest.load()
            manifest.modify(repository, new_tag)
            if len(manifest.modifications) > 0:
                if not self._dry_run:
                    manifest.write()
            self._modifications += manifest.modifications

    def _get_environments(self, environment: str | None) -> list[EnvironmentConfig]:
        envs: list[EnvironmentConfig] = []
        for env in self._environments:
            if not environment or env["name"] == environment:
                envs.append(env)
        return envs

    def _get_manifests(
        self, env: EnvironmentConfig, labels: list[str] | None = None
    ) -> list[ManifestConfig]:
        manifests: list[ManifestConfig] = []
        for manifest in env["manifests"]:
            if not labels or (
                "labels" in manifest and set(labels).issubset(set(manifest["labels"]))
            ):
                manifests.append(manifest)
        return manifests
