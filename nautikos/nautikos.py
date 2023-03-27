from __future__ import annotations

import os
import pathlib
import sys
from typing import TypedDict

from .manifests import get_manifest
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
        # Create list of environments
        envs: list[EnvironmentConfig] = []
        for env in self._environments:
            if not environment or env["name"] == environment:
                envs.append(env)
        if len(envs) == 0:
            raise Exception(f"Oops! No environments with name '{environment}' found...")

        # Create list of manifests
        manifests: list[ManifestConfig] = []
        for env in envs:
            for manifest in env["manifests"]:
                if not labels or (
                    "labels" in manifest
                    and set(labels).issubset(set(manifest["labels"]))
                ):
                    manifests.append(manifest)
        if len(manifest) == 0:
            raise Exception(
                f"Oops!! No manifest found; environment={environment}"
                f"labels={labels}"
            )

        # Modify manifests
        for manifest_config in manifests:
            self._modify_manifest(
                manifest_config["type"],
                manifest_config["path"],
                repository,
                new_tag,
            )

    def _modify_manifest(self, type: str, path: str, repository: str, tag: str) -> None:
        manifest = get_manifest(type)
        with open(os.path.join(self._workdir, pathlib.Path(path)), "r") as s:
            manifest.load(s)
        manifest.modify(repository, tag)
        if self._dry_run:
            manifest.write(sys.stdout)
        else:
            with open(os.path.join(self._workdir, pathlib.Path(path)), "w") as s:
                manifest.write(s)
                print(self._log_string(repository, tag, pathlib.Path(path)))

    @staticmethod
    def _log_string(repository: str, tag: str, path: str | pathlib.Path) -> str:
        return f"Modified tag for {repository} to {tag} in {path}"
