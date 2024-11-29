import pytest

import season_config
from sfsgt_scoring.spreadsheet.season import sheet
from sfsgt_scoring.spreadsheet.season.worksheet import event, players

pytestmark = pytest.mark.integration


def test_sheet_read() -> None:
    # This config defines a real spreadsheet which is a copy of the 2024 spreadsheet,
    # but with fake data for use in these tests.
    config = season_config.load_season_config("2024_test")

    event_configs = {
        event_.event_name: sheet.SeasonSheetEventConfig(
            sheet_name=event_.sheet_name,
            scorecard_start_cell=event_.scorecard_sheet_start_cell,
            event_num=event_idx + 1,
        )
        for event_idx, event_ in enumerate(config.events.values())
    }
    sheet_config = sheet.SeasonSheetConfig(
        sheet_id=config.sheet_id,
        leaderboard_sheet_name=config.leaderboard_sheet_name,
        players_sheet_name=config.players_sheet_name,
        events=event_configs,
        is_finale_enabled=False,
        finale_handicaps_sheet_name="",
    )

    sheet_ = sheet.SeasonSheet(config=sheet_config)

    expected_events = ["Poppy Ridge", "Presidio", "Harding Park"]
    expected_players_read_data = players.PlayersReadData(
        player_handicaps={
            "Stanton Turner": players.HandicapIndexByEvent(
                data={"Presidio": 14, "Poppy Ridge": 14, "Harding Park": 13.5},
                events=expected_events,
            ),
            "John Fratello": players.HandicapIndexByEvent(
                data={"Presidio": 16, "Poppy Ridge": 16, "Harding Park": 16},
                events=expected_events,
            ),
            "Steve Harasym": players.HandicapIndexByEvent(
                data={"Presidio": 8, "Poppy Ridge": 8, "Harding Park": 8.5},
                events=expected_events,
            ),
        }
    )
    expected_events_read_data: sheet.SeasonEventsReadData = {
        "Poppy Ridge": event.EventReadData(
            player_scores={
                "Stanton Turner": event.HoleScores(
                    scores={
                        1: 5,
                        2: 4,
                        3: 5,
                        4: 6,
                        5: 5,
                        6: 6,
                        7: 4,
                        8: 4,
                        9: 5,
                        10: 6,
                        11: 6,
                        12: 5,
                        13: 8,
                        14: 4,
                        15: 8,
                        16: 4,
                        17: 4,
                        18: 5,
                    },  # noqa: E501
                ),
                "John Fratello": event.HoleScores(
                    scores={
                        1: 5,
                        2: 7,
                        3: 6,
                        4: 3,
                        5: 5,
                        6: 6,
                        7: 3,
                        8: 5,
                        9: 6,
                        10: 7,
                        11: 6,
                        12: 4,
                        13: 3,
                        14: 5,
                        15: 3,
                        16: 4,
                        17: 5,
                        18: 6,
                    },  # noqa: E501
                ),
                "Steve Harasym": event.HoleScores(
                    scores={
                        1: 4,
                        2: 6,
                        3: 4,
                        4: 5,
                        5: 5,
                        6: 5,
                        7: 4,
                        8: 5,
                        9: 5,
                        10: 5,
                        11: 8,
                        12: 5,
                        13: 4,
                        14: 4,
                        15: 5,
                        16: 8,
                        17: 5,
                        18: 8,
                    },  # noqa: E501
                ),
            }
        ),
        "Presidio": event.EventReadData(
            player_scores={
                "Stanton Turner": event.HoleScores(
                    scores={
                        1: 5,
                        2: 4,
                        3: 5,
                        4: 6,
                        5: 5,
                        6: 6,
                        7: 4,
                        8: 4,
                        9: 5,
                        10: 6,
                        11: 6,
                        12: 5,
                        13: 4,
                        14: 4,
                        15: 4,
                        16: 4,
                        17: 4,
                        18: 5,
                    },  # noqa: E501
                ),
                "John Fratello": event.HoleScores(
                    scores={
                        1: 5,
                        2: 7,
                        3: 6,
                        4: 3,
                        5: 5,
                        6: 6,
                        7: 3,
                        8: 5,
                        9: 6,
                        10: 7,
                        11: 6,
                        12: 4,
                        13: 3,
                        14: 5,
                        15: 3,
                        16: 4,
                        17: 5,
                        18: 6,
                    },  # noqa: E501
                ),
                "Steve Harasym": event.IncompleteScore(),
            }
        ),
        "Harding Park": event.EventReadData(
            player_scores={
                "Stanton Turner": event.HoleScores(
                    scores={
                        1: 5,
                        2: 4,
                        3: 5,
                        4: 6,
                        5: 5,
                        6: 6,
                        7: 4,
                        8: 4,
                        9: 5,
                        10: 6,
                        11: 6,
                        12: 5,
                        13: 4,
                        14: 4,
                        15: 4,
                        16: 4,
                        17: 4,
                        18: 5,
                    },  # noqa: E501
                ),
                "John Fratello": event.HoleScores(
                    scores={
                        1: 5,
                        2: 4,
                        3: 5,
                        4: 6,
                        5: 5,
                        6: 6,
                        7: 4,
                        8: 4,
                        9: 5,
                        10: 6,
                        11: 6,
                        12: 5,
                        13: 4,
                        14: 4,
                        15: 4,
                        16: 4,
                        17: 4,
                        18: 5,
                    },  # noqa: E501
                ),
                "Steve Harasym": event.IncompleteScore(),
            }
        ),
    }

    sheet_read_data = sheet_.read()
    assert sheet_read_data.players == expected_players_read_data
    assert sheet_read_data.events == expected_events_read_data
