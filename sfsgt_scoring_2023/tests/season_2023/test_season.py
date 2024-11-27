from typing import List
from unittest import mock

from sfsgt_scoring_2023 import course, player, season, season_sheet


def make_mock_player_group(player_names: List[str] | None = None) -> mock.MagicMock:
    mock_obj = mock.MagicMock(spec=player.PlayerGroup)
    if player_names:
        mock_obj.player_names.return_value = player_names

    return mock_obj


def make_mock_season_player_group(player_names: List[str] | None = None) -> mock.MagicMock:
    mock_obj = mock.MagicMock(spec=season.SeasonPlayerGroup)
    if player_names:
        mock_obj.player_names.return_value = player_names

    return mock_obj


def make_mock_course_group(course_names: List[str] | None = None) -> course.CourseGroup:
    mock_obj = mock.MagicMock(spec=course.CourseGroup)
    if course_names:
        mock_obj.course_names.return_value = course_names

    return mock_obj


def make_mock_season_sheet(
    mock_player_group: mock.MagicMock,
    mock_season_player_group: mock.MagicMock,
    mock_course_group: mock.MagicMock,
) -> mock.MagicMock:
    mock_obj = mock.MagicMock(spec=season_sheet.SeasonSheet)
    mock_obj.read_players_sheet.return_value = mock_player_group
    mock_obj.read_courses_sheet.return_value = mock_course_group
    mock_obj.read_player_handicaps_sheet.return_value = mock_season_player_group
    return mock_obj


def test_constructor() -> None:
    player_names = ["Bolt", "Geoff"]
    mock_player_group = make_mock_player_group(player_names=player_names)
    mock_course_group = make_mock_course_group(course_names=["Presidio"])
    mock_season_player_group = make_mock_season_player_group(
        player_names=player_names,
    )
    mock_season_sheet = make_mock_season_sheet(
        mock_player_group=mock_player_group,
        mock_course_group=mock_course_group,
        mock_season_player_group=mock_season_player_group,
    )

    event_configs = [
        season.SeasonEventConfig(
            course_name="Presidio",
            scorecard_sheet_name="Presidio Scorecard",
            results_sheet_name="Presidio Results",
            points_by_rank={1: 50.0, 2: 25.0},
        )
    ]
    season_ = season.Season(
        season_sheet=mock_season_sheet,
        event_configs=event_configs,
    )

    assert season_.courses is mock_course_group
    assert season_.players is mock_season_player_group

    assert len(season_.event_configs) == 1
    assert season_.event_configs == event_configs

    assert season_.course_handicaps_list == []
    assert set(season_.season_points.index) == set(player_names)
    assert set(season_.season_points.columns) == {"Presidio"}
    assert all(season_.season_points.values == 0)
