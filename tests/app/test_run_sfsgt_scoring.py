from app import run_sfsgt_scoring
from click import testing as click_testing


def test_cli_missing_season_fails() -> None:
    test_args: list[str] = []
    result = invoke_cli(test_args)
    check_cli_fail(result, expected_output="Missing option '--season'")


def test_cli_unknown_option_fails() -> None:
    test_args = ["--not_a_known_option"]
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
