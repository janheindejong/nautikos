from unittest.mock import MagicMock

from typer.testing import CliRunner

from nautikos import cli

runner = CliRunner()


mock_set_dry_run = MagicMock()
mock_load_config = MagicMock()
mock_update_manifests = MagicMock()

cli.nautikos.set_dry_run = mock_set_dry_run  # type: ignore
cli.nautikos.load_config = mock_load_config  # type: ignore
cli.nautikos.update_manifests = mock_update_manifests  # type: ignore


def test_app():
    result = runner.invoke(
        cli.app,
        ["repo-a", "1.2.3", "--env", "prod", "--labels", "app1,app2", "--dry-run"],
    )
    mock_set_dry_run.assert_called_once_with(True)
    mock_load_config.assert_called_once_with("nautikos.yaml")
    mock_update_manifests.assert_called_once_with(
        "repo-a", "1.2.3", environment="prod", labels=["app1", "app2"]
    )
    assert result.exit_code == 0
