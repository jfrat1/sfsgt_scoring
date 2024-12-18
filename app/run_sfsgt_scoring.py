"""CLI to executing scoring for a SFSGT Season.

This should be used as the main entry point for executing season scoring
in a production context.
"""

import click

import courses
import season_config
from sfsgt_scoring import (
    runner,
)
from sfsgt_scoring.spreadsheet import season as season_spreadsheet


@click.command()
@click.option("--season", "season_name", required=True, help="Season to be executed.")
def cli(season_name: str) -> None:
    season_cfg = season_config.load_season_config(season_name)
    sheet = season_spreadsheet.SeasonSheet()
    course_provider = courses.build_default_concrete_course_provider()
    season_runner = runner.SeasonRunner(
        config=season_cfg,
        sheet=sheet,
        course_provider=course_provider,
    )
    season_runner.run()


if __name__ == "__main__":
    cli()
