from sfsgt_scoring import season_config, season_runner

TEST_SEASON_CONFIG = season_config.SeasonConfig(
    name="test_season",
    sheet_id="test_sheet_id",
    players_sheet_name="Players",
    leaderboard_sheet_name="Leaderboard",
    events={
        1: season_config.config.EventConfig(
            event_name="Standard Event",
            course_name="course_a",
            tee="white",
            type=season_config.config.EventType.STANDARD,
            scorecard_sheet_start_cell="A1",
        ),
        2: season_config.config.EventConfig(
            event_name="Major Event",
            course_name="course_b",
            tee="blue",
            type=season_config.config.EventType.MAJOR,
            scorecard_sheet_start_cell="B5",
        ),
    }
)

# Need to mock out some gspread or season sheet stuff to get this to construct
# def test_construct_season_runner() -> None:
#     runner = season_runner.SeasonRunner(season_cfg=TEST_SEASON_CONFIG)

