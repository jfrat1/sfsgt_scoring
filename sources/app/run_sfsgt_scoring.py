"""CLI to executing scoring for a SFSGT Season.

This should be used as the main entry point for executing season scoring
in a production context.
"""

import json
import logging
import pathlib
from logging import config as logging_config

import click
import courses
import google_sheet
import gspread
import season_config
import season_controller
import season_model
import season_view

# Get a reference to the root logger
logger = logging.getLogger()

SERVICE_ACCOUNT_CREDENTIALS_FILE = (
    pathlib.Path(__file__).parent.parent.parent / "google_cloud_creds" / "sfsgt-credentials.json"
)

LOGGING_CONFIG_FILE = pathlib.Path(__file__).parent / "logging_config.json"


class GoogleSheetViewConfigGenerator:
    def __init__(self, season_cfg: season_config.SeasonConfig) -> None:
        self._season_cfg = season_cfg

    def generate(self) -> season_view.GoogleSheetSeasonViewConfig:
        ordered_event_names = self._season_cfg.ordered_event_names()
        event_configs = [
            self._generate_event_config(event_num, event_name) for event_num, event_name in ordered_event_names.items()
        ]

        finale_view_config = None
        if (finale_config := self._season_cfg.finale_handicaps_sheet) is not None and finale_config.enabled:
            finale_view_config = season_view.GoogleSheetSeasonViewFinaleConfig(
                workshet_name=finale_config.sheet_name,
                player_names_range=finale_config.player_names_range,
                season_handicap_column=finale_config.season_handicap_column,
                finale_handicap_index_column=finale_config.finale_handicap_index_column,
                course_handicap_column=finale_config.course_handicap_column,
            )

        return season_view.GoogleSheetSeasonViewConfig(
            players_worksheet_name=self._season_cfg.players_sheet_name,
            leaderboard_worksheet_name=self._season_cfg.leaderboard_sheet_name,
            event_worksheet_configs=event_configs,
            finale_config=finale_view_config,
        )

    def _generate_event_config(self, event_num: int, event_name: str) -> season_view.GoogleSheetSeasonViewEventConfig:
        season_event_config = self._season_cfg.get_event_config(event_name)
        return season_view.GoogleSheetSeasonViewEventConfig(
            event_number=event_num,
            event_name=season_event_config.event_name,
            worksheet_name=season_event_config.sheet_name,
            scorecard_start_cell=season_event_config.scorecard_sheet_start_cell,
        )


def setup_logging() -> None:
    config_raw = LOGGING_CONFIG_FILE.read_text()
    config = json.loads(config_raw)

    logging_config.dictConfig(config)


def run_prod_mode_app(season_name: str) -> None:
    logger.debug(f"Loading config for {season_name}")
    season_cfg = season_config.load_season_config(season_name)

    model = season_model.ConcreteSeasonModel()

    logger.debug(f"Creating gspread client with service account credentials from {SERVICE_ACCOUNT_CREDENTIALS_FILE}")
    gspread_client = gspread.service_account(filename=SERVICE_ACCOUNT_CREDENTIALS_FILE)
    google_sheet_controller = google_sheet.ConcreteGoogleSheetController(
        gspread_client=gspread_client,
        sheet_id=season_cfg.sheet_id,
    )

    view_config = GoogleSheetViewConfigGenerator(season_cfg=season_cfg).generate()
    view = season_view.GoogleSheetSeasonView(
        config=view_config,
        sheet_controller=google_sheet_controller,
    )

    course_provider = courses.build_default_concrete_course_provider()

    controller = season_controller.SeasonController(
        model=model,
        view=view,
        config=season_cfg,
        course_provider=course_provider,
    )

    logger.debug("Running season controller")
    controller.run_season()


def run_dev_mode_app(season_name: str) -> None:
    raise NotImplementedError("Dev mode app is not available at this time.")


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
    setup_logging()

    if is_dev_mode:
        logger.info(f"Running dev mode for season {season_name}")
        run_dev_mode_app(season_name=season_name)
    else:
        logger.info(f"🏃🏽‍♀️ Running season {season_name}")
        run_prod_mode_app(season_name=season_name)


if __name__ == "__main__":
    cli()
