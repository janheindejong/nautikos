import os
import tempfile
from typing import Generator

import pytest

from nautikos.manifests import KubernetesManifest, Modification

INPUT = """# Comment
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: kubernetes-example
  name: kubernetes-example
spec:
  replicas: 3
  selector:
    matchLabels:
      app: kubernetes-example
  template:
    metadata:
      labels:
        app: kubernetes-example
    spec:
      containers:
      - image: some-repository:1.0.0 # Inline comment
        name: service-kubernetes-example-1 
        ports:
        - containerPort: 8000
      - image: some-repository
        name: service-kubernetes-example-2
      - image: some-other-repository:1.2.3
        name: some-other-service
"""

OUTPUT = """# Comment
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: kubernetes-example
  name: kubernetes-example
spec:
  replicas: 3
  selector:
    matchLabels:
      app: kubernetes-example
  template:
    metadata:
      labels:
        app: kubernetes-example
    spec:
      containers:
      - image: some-repository:1.1   # Inline comment
        name: service-kubernetes-example-1
        ports:
        - containerPort: 8000
      - image: some-repository:1.1
        name: service-kubernetes-example-2
      - image: some-other-repository:1.2.3
        name: some-other-service
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
def manifest(file_path: str) -> KubernetesManifest:
    manifest = KubernetesManifest(file_path)
    return manifest


class TestKubernetesManifest:
    @pytest.fixture(autouse=True, scope="class")
    def modify(self, manifest: KubernetesManifest):
        manifest.load()
        manifest.modify("some-repository", "1.1")
        manifest.write()

    def test_modifications(self, manifest: KubernetesManifest, file_path: str):
        assert manifest.modifications == [
            Modification(
                path=file_path,
                repository="some-repository",
                previous="1.0.0",
                new="1.1",
            ),
            Modification(
                path=file_path,
                repository="some-repository",
                previous="",
                new="1.1",
            ),
        ]

    def test_write(self, file_path: str):
        with open(file_path, "r") as f:
            s = f.read()
        assert s == OUTPUT
