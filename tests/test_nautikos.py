import os
import tempfile
from typing import Generator, TypedDict

import pytest
from ruamel.yaml import YAML

from nautikos.nautikos import Nautikos

CONFIG_FILE = """environments: 
- name: prod 
  manifests: 
  - path: prod/app1/deployment.yaml  # Path relative to configuration file
    type: kubernetes  # Type can be 'kubernetes' or 'kustomize'
    labels: 
    - app1
    - refs/head/main
  - path: prod/app2/kustomize.yaml
    type: kustomize
- name: dev
  manifests: 
  - path: dev/app1/deployment.yaml
    type: kubernetes
    labels: 
    - app1
    - refs/head/dev
  - path: dev/app1/feature-A/deployment.yaml
    type: kubernetes
    labels: 
    - app1
    - refs/head/feature-A
"""
KUBERNETES_MANIFEST = """spec:
  template:
    spec:
      containers:
      - image: my-repo:1.0
      - image: my-other-repo:1.0
      - image: some-other-repo:1.0
"""
KUSTOMIZE_MANIFEST = """images:
- name: my-repo
  newTag: 1.0
- name: my-other-repo
  newTag: 1.0
- name: some-other-repo
  newTag: 1.0
"""


yaml = YAML()


@pytest.fixture(scope="class")
def workdir() -> Generator[str, None, None]:
    with tempfile.TemporaryDirectory() as workdir:
        yield workdir


@pytest.fixture(autouse=True, scope="class")
def prepare_workdir(workdir: str) -> None:
    create_file(workdir, "nautikos.yaml", CONFIG_FILE)
    create_file(
        os.path.join(workdir, "prod", "app1"),
        "deployment.yaml",
        KUBERNETES_MANIFEST,
    )
    create_file(
        os.path.join(workdir, "prod", "app2"), "kustomize.yaml", KUSTOMIZE_MANIFEST
    )
    create_file(
        os.path.join(workdir, "dev", "app1"), "deployment.yaml", KUBERNETES_MANIFEST
    )
    create_file(
        os.path.join(workdir, "dev", "app1", "feature-A"),
        "deployment.yaml",
        KUBERNETES_MANIFEST,
    )


def create_file(dir, name, content) -> None:
    try:
        os.makedirs(dir)
    except FileExistsError:
        ...
    path = os.path.join(dir, name)
    with open(path, "w") as f:
        f.write(content)


@pytest.fixture(scope="class")
def nautikos(workdir: str):
    nautikos = Nautikos()
    nautikos.set_dry_run(False)
    nautikos.load_config(os.path.join(workdir, "nautikos.yaml"))
    return nautikos


class Tags(TypedDict):
    prod_app_1: tuple[str, str, str]
    prod_app_2: tuple[str, str, str]
    dev_app_1: tuple[str, str, str]
    dev_app_1_feature_a: tuple[str, str, str]


class BaseTest:
    TAGS: Tags

    def _test_kustomize_manifest(
        self, path: tuple[str, ...], tags: tuple[str, str, str]
    ) -> None:
        with open(os.path.join(*path), "r") as f:
            data = yaml.load(f)
        for i in range(3):
            assert str(data["images"][i]["newTag"]) == tags[i]

    def _test_k8s_manifest(
        self, path: tuple[str, ...], tags: tuple[str, str, str]
    ) -> None:
        with open(os.path.join(*path), "r") as f:
            data = yaml.load(f)
        imgs = (
            f"my-repo:{tags[0]}",
            f"my-other-repo:{tags[1]}",
            f"some-other-repo:{tags[2]}",
        )
        for i in range(3):
            assert data["spec"]["template"]["spec"]["containers"][i]["image"] == imgs[i]

    def test_prod_app1(self, workdir: str) -> None:
        path = (workdir, "prod", "app1", "deployment.yaml")
        self._test_k8s_manifest(path, self.TAGS["prod_app_1"])

    def test_prod_app2(self, workdir: str) -> None:
        path = (workdir, "prod", "app2", "kustomize.yaml")
        self._test_kustomize_manifest(path, self.TAGS["prod_app_2"])

    def test_dev_app1(self, workdir: str) -> None:
        path = (workdir, "dev", "app1", "deployment.yaml")
        self._test_k8s_manifest(path, self.TAGS["dev_app_1"])

    def test_dev_app1_feature_a(self, workdir: str) -> None:
        path = (workdir, "dev", "app1", "feature-A", "deployment.yaml")
        self._test_k8s_manifest(path, self.TAGS["dev_app_1_feature_a"])


class TestModifyAll(BaseTest):
    TAGS = {
        "prod_app_1": ("1.2.3", "1.0", "1.0"),
        "prod_app_2": ("1.2.3", "1.0", "1.0"),
        "dev_app_1": ("1.2.3", "1.0", "1.0"),
        "dev_app_1_feature_a": ("1.2.3", "1.0", "1.0"),
    }

    @pytest.fixture(autouse=True, scope="class")
    def modify(self, nautikos: Nautikos) -> None:
        nautikos.update_manifests("my-repo", "1.2.3")


class TestModifyProd(BaseTest):
    TAGS = {
        "prod_app_1": ("1.2.3", "1.0", "1.0"),
        "prod_app_2": ("1.2.3", "1.0", "1.0"),
        "dev_app_1": ("1.0", "1.0", "1.0"),
        "dev_app_1_feature_a": ("1.0", "1.0", "1.0"),
    }

    @pytest.fixture(autouse=True, scope="class")
    def modify(self, nautikos: Nautikos) -> None:
        nautikos.update_manifests("my-repo", "1.2.3", environment="prod")


class TestModifyProdApp1(BaseTest):
    TAGS = {
        "prod_app_1": ("1.2.3", "1.0", "1.0"),
        "prod_app_2": ("1.0", "1.0", "1.0"),
        "dev_app_1": ("1.0", "1.0", "1.0"),
        "dev_app_1_feature_a": ("1.0", "1.0", "1.0"),
    }

    @pytest.fixture(autouse=True, scope="class")
    def modify(self, nautikos: Nautikos) -> None:
        nautikos.update_manifests(
            "my-repo", "1.2.3", environment="prod", labels=["app1"]
        )


class TestModifyMultipleLabels(BaseTest):
    TAGS = {
        "prod_app_1": ("1.0", "1.0", "1.0"),
        "prod_app_2": ("1.0", "1.0", "1.0"),
        "dev_app_1": ("1.2.3", "1.0", "1.0"),
        "dev_app_1_feature_a": ("1.0", "1.0", "1.0"),
    }

    @pytest.fixture(autouse=True, scope="class")
    def modify(self, nautikos: Nautikos) -> None:
        nautikos.update_manifests("my-repo", "1.2.3", labels=["app1", "refs/head/dev"])
