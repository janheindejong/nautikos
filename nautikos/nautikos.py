from __future__ import annotations

from typing import TypedDict


class ManifestConfig(TypedDict):
    path: str
    type: str
    repositories: list[str]


class EnvironmentConfig(TypedDict):
    name: str
    manifests: list[str]


class Config(TypedDict):
    environments: list[EnvironmentConfig]


# class ManifestEditor: 

#     def __init__(self, dry_run: bool = False) -> None:
#         self._dry_run = dry_run

#     def edit(self, manifest_config: ManifestConfig, tag: str) -> None: 
#         manifest = _manifest_factory(manifest_config["type"])
#         with open(manifest_config["path"], "r") as s: 
#             manifest.load(s)
#             manifest.modify(repository, tag)
#         if self._dry_run: 
#             manifest.write(sys.stdout)
#         else: 
#             with open(manifest_config["path"], "w") as s:
#                 manifest.write(s)


#     def load(self, configfile: str) -> None: 
#         self._config = self._read_config(configfile)

#     def run(self, repository, tag, env, dry_run=False) -> None: 
#         manifest_configs = self._get_manifest_configs(repository, env)
#         for manifest_config in manifest_configs: 
#             manifest = _manifest_factory(manifest_config["type"])
#             with open(manifest_config["path"], "r") as s: 
#                 manifest.load(s)
#                 manifest.modify(repository, tag)
#             if dry_run: 
#                 print(manifest.data)
#             else: 
#                 with open(manifest_config["path"], "w") as s:
#                     manifest.write(s)

#     def _get_manifest_configs(self, repository: str, env: str) -> list[ManifestConfig]:
#         image = next((image for image in self._config["images"] if image["repository"] == repository), None)
#         if not image: 
#             raise Exception(f"Image {image} is not in configuration file")
#         environment = next((environment for environment in image["environments"	] if environment["name"] == env), None)
#         if not environment: 
#             raise Exception(f"Environment {env} is not in configuration file")
#         return environment["manifests"]
    
                
#     @staticmethod
#     def _read_config(filepath: str) -> Config:
#         with open(filepath, "r") as f:
#             data = yaml.load(f.read())
#         return data
