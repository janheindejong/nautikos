import os
import tempfile
from typing import Generator

import pytest

from nautikos.manifests import KustomizeManifest, Modification

INPUT = """# Comment
resources:
- ../some/path
images:
- name: some-repository
  newTag: '1.0.0'
- name: some-other-repository
  newTag: '1.2.3'

patchesStrategicMerge:
- ingress.yml
"""

OUTPUT = """# Comment
resources:
- ../some/path
images:
- name: some-repository
  newTag: '1.1'
- name: some-other-repository
  newTag: 1.2.3

patchesStrategicMerge:
- ingress.yml
"""


@pytest.fixture(scope="class")
def workdir() -> Generator[str, None, None]:
    with tempfile.TemporaryDirectory() as workdir:
        yield workdir


@pytest.fixture(scope="class")
def file_path(workdir: str) -> str:
    path = os.path.join(workdir, "manifest.yaml")
    with open(path, "w") as f:
        f.write(INPUT)
    return path


@pytest.fixture(scope="class")
def manifest(file_path: str) -> KustomizeManifest:
    manifest = KustomizeManifest(file_path)
    return manifest


class TestKustomizeManifest:
    @pytest.fixture(autouse=True, scope="class")
    def modify(self, manifest: KustomizeManifest):
        manifest.load()
        manifest.modify("some-repository", "1.1")
        manifest.write()

    def test_output(self, file_path: str):
        with open(file_path, "r") as f:
            s = f.read()
        assert s == OUTPUT

    def test_modifications(self, manifest: KustomizeManifest, file_path: str):
        assert manifest.modifications == [
            Modification(
                path=file_path,
                repository="some-repository",
                previous="1.0.0",
                new="1.1",
            )
        ]
