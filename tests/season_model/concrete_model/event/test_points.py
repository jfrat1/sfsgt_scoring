import pytest

from season_model.api.input import SeasonModelEventType
from season_model.concrete_model.event import points

TEST_PLAYER_RANKS_NO_TIES = {
    "Player_1": 6,
    "Player_2": 8,
    "Player_3": 7,
    "Player_4": 3,
    "Player_5": 10,
    "Player_6": 2,
    "Player_7": 5,
    "Player_8": 1,
    "Player_9": 4,
    "Player_10": 9,
}

TEST_PLAYERS_AT_EACH_RANK_NO_TIES: dict[int, list[str]] = {
    1: ["Player_8"],
    2: ["Player_6"],
    3: ["Player_4"],
    4: ["Player_9"],
    5: ["Player_7"],
    6: ["Player_1"],
    7: ["Player_3"],
    8: ["Player_2"],
    9: ["Player_10"],
    10: ["Player_5"],
}

TEST_PLAYER_POINTS_NO_TIES_STANDARD_EVENT = {
    "Player_1": 20.0,
    "Player_2": 19.0,
    "Player_3": 19.5,
    "Player_4": 37.5,
    "Player_5": 18.0,
    "Player_6": 45.0,
    "Player_7": 25.0,
    "Player_8": 50.0,
    "Player_9": 30.0,
    "Player_10": 18.5,
}

TEST_PLAYER_RANKS_WITH_TIES = {
    "Player_1": 6,
    "Player_2": 7,
    "Player_3": 7,
    "Player_4": 2,
    "Player_5": 10,
    "Player_6": 2,
    "Player_7": 5,
    "Player_8": 1,
    "Player_9": 4,
    "Player_10": 9,
}

TEST_PLAYERS_AT_EACH_RANK_WITH_TIES: dict[int, list[str]] = {
    1: ["Player_8"],
    2: ["Player_4", "Player_6"],
    3: [],
    4: ["Player_9"],
    5: ["Player_7"],
    6: ["Player_1"],
    7: ["Player_2", "Player_3"],
    8: [],
    9: ["Player_10"],
    10: ["Player_5"],
}

TEST_PLAYER_POINTS_WITH_TIES_STANDARD_EVENT = {
    "Player_1": 20.0,
    "Player_2": 19.25,
    "Player_3": 19.25,
    "Player_4": 41.25,
    "Player_5": 18.0,
    "Player_6": 41.25,
    "Player_7": 25.0,
    "Player_8": 50.0,
    "Player_9": 30.0,
    "Player_10": 18.5,
}


def test_points_construct_standard_event() -> None:
    points_ = points.Points(SeasonModelEventType.STANDARD)
    assert points_._points_by_rank == points.STANDARD_EVENT_POINTS_BY_RANK


def test_points_construct_major_event() -> None:
    points_ = points.Points(SeasonModelEventType.MAJOR)
    assert points_._points_by_rank == points.MAJOR_EVENT_POINTS_BY_RANK


def test_player_points_from_ranks_no_ties_standard_event() -> None:
    points_ = points.Points(SeasonModelEventType.STANDARD)
    assert points_.player_points_from_ranks(TEST_PLAYER_RANKS_NO_TIES) == TEST_PLAYER_POINTS_NO_TIES_STANDARD_EVENT


def test_player_points_from_ranks_with_ties_standard_event() -> None:
    points_ = points.Points(SeasonModelEventType.STANDARD)
    assert points_.player_points_from_ranks(TEST_PLAYER_RANKS_WITH_TIES) == TEST_PLAYER_POINTS_WITH_TIES_STANDARD_EVENT


def test_player_points_from_ranks_empty_ranks_returns_empty_dict() -> None:
    points_ = points.Points(SeasonModelEventType.STANDARD)

    empty_dict: dict[str, int] = {}
    assert points_.player_points_from_ranks(player_ranks=empty_dict) == empty_dict


def test_are_player_ranks_empty_true() -> None:
    points_ = points.Points(SeasonModelEventType.STANDARD)

    empty_dict: dict[str, int] = {}
    assert points_._are_player_ranks_empty(empty_dict)


def test_are_player_rans_empty_false() -> None:
    points_ = points.Points(SeasonModelEventType.STANDARD)

    not_empty_dict: dict[str, int] = {"foo": 1}
    assert not points_._are_player_ranks_empty(not_empty_dict)


def test_verify_player_ranks_ok() -> None:
    points_ = points.Points(SeasonModelEventType.STANDARD)
    points_._verify_player_ranks(TEST_PLAYER_RANKS_NO_TIES)


def test_verify_player_ranks_raises_error_if_rank_not_in_allowed_range() -> None:
    points_ = points.Points(SeasonModelEventType.STANDARD)

    player_ranks = TEST_PLAYER_RANKS_NO_TIES.copy()

    player_ranks["Player_1"] = 51
    with pytest.raises(points.InvalidPlayerRanksError):
        points_._verify_player_ranks(player_ranks)

    player_ranks["Player_1"] = 0
    with pytest.raises(points.InvalidPlayerRanksError):
        points_._verify_player_ranks(player_ranks)


def test_players_at_each_rank_no_ties() -> None:
    points_ = points.Points(SeasonModelEventType.STANDARD)

    assert points_._players_at_each_rank(TEST_PLAYER_RANKS_NO_TIES) == TEST_PLAYERS_AT_EACH_RANK_NO_TIES


def test_players_at_each_rank_with_ties() -> None:
    points_ = points.Points(SeasonModelEventType.STANDARD)

    assert points_._players_at_each_rank(TEST_PLAYER_RANKS_WITH_TIES) == TEST_PLAYERS_AT_EACH_RANK_WITH_TIES


def test_player_points_no_ties_standard_event() -> None:
    points_ = points.Points(SeasonModelEventType.STANDARD)

    assert points_._player_points(TEST_PLAYERS_AT_EACH_RANK_NO_TIES) == TEST_PLAYER_POINTS_NO_TIES_STANDARD_EVENT


def test_player_points_with_ties_standard_event() -> None:
    points_ = points.Points(SeasonModelEventType.STANDARD)

    assert points_._player_points(TEST_PLAYERS_AT_EACH_RANK_WITH_TIES) == TEST_PLAYER_POINTS_WITH_TIES_STANDARD_EVENT


def test_points_for_players_at_rank_one_player_standard_event() -> None:
    points_ = points.Points(SeasonModelEventType.STANDARD)

    assert points_._points_for_players_at_rank(rank=1, num_players=1) == 50.0


def test_points_for_players_at_rank_two_players_standard_event() -> None:
    points_ = points.Points(SeasonModelEventType.STANDARD)

    # Points for rank 3 and 4 split evenly
    assert points_._points_for_players_at_rank(rank=3, num_players=2) == 33.75


def test_points_for_players_at_rank_three_players_standard_event() -> None:
    points_ = points.Points(SeasonModelEventType.STANDARD)

    # Points for rank 6, 7, and 8 split evenly
    assert points_._points_for_players_at_rank(rank=6, num_players=3) == 19.5
