import pytest
from season_common import rank

TEST_PLAYER_VALUES_NO_TIES = {
    "Player_1": 10,
    "Player_2": 40,
    "Player_3": 30,
    "Player_4": 20,
    "Player_5": 5,
}

TEST_PLAYER_RANKS_ASCENDING_NO_TIES = {
    "Player_1": rank.RankValue(2),
    "Player_2": rank.RankValue(5),
    "Player_3": rank.RankValue(4),
    "Player_4": rank.RankValue(3),
    "Player_5": rank.RankValue(1),
}

TEST_PLAYER_RANKS_DESCENDING_NO_TIES = {
    "Player_1": rank.RankValue(4),
    "Player_2": rank.RankValue(1),
    "Player_3": rank.RankValue(2),
    "Player_4": rank.RankValue(3),
    "Player_5": rank.RankValue(5),
}

TEST_PLAYER_VALUES_WITH_TIES = {
    "Player_1": 10,
    "Player_2": 40,
    "Player_3": 20,
    "Player_4": 20,
    "Player_5": 5,
}

TEST_PLAYER_RANKS_ASCENDING_WITH_TIES = {
    "Player_1": rank.RankValue(2),
    "Player_2": rank.RankValue(5),
    "Player_3": rank.RankValue(3),
    "Player_4": rank.RankValue(3),
    "Player_5": rank.RankValue(1),
}

TEST_PLAYER_RANKS_DESCENDING_WITH_TIES = {
    "Player_1": rank.RankValue(4),
    "Player_2": rank.RankValue(1),
    "Player_3": rank.RankValue(2),
    "Player_4": rank.RankValue(2),
    "Player_5": rank.RankValue(5),
}


def test_rank_tie_method_as_pandas_rank_method() -> None:
    assert rank.RankTieMethod.MIN.as_pandas_rank_method() == "min"
    assert rank.RankTieMethod.MAX.as_pandas_rank_method() == "max"


def test_rank_order_is_ascending() -> None:
    assert rank.RankOrder.ASCENDING.is_ascending()
    assert not rank.RankOrder.DESCENDING.is_ascending()


def test_rank_ascending_no_ties() -> None:
    rank_mgr = rank.RankManager()
    assert (
        rank_mgr.player_ranks_from_values(
            player_values=TEST_PLAYER_VALUES_NO_TIES,
            rank_order=rank.RankOrder.ASCENDING,
        )
        == TEST_PLAYER_RANKS_ASCENDING_NO_TIES
    )


def test_rank_descending_no_ties() -> None:
    rank_mgr = rank.RankManager()
    assert (
        rank_mgr.player_ranks_from_values(
            player_values=TEST_PLAYER_VALUES_NO_TIES,
            rank_order=rank.RankOrder.DESCENDING,
        )
        == TEST_PLAYER_RANKS_DESCENDING_NO_TIES
    )


def test_rank_ascending_with_ties() -> None:
    rank_mgr = rank.RankManager()
    assert (
        rank_mgr.player_ranks_from_values(
            player_values=TEST_PLAYER_VALUES_WITH_TIES,
            rank_order=rank.RankOrder.ASCENDING,
        )
        == TEST_PLAYER_RANKS_ASCENDING_WITH_TIES
    )


def test_rank_descending_with_ties() -> None:
    rank_mgr = rank.RankManager()
    assert (
        rank_mgr.player_ranks_from_values(
            player_values=TEST_PLAYER_VALUES_WITH_TIES,
            rank_order=rank.RankOrder.DESCENDING,
        )
        == TEST_PLAYER_RANKS_DESCENDING_WITH_TIES
    )


def test_player_ranks_from_values_empty_values_returns_empty() -> None:
    rank_mgr = rank.RankManager()

    empty_dict: dict[str, int] = {}

    assert (
        rank_mgr.player_ranks_from_values(
            player_values=empty_dict,
            rank_order=rank.RankOrder.DESCENDING,
        )
        == empty_dict
    )


def test_rank_value_construct_non_int_raises_error() -> None:
    with pytest.raises(rank.RankValueNotIntegerError):
        rank.RankValue("4")  # type: ignore


def test_rank_value_as_str() -> None:
    rank_ = rank.RankValue(4)
    assert rank_.as_str() == "4"


def test_rank_value_add_integer() -> None:
    assert rank.RankValue(4) + 6 == rank.RankValue(10)


def test_rank_value_add_rank_value() -> None:
    assert rank.RankValue(4) + rank.RankValue(6) == rank.RankValue(10)


def test_no_rank_construct() -> None:
    rank.NoRankValue()


def test_no_rank_as_str_call_raises_error() -> None:
    rank_ = rank.NoRankValue()

    with pytest.raises(rank.NoRankValueApiCallError):
        rank_.as_str()


def test_no_rank_singleton_implementation() -> None:
    no_rank_1 = rank.NoRankValue()
    no_rank_2 = rank.NoRankValue()

    assert no_rank_1 is no_rank_2


def test_ranks_list_max() -> None:
    ranks = [rank.RankValue(3), rank.RankValue(1), rank.RankValue(2)]

    assert max(ranks) == rank.RankValue(3)


def test_ranks_list_min() -> None:
    ranks = [rank.RankValue(3), rank.RankValue(1), rank.RankValue(2)]

    assert min(ranks) == rank.RankValue(1)


def test_rank_value_is_win() -> None:
    assert rank.RankValue(1).is_win()
    assert not rank.RankValue(2).is_win()
    assert not rank.RankValue(3).is_win()


def test_rank_value_is_top_five() -> None:
    assert rank.RankValue(1).is_top_five()
    assert rank.RankValue(2).is_top_five()
    assert rank.RankValue(3).is_top_five()
    assert rank.RankValue(4).is_top_five()
    assert rank.RankValue(5).is_top_five()
    assert not rank.RankValue(6).is_top_five()
    assert not rank.RankValue(7).is_top_five()


def test_rank_value_is_top_ten() -> None:
    assert rank.RankValue(1).is_top_ten()
    assert rank.RankValue(2).is_top_ten()
    assert rank.RankValue(3).is_top_ten()
    assert rank.RankValue(4).is_top_ten()
    assert rank.RankValue(5).is_top_ten()
    assert rank.RankValue(6).is_top_ten()
    assert rank.RankValue(7).is_top_ten()
    assert rank.RankValue(8).is_top_ten()
    assert rank.RankValue(9).is_top_ten()
    assert rank.RankValue(10).is_top_ten()
    assert not rank.RankValue(11).is_top_ten()
    assert not rank.RankValue(12).is_top_ten()


def assert_no_rank_value_is_not_win() -> None:
    assert not rank.NoRankValue().is_win()


def assert_no_rank_value_is_not_top_five() -> None:
    assert not rank.NoRankValue().is_top_five()


def assert_no_rank_value_is_not_top_ten() -> None:
    assert not rank.NoRankValue().is_top_ten()
