from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner

from nautikos import cli
from nautikos.manifests import Modification
from nautikos.nautikos import Nautikos

runner = CliRunner()


@pytest.fixture()
def mocked_nautikos():
    mock_set_dry_run = MagicMock()
    mock_load_config = MagicMock()
    mock_update_manifests = MagicMock()
    cli.nautikos.set_dry_run = mock_set_dry_run  # type: ignore
    cli.nautikos.load_config = mock_load_config  # type: ignore
    cli.nautikos.update_manifests = mock_update_manifests  # type: ignore
    return cli.nautikos


def test_app(mocked_nautikos: Nautikos):
    mocked_nautikos._modifications = [
        Modification(path="", repository="", previous="1", new="2")
    ]
    result = runner.invoke(
        cli.app,
        ["repo-a", "1.2.3", "--env", "prod", "--labels", "app1,app2", "--dry-run"],
    )
    mocked_nautikos.set_dry_run.assert_called_once_with(True)  # type: ignore
    mocked_nautikos.load_config.assert_called_once_with("nautikos.yaml")  # type: ignore
    mocked_nautikos.update_manifests.assert_called_once_with(  # type: ignore
        "repo-a", "1.2.3", environment="prod", labels=["app1", "app2"]
    )
    assert result.exit_code == 0


def test_no_mods(mocked_nautikos: Nautikos):
    mocked_nautikos._modifications = []
    result = runner.invoke(
        cli.app,
        ["repo-a", "1.2.3", "--env", "prod", "--labels", "app1,app2", "--dry-run"],
    )
    mocked_nautikos.set_dry_run.assert_called_once_with(True)  # type: ignore
    mocked_nautikos.load_config.assert_called_once_with("nautikos.yaml")  # type: ignore
    mocked_nautikos.update_manifests.assert_called_once_with(  # type: ignore
        "repo-a", "1.2.3", environment="prod", labels=["app1", "app2"]
    )
    assert result.exit_code == 1


def test_no_update(mocked_nautikos: Nautikos):
    mocked_nautikos._modifications = [
        Modification(path="", repository="", previous="1", new="1")
    ]
    result = runner.invoke(
        cli.app,
        ["repo-a", "1.2.3", "--env", "prod", "--labels", "app1,app2", "--dry-run"],
    )
    mocked_nautikos.set_dry_run.assert_called_once_with(True)  # type: ignore
    mocked_nautikos.load_config.assert_called_once_with("nautikos.yaml")  # type: ignore
    mocked_nautikos.update_manifests.assert_called_once_with(  # type: ignore
        "repo-a", "1.2.3", environment="prod", labels=["app1", "app2"]
    )
    assert result.exit_code == 0
