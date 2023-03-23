import io

import pytest

from nautikos.manifests import KustomizeManifest

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
  newTag: '1.2.3'

patchesStrategicMerge:
- ingress.yml
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
def manifest(input_file: io.StringIO) -> KustomizeManifest:
    manifest = KustomizeManifest()
    manifest.load(input_file)
    return manifest


class TestKustomizeManifest:
    @pytest.fixture(autouse=True, scope="class")
    def modify(self, manifest: KustomizeManifest):
        manifest.modify(REPOSITORY, TAG)

    @pytest.fixture(autouse=True, scope="class")
    def write(self, manifest: KustomizeManifest, output_file):
        manifest.write(output_file)

    def test_tag_applied_correctly(self, manifest: KustomizeManifest):
        assert manifest.get_images()[0] == {
            "repository": REPOSITORY,
            "tag": TAG,
        }

    def test_different_image_untouched(self, manifest: KustomizeManifest):
        assert manifest.get_images()[1] == {
            "repository": "some-other-repository",
            "tag": "1.2.3",
        }    

    def test_write(self, output_file: io.StringIO):
        assert output_file.getvalue() == OUTPUT
