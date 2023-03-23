from __future__ import annotations

import sys
from typing import TypedDict

from .manifests import get_manifest


class ManifestConfig(TypedDict):
    path: str
    type: str
    repositories: list[str]


class EnvironmentConfig(TypedDict):
    name: str
    manifests: list[ManifestConfig]


def apply_new_tag(
    env: EnvironmentConfig, repository: str, tag: str, dry_run: bool = True
) -> None:
    for manifest_config in env["manifests"]:
        if (
            len(manifest_config["repositories"]) > 0
            and repository not in manifest_config["repositories"]
        ):
            continue
        manifest = get_manifest(manifest_config["type"])
        with open(manifest_config["path"], "r") as s:
            manifest.load(s)
        manifest.modify(repository, tag)
        if dry_run:
            manifest.write(sys.stdout)
        else:
            with open(manifest_config["path"], "w") as s:
                manifest.write(s)
                print(
                    f"Modified tag for {repository}"
                    f" to {tag} in {manifest_config['path']}"
                )
