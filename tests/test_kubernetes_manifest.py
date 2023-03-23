import io

import pytest

from nautikos.manifests import KubernetesManifest

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

REPOSITORY = "some-repository"
TAG = "1.1"


@pytest.fixture(scope="class")
def input_file() -> io.StringIO:
    f = io.StringIO(INPUT)
    return f


@pytest.fixture(scope="class")
def output_file() -> io.StringIO:
    f = io.StringIO()
    return f


@pytest.fixture(scope="class")
def manifest(input_file: io.StringIO) -> KubernetesManifest:
    kubernetes_handler = KubernetesManifest()
    kubernetes_handler.load(input_file)
    return kubernetes_handler


class TestKubernetesManifest:
    @pytest.fixture(autouse=True, scope="class")
    def modify(self, manifest: KubernetesManifest):
        manifest.modify(REPOSITORY, TAG)

    @pytest.fixture(autouse=True, scope="class")
    def write(self, manifest: KubernetesManifest, output_file):
        manifest.write(output_file)

    def test_tag_applied_correctly(self, manifest: KubernetesManifest):
        assert manifest.get_images()[0] == {
            "repository": REPOSITORY,
            "tag": TAG,
        }

    def test_no_tag_handled_correctly(self, manifest: KubernetesManifest):
        assert manifest.get_images()[1] == {
            "repository": REPOSITORY,
            "tag": TAG,
        }

    def test_different_image_untouched(self, manifest: KubernetesManifest):
        assert manifest.get_images()[2] == {
            "repository": "some-other-repository",
            "tag": "1.2.3",
        }

    def test_write(self, output_file: io.StringIO):
        assert output_file.getvalue() == OUTPUT
