import pytest
from season_common import rank
from season_model.api.result.event_result import (
    DisallowedApiCallError,
    SeasonModelCompleteEventPlayerIndividualResult,
    SeasonModelEventPlayerAggregateResult,
    SeasonModelEventPlayerResult,
    SeasonModelIncompleteEventPlayerInividualResult,
)
from season_model.api.result.notable_holes import NotableHoles, NotableHoleType


def test_incomplete_player_event_result_singleton_implementation() -> None:
    result_1 = SeasonModelIncompleteEventPlayerInividualResult()
    result_2 = SeasonModelIncompleteEventPlayerInividualResult()

    assert result_1 is result_2


def test_player_event_result_is_complete_result_false() -> None:
    result_ = SeasonModelEventPlayerResult(
        name="FooBar",
        individual_result=SeasonModelIncompleteEventPlayerInividualResult(),
        aggregate_result=SeasonModelEventPlayerAggregateResult(
            gross_score_points=100.0,
            net_score_points=100.0,
            event_points=200.0,
            gross_score_rank=rank.RankValue(3),
            net_score_rank=rank.RankValue(5),
            event_rank=rank.RankValue(4),
        ),
    )

    assert not result_.is_complete_result


def test_player_event_result_is_complete_result_true() -> None:
    result_ = SeasonModelEventPlayerResult(
        name="FooBar",
        individual_result=SeasonModelCompleteEventPlayerIndividualResult(
            course_handicap=16,
            front_9_gross=39,
            back_9_gross=49,
            total_gross=88,
            total_net=72,
            notable_holes=NotableHoles(),
            score_differential=16,
        ),
        aggregate_result=SeasonModelEventPlayerAggregateResult(
            gross_score_points=100.0,
            net_score_points=100.0,
            event_points=200.0,
            gross_score_rank=rank.RankValue(3),
            net_score_rank=rank.RankValue(5),
            event_rank=rank.RankValue(4),
        ),
    )

    assert result_.is_complete_result


def test_player_event_result_complete_result_property_getters() -> None:
    notable_holes = NotableHoles()
    notable_holes.set_hole(hole_num=1, hole_type=NotableHoleType.BIRDIE)

    result_ = SeasonModelEventPlayerResult(
        name="FooBar",
        individual_result=SeasonModelCompleteEventPlayerIndividualResult(
            course_handicap=16,
            front_9_gross=39,
            back_9_gross=49,
            total_gross=88,
            total_net=72,
            notable_holes=notable_holes,
            score_differential=16,
        ),
        aggregate_result=SeasonModelEventPlayerAggregateResult(
            gross_score_points=100.0,
            net_score_points=100.0,
            event_points=200.0,
            gross_score_rank=rank.RankValue(3),
            net_score_rank=rank.RankValue(5),
            event_rank=rank.RankValue(4),
        ),
    )

    assert result_.course_handicap == 16
    assert result_.front_9_gross == 39
    assert result_.back_9_gross == 49
    assert result_.total_gross == 88
    assert result_.total_net == 72
    assert result_.notable_holes == notable_holes
    assert result_.gross_score_points == 100.0
    assert result_.net_score_points == 100.0
    assert result_.event_points == 200.0
    assert result_.gross_score_rank == rank.RankValue(3)
    assert result_.net_score_rank == rank.RankValue(5)
    assert result_.event_rank == rank.RankValue(4)


def test_incomplete_individual_player_event_result_api_calls_raises_error() -> None:
    result_ = SeasonModelIncompleteEventPlayerInividualResult()

    with pytest.raises(DisallowedApiCallError):
        result_.course_handicap

    with pytest.raises(DisallowedApiCallError):
        result_.front_9_gross

    with pytest.raises(DisallowedApiCallError):
        result_.back_9_gross

    with pytest.raises(DisallowedApiCallError):
        result_.total_gross

    with pytest.raises(DisallowedApiCallError):
        result_.total_net

    with pytest.raises(DisallowedApiCallError):
        result_.notable_holes


def test_individual_player_event_result_property_getters() -> None:
    notable_holes = NotableHoles()
    notable_holes.set_hole(hole_num=1, hole_type=NotableHoleType.BIRDIE)

    result_ = SeasonModelCompleteEventPlayerIndividualResult(
        course_handicap=16,
        front_9_gross=39,
        back_9_gross=49,
        total_gross=88,
        total_net=72,
        notable_holes=notable_holes,
        score_differential=16,
    )

    assert result_.course_handicap == 16
    assert result_.front_9_gross == 39
    assert result_.back_9_gross == 49
    assert result_.total_gross == 88
    assert result_.total_net == 72
    assert result_.notable_holes == notable_holes


def test_cumulative_player_event_result_construct() -> None:
    SeasonModelEventPlayerAggregateResult(
        gross_score_points=100.0,
        net_score_points=100.0,
        event_points=200.0,
        gross_score_rank=rank.RankValue(3),
        net_score_rank=rank.RankValue(5),
        event_rank=rank.RankValue(4),
    )
