import pytest

from .. import rank


def test_event_rank_construct_non_int_raises_error() -> None:
    with pytest.raises(rank.EventRankNotIntegerError):
        rank.EventRank("4")  # type: ignore


def test_event_rank_as_str() -> None:
    rank_ = rank.EventRank(4)
    assert rank_.as_str() == "4"


def test_no_rank_construct() -> None:
    rank.NoRank()


def test_no_rank_as_str_call_raises_error() -> None:
    rank_ = rank.NoRank()

    with pytest.raises(rank.NoRankAccessError):
        rank_.as_str()


def test_no_rank_singleton_implementation() -> None:
    no_rank_1 = rank.NoRank()
    no_rank_2 = rank.NoRank()

    assert no_rank_1 is no_rank_2
