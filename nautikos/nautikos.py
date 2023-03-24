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
        self._manifest_configs: dict[str, list[ManifestConfig]] = {}

    def set_dry_run(self, dry_run: bool) -> None:
        self._dry_run = dry_run

    def load_config(self, path: str) -> None:
        self._workdir = pathlib.Path(path).parent
        with open(path, "r") as f:
            config_data: ConfigData = yaml.load(f)
        self._manifest_configs = {
            env["name"]: env["manifests"] for env in config_data["environments"]
        }

    def update_manifests(self, environment: str, repository: str, new_tag: str) -> None:
        if environment not in self._manifest_configs:
            raise Exception(f"Unknown environment '{environment}'")
        for manifest_config in self._manifest_configs[environment]:
            if self._needs_modification(manifest_config, repository):
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
    def _needs_modification(manifest_config: ManifestConfig, repository: str) -> bool:
        needs_modification = False
        if "repositories" not in manifest_config:
            needs_modification = True
        elif len(manifest_config["repositories"]) == 0:
            needs_modification = True
        elif repository in manifest_config["repositories"]:
            needs_modification = True
        return needs_modification

    @staticmethod
    def _log_string(repository: str, tag: str, path: str | pathlib.Path) -> str:
        return f"Modified tag for {repository} to {tag} in {path}"
