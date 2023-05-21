from unittest import mock

import pandas as pd
import pytest

from sfsgt_scoring import (
    course,
    event,
    player,
    season,
    season_sheet,
)


def test_constructor() -> None:
    mock_sheet_controller = mock.MagicMock(spec=season_sheet.sheets.SheetController)

    season_ = season_sheet.SeasonSheet(sheet_controller=mock_sheet_controller)

    assert season_.sheet_controller is mock_sheet_controller

def test_read_players_sheet() -> None:
    mock_sheet_controller = mock.MagicMock(spec=season_sheet.sheets.SheetController)
    mock_sheet_controller.worksheet_to_df.return_value = pd.DataFrame(
        data=[["Geoff", 12.5], ["Bolt", 4]],
        columns=["Player", "Handicap"],
    )

    season_ = season_sheet.SeasonSheet(sheet_controller=mock_sheet_controller)

    season_players = season_.read_players_sheet()
    assert isinstance(season_players, player.PlayerGroup)
    assert len(season_players.player_list) == 2
    assert season_players.player_list[0] == player.Player(name="Geoff", handicap=12.5)
    assert season_players.player_list[1] == player.Player(name="Bolt", handicap=4)


def test_read_players_sheet_wrong_headers() -> None:
    mock_sheet_controller = mock.MagicMock(spec=season_sheet.sheets.SheetController)
    mock_sheet_controller.worksheet_to_df.return_value = pd.DataFrame(
        data=[["Geoff", 12.5], ["Bolt", 4]],
        columns=["Incorrect Column Header", "Handicap"],
    )

    season_ = season_sheet.SeasonSheet(sheet_controller=mock_sheet_controller)

    with pytest.raises(
        season_sheet.SeasonSheetException, match="Malformed 'Players' sheet. Expected columns"
    ):
        season_.read_players_sheet()


def test_read_players_sheet_player_column_values_not_strings() -> None:
    mock_sheet_controller = mock.MagicMock(spec=season_sheet.sheets.SheetController)
    mock_sheet_controller.worksheet_to_df.return_value = pd.DataFrame(
        data=[["Geoff", 12.5], [10, 4]],
        columns=["Player", "Handicap"],
    )

    season_ = season_sheet.SeasonSheet(sheet_controller=mock_sheet_controller)

    with pytest.raises(
        season_sheet.SeasonSheetException,
        match="Malformed 'Players' sheet. Values in the 'Player' column"
    ):
        season_.read_players_sheet()


def test_read_players_sheet_handicap_column_values_not_numeric() -> None:
    mock_sheet_controller = mock.MagicMock(spec=season_sheet.sheets.SheetController)
    mock_sheet_controller.worksheet_to_df.return_value = pd.DataFrame(
        data=[["Geoff", 12], ["Bolt", "4"]],
        columns=["Player", "Handicap"],
    )

    season_ = season_sheet.SeasonSheet(sheet_controller=mock_sheet_controller)

    with pytest.raises(
        season_sheet.SeasonSheetException,
        match="Malformed 'Players' sheet. Values in the 'Handicap' column"
    ):
        season_.read_players_sheet()

def test_read_player_handicaps_sheet() -> None:
    mock_sheet_controller = mock.MagicMock(spec=season_sheet.sheets.SheetController)
    mock_sheet_controller.worksheet_to_df.return_value = pd.DataFrame(
        data=[["Geoff", 12, 12.5], ["Bolt", 6, 5]],
        columns=["Player", "Presidio", "Harding Park"],
    )

    season_ = season_sheet.SeasonSheet(sheet_controller=mock_sheet_controller)

    season_players = season_.read_player_handicaps_sheet(
        expected_events=["Presidio", "Harding Park"]
    )

    assert isinstance(season_players, season.SeasonPlayerGroup)
    assert len(season_players.player_list) == 2
    assert season_players.player_list[0] == season.SeasonPlayer(
        name="Geoff",
        handicap_by_event={"Presidio": 12, "Harding Park": 12.5}
    )
    assert season_players.player_list[1] == season.SeasonPlayer(
        name="Bolt",
        handicap_by_event={"Presidio": 6, "Harding Park": 5}
    )


def test_read_player_handicaps_sheet_not_enough_columns() -> None:
    mock_sheet_controller = mock.MagicMock(spec=season_sheet.sheets.SheetController)
    mock_sheet_controller.worksheet_to_df.return_value = pd.DataFrame(
        data=[["Geoff"], ["Bolt"]],
        columns=["Player"],
    )

    season_ = season_sheet.SeasonSheet(sheet_controller=mock_sheet_controller)

    with pytest.raises(
        season_sheet.SeasonSheetException,
        match="Malformed 'Player Handicaps' sheet. There must be 2 or more columns."
    ):
        season_.read_player_handicaps_sheet(
            expected_events=["Presidio", "Harding Park"]
        )


def test_read_player_handicaps_sheet_first_column_not_player() -> None:
    mock_sheet_controller = mock.MagicMock(spec=season_sheet.sheets.SheetController)
    mock_sheet_controller.worksheet_to_df.return_value = pd.DataFrame(
        data=[["Geoff", 12, 12.5], ["Bolt", 6, 5]],
        columns=["Not Player", "Presidio", "Harding Park"],
    )

    season_ = season_sheet.SeasonSheet(sheet_controller=mock_sheet_controller)

    with pytest.raises(
        season_sheet.SeasonSheetException,
        match="Malformed 'Player Handicaps' sheet. The first column header should be 'Player'"
    ):
        season_.read_player_handicaps_sheet(
            expected_events=["Presidio", "Harding Park"]
        )


def test_read_player_handicaps_sheet_event_columns_dont_match() -> None:
    mock_sheet_controller = mock.MagicMock(spec=season_sheet.sheets.SheetController)
    mock_sheet_controller.worksheet_to_df.return_value = pd.DataFrame(
        data=[["Geoff", 12, 12.5], ["Bolt", 6, 5]],
        columns=["Player", "Presidio", "Not Harding Park"],
    )

    season_ = season_sheet.SeasonSheet(sheet_controller=mock_sheet_controller)

    with pytest.raises(
        season_sheet.SeasonSheetException,
        match="Malformed 'Player Handicaps' sheet. Expected events"
    ):
        season_.read_player_handicaps_sheet(
            expected_events=["Presidio", "Harding Park"]
        )


def test_read_player_handicaps_sheet_player_values_not_string() -> None:
    mock_sheet_controller = mock.MagicMock(spec=season_sheet.sheets.SheetController)
    mock_sheet_controller.worksheet_to_df.return_value = pd.DataFrame(
        data=[["Geoff", 12, 12.5], [12, 6, 5]],
        columns=["Player", "Presidio", "Harding Park"],
    )

    season_ = season_sheet.SeasonSheet(sheet_controller=mock_sheet_controller)

    with pytest.raises(
        season_sheet.SeasonSheetException,
        match="Malformed 'Player Handicaps' sheet. Values in the 'Player' column"
    ):
        season_.read_player_handicaps_sheet(
            expected_events=["Presidio", "Harding Park"]
        )


def test_read_player_handicaps_sheet_handicap_values_not_numeric() -> None:
    mock_sheet_controller = mock.MagicMock(spec=season_sheet.sheets.SheetController)
    mock_sheet_controller.worksheet_to_df.return_value = pd.DataFrame(
        data=[["Geoff", 12, 12.5], ["Bolt", "6", 5]],
        columns=["Player", "Presidio", "Harding Park"],
    )

    season_ = season_sheet.SeasonSheet(sheet_controller=mock_sheet_controller)

    with pytest.raises(
        season_sheet.SeasonSheetException,
        match="Malformed 'Player Handicaps' sheet. Values in the 'Presidio' column"
    ):
        season_.read_player_handicaps_sheet(
            expected_events=["Presidio", "Harding Park"]
        )


def test_read_courses_sheet() -> None:
    mock_sheet_controller = mock.MagicMock(spec=season_sheet.sheets.SheetController)
    mock_sheet_controller.worksheet_to_df.return_value = pd.DataFrame(
        data=[
            ["Presidio", 72, 69.5, 129, "Blue", 5746],
            ["Peacock Gap", 71, 67.2, 117, "White", 5673],
        ],
        columns=["Course", "Par", "Rating", "Slope", "Tee", "Distance"],
    )

    season_ = season_sheet.SeasonSheet(sheet_controller=mock_sheet_controller)

    season_courses = season_.read_courses_sheet()
    assert isinstance(season_courses, course.CourseGroup)
    assert len(season_courses.course_list) == 2
    assert season_courses.course_list[0] == course.Course(
        course_name="Presidio", tee_name="Blue", par=72, rating=69.5, slope=129, distance=5746
    )
    assert season_courses.course_list[1] == course.Course(
        course_name="Peacock Gap", tee_name="White", par=71, rating=67.2, slope=117, distance=5673
    )


def test_read_courses_sheet_wrong_headers() -> None:
    mock_sheet_controller = mock.MagicMock(spec=season_sheet.sheets.SheetController)
    mock_sheet_controller.worksheet_to_df.return_value = pd.DataFrame(
        data=[
            ["Presidio", 72, 69.5, 129, "Blue", 5746],
            ["Peacock Gap", 71, 67.2, 117, "White", 5673],
        ],
        columns=["Not Course", "Par", "Rating", "Slope", "Tee", "Distance"],
    )

    season_ = season_sheet.SeasonSheet(sheet_controller=mock_sheet_controller)

    with pytest.raises(
        season_sheet.SeasonSheetException,
        match="Malformed 'Courses' sheet. Expected columns"
    ):
        season_.read_courses_sheet()


def test_read_courses_sheet_wrong_course_value_type() -> None:
    mock_sheet_controller = mock.MagicMock(spec=season_sheet.sheets.SheetController)
    mock_sheet_controller.worksheet_to_df.return_value = pd.DataFrame(
        data=[
            [12, 72, 69.5, 129, "Blue", 5746],
            ["Peacock Gap", 71, 67.2, 117, "White", 5673],
        ],
        columns=["Course", "Par", "Rating", "Slope", "Tee", "Distance"],
    )

    season_ = season_sheet.SeasonSheet(sheet_controller=mock_sheet_controller)

    with pytest.raises(
        season_sheet.SeasonSheetException,
        match="Malformed 'Courses' sheet. The 'Course' column values should all be <class 'str'>."
    ):
        season_.read_courses_sheet()


def test_read_courses_sheet_wrong_par_value_type() -> None:
    mock_sheet_controller = mock.MagicMock(spec=season_sheet.sheets.SheetController)
    mock_sheet_controller.worksheet_to_df.return_value = pd.DataFrame(
        data=[
            ["Presidio", "72", 69.5, 129, "Blue", 5746],
            ["Peacock Gap", 71, 67.2, 117, "White", 5673],
        ],
        columns=["Course", "Par", "Rating", "Slope", "Tee", "Distance"],
    )

    season_ = season_sheet.SeasonSheet(sheet_controller=mock_sheet_controller)

    with pytest.raises(
        season_sheet.SeasonSheetException,
        match="Malformed 'Courses' sheet. The 'Par' column values should all be <class 'int'>."
    ):
        season_.read_courses_sheet()


def test_read_courses_sheet_wrong_rating_value_type() -> None:
    mock_sheet_controller = mock.MagicMock(spec=season_sheet.sheets.SheetController)
    mock_sheet_controller.worksheet_to_df.return_value = pd.DataFrame(
        data=[
            ["Presidio", 72, "69.5", 129, "Blue", 5746],
            ["Peacock Gap", 71, 67.2, 117, "White", 5673],
        ],
        columns=["Course", "Par", "Rating", "Slope", "Tee", "Distance"],
    )

    season_ = season_sheet.SeasonSheet(sheet_controller=mock_sheet_controller)

    with pytest.raises(
        season_sheet.SeasonSheetException,
        match="Malformed 'Courses' sheet. The 'Rating' column values should all be <class 'float'>."
    ):
        season_.read_courses_sheet()


def test_read_courses_sheet_wrong_slope_value_type() -> None:
    mock_sheet_controller = mock.MagicMock(spec=season_sheet.sheets.SheetController)
    mock_sheet_controller.worksheet_to_df.return_value = pd.DataFrame(
        data=[
            ["Presidio", 72, 69.5, "129", "Blue", 5746],
            ["Peacock Gap", 71, 67.2, 117, "White", 5673],
        ],
        columns=["Course", "Par", "Rating", "Slope", "Tee", "Distance"],
    )

    season_ = season_sheet.SeasonSheet(sheet_controller=mock_sheet_controller)

    with pytest.raises(
        season_sheet.SeasonSheetException,
        match="Malformed 'Courses' sheet. The 'Slope' column values should all be <class 'int'>."
    ):
        season_.read_courses_sheet()


def test_read_courses_sheet_wrong_tee_value_type() -> None:
    mock_sheet_controller = mock.MagicMock(spec=season_sheet.sheets.SheetController)
    mock_sheet_controller.worksheet_to_df.return_value = pd.DataFrame(
        data=[
            ["Presidio", 72, 69.5, 129, 12, 5746],
            ["Peacock Gap", 71, 67.2, 117, "White", 5673],
        ],
        columns=["Course", "Par", "Rating", "Slope", "Tee", "Distance"],
    )

    season_ = season_sheet.SeasonSheet(sheet_controller=mock_sheet_controller)

    with pytest.raises(
        season_sheet.SeasonSheetException,
        match="Malformed 'Courses' sheet. The 'Tee' column values should all be <class 'str'>."
    ):
        season_.read_courses_sheet()


def test_read_courses_sheet_wrong_distance_value_type() -> None:
    mock_sheet_controller = mock.MagicMock(spec=season_sheet.sheets.SheetController)
    mock_sheet_controller.worksheet_to_df.return_value = pd.DataFrame(
        data=[
            ["Presidio", 72, 69.5, 129, "Blue", 5746.0],
            ["Peacock Gap", 71, 67.2, 117, "White", 5673],
        ],
        columns=["Course", "Par", "Rating", "Slope", "Tee", "Distance"],
    )

    season_ = season_sheet.SeasonSheet(sheet_controller=mock_sheet_controller)

    with pytest.raises(
        season_sheet.SeasonSheetException,
        match="Malformed 'Courses' sheet. The 'Distance' column values should all be <class 'int'>."
    ):
        season_.read_courses_sheet()


def test_read_event_scorecard() -> None:
    mock_sheet_controller = mock.MagicMock(spec=season_sheet.sheets.SheetController)
    mock_sheet_controller.worksheet_to_df.return_value = pd.DataFrame(
        data=[
            ["Par"] + [4] * 9 + [36, ""] + [4] * 9 + [36, 72],
            ["Max"] + [10] * 9 + [90, ""] + [10] * 9 + [90, 180],
            ["Geoff"] + [4] * 9 + [45, ""] + [4] * 9 + [45, 90],
            ["Bolt"] + [5] * 9 + [36, ""] + [5] * 9 + [36, 72],
        ],
        columns=(
            ["Player"] +
            [str(x) for x in range(1, 10)] + ["Out", ""] +
            [str(x) for x in range(10, 19)] + ["In", "Total"]
        )
    )

    season_ = season_sheet.SeasonSheet(sheet_controller=mock_sheet_controller)

    scorecard = season_.read_event_scorecard_sheet(
        worksheet_name="Presidio Scorecard", expected_players=["Geoff", "Bolt"]
    )

    assert isinstance(scorecard, event.EventScorecard)
    assert list(scorecard.player_scorecards.keys()) == ["Geoff", "Bolt"]
    assert scorecard.player_scorecards["Geoff"].hole_scores == {hole: 4 for hole in range(1, 19)}
    assert scorecard.player_scorecards["Geoff"].gross_strokes() == 72
    assert scorecard.player_scorecards["Bolt"].hole_scores == {hole: 5 for hole in range(1, 19)}
    assert scorecard.player_scorecards["Bolt"].gross_strokes() == 90


def test_read_event_scorecard_missing_total_column() -> None:
    mock_sheet_controller = mock.MagicMock(spec=season_sheet.sheets.SheetController)
    mock_sheet_controller.worksheet_to_df.return_value = pd.DataFrame(
        data=[
            ["Par"] + [4] * 9 + [36, ""] + [4] * 9 + [36],
            ["Max"] + [10] * 9 + [90, ""] + [10] * 9 + [90],
            ["Geoff"] + [5] * 9 + [45, ""] + [5] * 9 + [45],
            ["Bolt"] + [4] * 9 + [36, ""] + [4] * 9 + [36],
        ],
        columns=(
            ["Player"] +
            [str(x) for x in range(1, 10)] + ["Out", ""] +
            [str(x) for x in range(10, 19)] + ["In"]
        )
    )

    season_ = season_sheet.SeasonSheet(sheet_controller=mock_sheet_controller)

    with pytest.raises(
        season_sheet.SeasonSheetException,
        match="Malformed 'Presidio Scorecard' sheet. Column headers do not match expectations."
    ):
        season_.read_event_scorecard_sheet(
            worksheet_name="Presidio Scorecard", expected_players=["Geoff", "Bolt"]
        )


def test_read_event_scorecard_missing_par_row() -> None:
    mock_sheet_controller = mock.MagicMock(spec=season_sheet.sheets.SheetController)
    mock_sheet_controller.worksheet_to_df.return_value = pd.DataFrame(
        data=[
            ["Max"] + [10] * 9 + [90, ""] + [10] * 9 + [90, 180],
            ["Geoff"] + [5] * 9 + [45, ""] + [5] * 9 + [45, 90],
            ["Bolt"] + [4] * 9 + [36, ""] + [4] * 9 + [36, 72],
        ],
        columns=(
            ["Player"] +
            [str(x) for x in range(1, 10)] + ["Out", ""] +
            [str(x) for x in range(10, 19)] + ["In", "Total"]
        )
    )

    season_ = season_sheet.SeasonSheet(sheet_controller=mock_sheet_controller)

    with pytest.raises(
        season_sheet.SeasonSheetException,
        match=(
            "Malformed 'Presidio Scorecard' sheet. The sheet must have a 'Par' and 'Max' "
            "row header."
        )
    ):
        season_.read_event_scorecard_sheet(
            worksheet_name="Presidio Scorecard", expected_players=["Geoff", "Bolt"]
        )


def test_read_event_scorecard_missing_players() -> None:
    mock_sheet_controller = mock.MagicMock(spec=season_sheet.sheets.SheetController)
    mock_sheet_controller.worksheet_to_df.return_value = pd.DataFrame(
        data=[
            ["Par"] + [4] * 9 + [36, ""] + [4] * 9 + [36, 72],
            ["Max"] + [10] * 9 + [90, ""] + [10] * 9 + [90, 180],
            ["Geoff"] + [5] * 9 + [45, ""] + [5] * 9 + [45, 90],
            ["Bolt"] + [4] * 9 + [36, ""] + [4] * 9 + [36, 72],
        ],
        columns=(
            ["Player"] +
            [str(x) for x in range(1, 10)] + ["Out", ""] +
            [str(x) for x in range(10, 19)] + ["In", "Total"]
        )
    )

    season_ = season_sheet.SeasonSheet(sheet_controller=mock_sheet_controller)

    with pytest.raises(
        season_sheet.SeasonSheetException,
        match=(
            "Malformed 'Presidio Scorecard' sheet. Player names do not match the expected "
            "players list."
        )
    ):
        season_.read_event_scorecard_sheet(
            worksheet_name="Presidio Scorecard", expected_players=["Geoff", "Bolt", "Someone Else"]
        )
