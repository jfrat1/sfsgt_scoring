from season_common.rank import NoRankValue, Rank, RankValue
from season_model.api.input import SeasonModelEventType
from season_model.api.result import (
    NotableHoles,
    NotableHoleType,
    SeasonModelCompleteEventPlayerIndividualResult,
    SeasonModelIncompleteEventPlayerInividualResult,
    SeasonModelEventPlayerAggregateResult,
    SeasonModelEventPlayerIndividualResult,
)
from season_model.concrete_model.event.aggregate import EventAggregateResultsGenerator

STANTON_NOTABLE_HOLES = NotableHoles()
STANTON_NOTABLE_HOLES.set_hole(14, NotableHoleType.BIRDIE)
STANTON_NOTABLE_HOLES.set_hole(17, NotableHoleType.BIRDIE)

JOHN_NOTABLE_HOLES = NotableHoles()
JOHN_NOTABLE_HOLES.set_hole(4, NotableHoleType.BIRDIE)
JOHN_NOTABLE_HOLES.set_hole(13, NotableHoleType.BIRDIE)
JOHN_NOTABLE_HOLES.set_hole(15, NotableHoleType.BIRDIE)

NO_NOTABLE_HOLES = NotableHoles()

PLAYERS_WITH_COMPLETE_SCORES = [
    "Stanton Turner",
    "John Fratello",
    "Cullan Jackson",
    "Jeff McCarthy",
]
PLAYERS_WITH_INCOMPLETE_SCORES = [
    "Steve Harasym",
]

STUB_PLAYER_INDIVIDUAL_RESULTS: dict[str, SeasonModelEventPlayerIndividualResult] = {
    "Stanton Turner": SeasonModelCompleteEventPlayerIndividualResult(
        course_handicap=14,
        front_9_gross=44,
        back_9_gross=46,
        total_gross=90,
        total_net=76,
        notable_holes=STANTON_NOTABLE_HOLES,
        score_differential=17.5,
    ),
    "John Fratello": SeasonModelCompleteEventPlayerIndividualResult(
        course_handicap=16,
        front_9_gross=46,
        back_9_gross=43,
        total_gross=89,
        total_net=73,
        notable_holes=JOHN_NOTABLE_HOLES,
        score_differential=16.6,
    ),
    "Cullan Jackson": SeasonModelCompleteEventPlayerIndividualResult(
        course_handicap=7,
        front_9_gross=41,
        back_9_gross=43,
        total_gross=84,
        total_net=77,
        notable_holes=NO_NOTABLE_HOLES,
        score_differential=12.2,
    ),
    "Jeff McCarthy": SeasonModelCompleteEventPlayerIndividualResult(
        course_handicap=22,
        front_9_gross=51,
        back_9_gross=49,
        total_gross=100,
        total_net=78,
        notable_holes=NO_NOTABLE_HOLES,
        score_differential=26.3,
    ),
    "Steve Harasym": SeasonModelIncompleteEventPlayerInividualResult(),
}

TEST_PLAYER_CUMULATIVE_RESULTS = {
    "Stanton Turner": SeasonModelEventPlayerAggregateResult(
        gross_score_points=37.5,
        net_score_points=45.0,
        event_points=82.5,
        gross_score_rank=RankValue(3),
        net_score_rank=RankValue(2),
        event_rank=RankValue(3),
    ),
    "John Fratello": SeasonModelEventPlayerAggregateResult(
        gross_score_points=45.0,
        net_score_points=50.0,
        event_points=95.0,
        gross_score_rank=RankValue(2),
        net_score_rank=RankValue(1),
        event_rank=RankValue(1),
    ),
    "Cullan Jackson": SeasonModelEventPlayerAggregateResult(
        gross_score_points=50.0,
        net_score_points=37.5,
        event_points=87.5,
        gross_score_rank=RankValue(1),
        net_score_rank=RankValue(3),
        event_rank=RankValue(2),
    ),
    "Jeff McCarthy": SeasonModelEventPlayerAggregateResult(
        gross_score_points=30.0,
        net_score_points=30.0,
        event_points=60.0,
        gross_score_rank=RankValue(4),
        net_score_rank=RankValue(4),
        event_rank=RankValue(4),
    ),
    "Steve Harasym": SeasonModelEventPlayerAggregateResult(
        gross_score_points=0.0,
        net_score_points=0.0,
        event_points=0.0,
        gross_score_rank=NoRankValue(),
        net_score_rank=NoRankValue(),
        event_rank=RankValue(5),
    ),
}


def test_event_player_cumulative_results() -> None:
    result = EventAggregateResultsGenerator(
        individual_results=STUB_PLAYER_INDIVIDUAL_RESULTS,
        event_type=SeasonModelEventType.STANDARD,
    ).generate()
    assert result == TEST_PLAYER_CUMULATIVE_RESULTS


def test_cumulative_results_construct() -> None:
    generator = EventAggregateResultsGenerator(
        individual_results=STUB_PLAYER_INDIVIDUAL_RESULTS,
        event_type=SeasonModelEventType.STANDARD,
    )

    expected_complete_individual_player_results = {
        player_name: result
        for player_name, result in STUB_PLAYER_INDIVIDUAL_RESULTS.items()
        if player_name in PLAYERS_WITH_COMPLETE_SCORES
    }
    expected_incomplete_individual_player_results = {
        player_name: result
        for player_name, result in STUB_PLAYER_INDIVIDUAL_RESULTS.items()
        if player_name in PLAYERS_WITH_INCOMPLETE_SCORES
    }

    assert generator._complete_results == expected_complete_individual_player_results
    assert generator._incomplete_results == expected_incomplete_individual_player_results


def test_aggregate_results_from_complete_individual_results() -> None:
    generator = EventAggregateResultsGenerator(
        individual_results=STUB_PLAYER_INDIVIDUAL_RESULTS,
        event_type=SeasonModelEventType.STANDARD,
    )

    expected_result = {
        name: result for name, result in TEST_PLAYER_CUMULATIVE_RESULTS.items() if name in PLAYERS_WITH_COMPLETE_SCORES
    }

    assert generator._aggregate_results_from_complete_individual_results() == expected_result


def test_highest_complete_results_rank() -> None:
    generator = EventAggregateResultsGenerator(
        individual_results=STUB_PLAYER_INDIVIDUAL_RESULTS,
        event_type=SeasonModelEventType.STANDARD,
    )

    complete_results = {
        name: result for name, result in TEST_PLAYER_CUMULATIVE_RESULTS.items() if name in PLAYERS_WITH_COMPLETE_SCORES
    }

    assert generator._highest_complete_results_rank(complete_results) == RankValue(4)


def test_highest_complete_results_rank_no_complete_results_returns_no_rank() -> None:
    generator = EventAggregateResultsGenerator(
        individual_results=STUB_PLAYER_INDIVIDUAL_RESULTS,
        event_type=SeasonModelEventType.STANDARD,
    )

    empty_dict: dict[str, SeasonModelEventPlayerAggregateResult] = {}

    assert generator._highest_complete_results_rank(empty_dict) == NoRankValue()


def test_aggregate_results_from_incomplete_individual_results() -> None:
    generator = EventAggregateResultsGenerator(
        individual_results=STUB_PLAYER_INDIVIDUAL_RESULTS,
        event_type=SeasonModelEventType.STANDARD,
    )

    expected_result = {
        "Steve Harasym": SeasonModelEventPlayerAggregateResult(
            gross_score_points=0.0,
            net_score_points=0.0,
            event_points=0.0,
            gross_score_rank=NoRankValue(),
            net_score_rank=NoRankValue(),
            event_rank=RankValue(6),  # This value is sensitive to the higheest ranke value below.
        )
    }

    assert (
        generator._aggregate_results_from_incomplete_individual_results(
            highest_event_rank_from_complete_results=RankValue(5)
        )
        == expected_result
    )


def test_event_rank_for_all_incomplete_results() -> None:
    generator = EventAggregateResultsGenerator(
        individual_results=STUB_PLAYER_INDIVIDUAL_RESULTS,
        event_type=SeasonModelEventType.STANDARD,
    )

    assert generator._event_rank_for_all_incomplete_results(RankValue(4)) == RankValue(5)
    assert generator._event_rank_for_all_incomplete_results(RankValue(12)) == RankValue(13)
    assert generator._event_rank_for_all_incomplete_results(RankValue(33)) == RankValue(34)


def test_event_rank_for_all_incomplete_results_no_rank_value_returns_1() -> None:
    generator = EventAggregateResultsGenerator(
        individual_results=STUB_PLAYER_INDIVIDUAL_RESULTS,
        event_type=SeasonModelEventType.STANDARD,
    )

    assert generator._event_rank_for_all_incomplete_results(NoRankValue()) == RankValue(1)
