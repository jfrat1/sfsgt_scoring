"""CLI to executing scoring for a SFSGT Season.

This should be used as the main entry point for executing season scoring
in a production context.
"""

import click

import courses
import season_config
import season_controller
import season_model
import season_view
from sfsgt_scoring import (
    runner,
)
from sfsgt_scoring.spreadsheet import season as season_spreadsheet


def run_prod_mode_app(season_name: str) -> None:
    season_cfg = season_config.load_season_config(season_name)
    sheet = season_spreadsheet.SeasonSheet()
    course_provider = courses.build_default_concrete_course_provider()
    season_runner = runner.SeasonRunner(
        config=season_cfg,
        sheet=sheet,
        course_provider=course_provider,
    )
    season_runner.run()

def run_dev_mode_app(season_name: str) -> None:
    season_cfg = season_config.load_season_config(season_name)
    course_provider = courses.build_default_concrete_course_provider()
    model = season_model.ConcreteSeasonModel()
    view_config = season_view.GoogleSheetSeasonViewConfig()
    view = season_view.GoogleSheetSeasonView(config=view_config)

    controller = season_controller.SeasonController(
        model=model,
        view=view,
        config=season_cfg,
        course_provider=course_provider,
    )
    print(f"Running season `{season_name}` in dev mode.")

@click.command()
@click.option("--season", "season_name", required=True, help="Season to be executed.")
@click.option(
    "--dev-mode",
    "is_dev_mode",
    is_flag=True,
    default=False,
    help="Use development mode. Behavior may vary, see source code for details.",
)
def cli(season_name: str, is_dev_mode: bool) -> None:
    if is_dev_mode:
        run_dev_mode_app(season_name=season_name)
    else:
        run_prod_mode_app(season_name=season_name)

if __name__ == "__main__":
    cli()
