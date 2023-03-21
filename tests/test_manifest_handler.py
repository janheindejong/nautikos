import io

import pytest

from nautikos.nautikos import KubernetesManifest

INPUT = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: kubernetes-example
  labels:
    app: kubernetes-example
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
      - name: service-kubernetes-example-1
        image: kubernetes-example:1.0.0
        ports:
        - containerPort: 8000
      - name: service-kubernetes-example-2
        image: kubernetes-example
      - name: some-other-service
        image: some-other-image:1.2.3
"""

OUTPUT = """apiVersion: apps/v1
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
      - image: kubernetes-example:1.1
        name: service-kubernetes-example-1
        ports:
        - containerPort: 8000
      - image: kubernetes-example:1.1
        name: service-kubernetes-example-2
      - image: some-other-image:1.2.3
        name: some-other-service
"""

REPOSITORY = "kubernetes-example"
TAG = "1.1"


@pytest.fixture(scope="class")
def input_file() -> io.StringIO:
    f = io.StringIO(INPUT)
    return f


@pytest.fixture(scope="class")
def kubernetes_manifest(input_file: io.StringIO) -> KubernetesManifest:
    kubernetes_handler = KubernetesManifest()
    kubernetes_handler.load(input_file)
    return kubernetes_handler


class TestKubernetesHandler:
    @pytest.fixture(autouse=True, scope="class")
    def modify(self, kubernetes_manifest: KubernetesManifest):
        kubernetes_manifest.modify(REPOSITORY, TAG)

    def test_tag_applied_correctly(self, kubernetes_manifest: KubernetesManifest):
        assert kubernetes_manifest.get_images()[0] == {
            "repository": REPOSITORY,
            "tag": TAG,
        }

    def test_no_tag_handled_correctly(self, kubernetes_manifest: KubernetesManifest):
        assert kubernetes_manifest.get_images()[1] == {
            "repository": REPOSITORY,
            "tag": TAG,
        }

    def test_different_image_untouched(self, kubernetes_manifest: KubernetesManifest):
        assert kubernetes_manifest.get_images()[2] == {
            "repository": "some-other-image",
            "tag": "1.2.3",
        }

    def test_text(self, kubernetes_manifest: KubernetesManifest):
        assert OUTPUT == str(kubernetes_manifest)
