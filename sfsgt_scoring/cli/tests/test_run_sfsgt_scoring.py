from unittest import mock

from click import testing as click_testing

from .. import run_sfsgt_scoring


@mock.patch.object(run_sfsgt_scoring.course_database, "load_default_database", autospec=True)
@mock.patch.object(run_sfsgt_scoring.season_spreadsheet, "SeasonSheet")
@mock.patch.object(run_sfsgt_scoring.runner, "SeasonRunner", autospec=True)
@mock.patch.object(run_sfsgt_scoring.season_config, "load_season_config", autospec=True)
def test_cli_nominal(
    spy_load_season_config: mock.MagicMock,
    spy_season_runner: mock.MagicMock,
    spy_season_sheet: mock.MagicMock,
    spy_load_default_database: mock.MagicMock,
) -> None:
    stub_season_config = mock.MagicMock(spec=run_sfsgt_scoring.season_config.SeasonConfig)
    spy_load_season_config.return_value = stub_season_config

    test_args = ["--season", "test_season_name"]
    result = invoke_cli(test_args)
    check_cli_pass(result)

    spy_load_season_config.assert_called_once_with("test_season_name")
    spy_season_sheet.assert_called_once_with()
    spy_load_default_database.assert_called_once_with()
    spy_season_runner.assert_called_once_with(
        config=spy_load_season_config.return_value,
        sheet=spy_season_sheet.return_value,
        course_db=spy_load_default_database.return_value,
    )


def test_cli_missing_season_fails() -> None:
    test_args: list[str] = []
    result = invoke_cli(test_args)
    check_cli_fail(result, expected_output="Missing option '--season'")


def test_cli_unknown_option_fails() -> None:
    test_args = [
        "--not_a_known_option"
    ]
    result = invoke_cli(test_args)
    check_cli_fail(result, expected_output="No such option: --not_a_known_option")


def invoke_cli(test_args: list[str]) -> click_testing.Result:
    result = click_testing.CliRunner().invoke(
        cli=run_sfsgt_scoring.cli,
        args=test_args,
        catch_exceptions=False,
    )
    return result


def check_cli_pass(result: click_testing.Result) -> None:
    assert result.exit_code == 0, f"CLI did not exit successfully. CLI output:\n\n{result.output}"


def check_cli_fail(result: click_testing.Result, expected_output: str | None = None) -> None:
    assert result.exit_code != 0, "CLI call succeeded, but was expected to fail."
    if expected_output is not None:
        assert expected_output in result.output

