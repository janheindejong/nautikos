import os
import tempfile
from typing import Generator

import pytest

from nautikos.nautikos import Nautikos

CONFIG_FILE = """environments:
- name: prod 
  manifests: 
  - path: prod/app1/deployment.yaml
    type: kubernetes
  - path: prod/app2/kustomize.yaml
    type: kustomize
    repositories:
      - repository-b
      - repository-c
- name: dev
  manifests: 
  - path: dev/app3/deployment.yaml
    type: kubernetes
"""

KUBERNETES_MANIFEST = """spec:
  template:
    spec:
      containers:
      - image: repository-a:1.0
      - image: repository-b:2.0
      - image: repository-c:3.0
"""
KUSTOMIZE_MANIFEST = """images:
- name: repository-a
  newTag: 1.0
- name: repository-b
  newTag: 2.0
- name: repository-c
  newTag: 3.0
"""


PROD_APP_ONE_OUTPUT = """spec:
  template:
    spec:
      containers:
      - image: repository-a:1.2.3
      - image: repository-b:4.5.6
      - image: repository-c:3.0
"""

PROD_APP_TWO_OUTPUT = """images:
- name: repository-a
  newTag: 1.0
- name: repository-b
  newTag: 4.5.6
- name: repository-c
  newTag: 3.0
"""

DEV_APP_ONE_OUTPUT = """spec:
  template:
    spec:
      containers:
      - image: repository-a:1.0
      - image: repository-b:2.0
      - image: repository-c:7.8.9
"""


@pytest.fixture(scope="class")
def workdir() -> Generator[str, None, None]:
    with tempfile.TemporaryDirectory() as workdir:
        yield workdir


class TestNautikos:
    @pytest.fixture(autouse=True, scope="class")
    def prepare_workdir(self, workdir: str) -> None:
        _create_file(workdir, "nautikos.yaml", CONFIG_FILE)
        _create_file(
            os.path.join(workdir, "prod", "app1"),
            "deployment.yaml",
            KUBERNETES_MANIFEST,
        )
        _create_file(
            os.path.join(workdir, "prod", "app2"), "kustomize.yaml", KUSTOMIZE_MANIFEST
        )
        _create_file(
            os.path.join(workdir, "dev", "app3"), "deployment.yaml", KUBERNETES_MANIFEST
        )

    @pytest.fixture(scope="class")
    def nautikos(self, workdir: str):
        nautikos = Nautikos()
        nautikos.set_dry_run(False)
        nautikos.load_config(os.path.join(workdir, "nautikos.yaml"))
        return nautikos

    @pytest.fixture(autouse=True, scope="class")
    def update_manifests(self, nautikos: Nautikos):
        nautikos.update_manifests("prod", "repository-a", "1.2.3")
        nautikos.update_manifests("prod", "repository-b", "4.5.6")
        nautikos.update_manifests("dev", "repository-c", "7.8.9")

    def test_prod_app_one(self, nautikos: Nautikos):
        with open(
            os.path.join(nautikos._workdir, "prod", "app1", "deployment.yaml"), "r"
        ) as f:
            output = f.read()
        assert output == PROD_APP_ONE_OUTPUT

    def test_prod_app_two(self, nautikos: Nautikos):
        with open(
            os.path.join(nautikos._workdir, "prod", "app2", "kustomize.yaml"), "r"
        ) as f:
            output = f.read()
        assert output == PROD_APP_TWO_OUTPUT

    def test_dev_app_three(self, nautikos: Nautikos):
        with open(
            os.path.join(nautikos._workdir, "dev", "app3", "deployment.yaml"), "r"
        ) as f:
            output = f.read()
        assert output == DEV_APP_ONE_OUTPUT


def _create_file(dir, name, content) -> None:
    try:
        os.makedirs(dir)
    except FileExistsError:
        ...
    path = os.path.join(dir, name)
    with open(path, "w") as f:
        f.write(content)
