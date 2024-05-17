from ... import rank
from .. import inputs, event, results

TEST_EVENT_INPUT = inputs.EventInput(
    course=inputs.CourseInput(
        name="Poppy Ridge",
        tee=inputs.CourseTeeData(
            name="White",
            rating=70.2,
            slope=128,
        ),
        hole_pars=inputs.CourseHolePars({
            1: 4,
            2: 4,
            3: 3,
            4: 4,
            5: 5,
            6: 4,
            7: 3,
            8: 4,
            9: 5,
            10: 4,
            11: 3,
            12: 4,
            13: 4,
            14: 5,
            15: 4,
            16: 3,
            17: 5,
            18: 4,
        }),
    ),
    type=inputs.EventType.STANDARD,
    players={
        "Stanton Turner": inputs.EventPlayerInput(
            handicap_index=14,
            scorecard=inputs.Scorecard(
                strokes_per_hole={1: 5, 2: 4, 3: 5, 4: 6, 5: 5, 6: 6, 7: 4, 8: 4, 9: 5, 10: 6, 11: 6, 12: 5, 13: 4, 14: 4, 15: 4, 16: 4, 17: 4, 18: 5}   # noqa: E501
            ),
        ),
        "John Fratello": inputs.EventPlayerInput(
            handicap_index=15.8,
            scorecard=inputs.Scorecard(
                strokes_per_hole={1: 5, 2: 7, 3: 6, 4: 3, 5: 5, 6: 6, 7: 3, 8: 5, 9: 6, 10: 7, 11: 6, 12: 4, 13: 3, 14: 5, 15: 3, 16: 4, 17: 5, 18: 6}   # noqa: E501
            ),
        ),
        "Steve Harasym": inputs.EventPlayerInput(
            handicap_index=15.8,
            scorecard=inputs.IncompleteScorecard(),
        ),
    }
)

STANTON_NOTABLE_HOLES = results.NotableHoles()
STANTON_NOTABLE_HOLES.set_hole(14, results.NotableHoleType.BIRDIE)
STANTON_NOTABLE_HOLES.set_hole(17, results.NotableHoleType.BIRDIE)

JOHN_NOTABLE_HOLES = results.NotableHoles()
JOHN_NOTABLE_HOLES.set_hole(4, results.NotableHoleType.BIRDIE)
JOHN_NOTABLE_HOLES.set_hole(13, results.NotableHoleType.BIRDIE)
JOHN_NOTABLE_HOLES.set_hole(15, results.NotableHoleType.BIRDIE)

TEST_PLAYER_INDIVIDUAL_RESULTS: dict[str, results.IPlayerEventIndividualResult] = {
    "Stanton Turner": results.PlayerEventIndividualResult(
        course_handicap=14,
        front_9_gross=44,
        back_9_gross=42,
        total_gross=86,
        total_net=72,
        notable_holes=STANTON_NOTABLE_HOLES,
    ),
    "John Fratello": results.PlayerEventIndividualResult(
        course_handicap=16,
        front_9_gross=46,
        back_9_gross=43,
        total_gross=89,
        total_net=73,
        notable_holes=JOHN_NOTABLE_HOLES,
    ),
    "Steve Harasym": results.IncompletePlayerEventInividualResult(),
}

TEST_PLAYER_CUMULATIVE_RESULTS = {
    "Stanton Turner": results.PlayerEventCumulativeResult(
        gross_score_points=50.0,
        net_score_points=50.0,
        event_points=100.0,
        gross_score_rank=rank.RankValue(1),
        net_score_rank=rank.RankValue(1),
        event_rank=rank.RankValue(1),
    ),
    "John Fratello": results.PlayerEventCumulativeResult(
        gross_score_points=45.0,
        net_score_points=45.0,
        event_points=90.0,
        gross_score_rank=rank.RankValue(2),
        net_score_rank=rank.RankValue(2),
        event_rank=rank.RankValue(2),
    ),
    "Steve Harasym": results.PlayerEventCumulativeResult(
        gross_score_points=0.0,
        net_score_points=0.0,
        event_points=0.0,
        gross_score_rank=rank.NoRankValue(),
        net_score_rank=rank.NoRankValue(),
        event_rank=rank.RankValue(3),
    )
}


def test_event_construct() -> None:
    event.Event(input=TEST_EVENT_INPUT)


def test_event_player_individual_results() -> None:
    event_ = event.Event(input=TEST_EVENT_INPUT)
    result_ = event_._player_individual_results()
    assert result_ == TEST_PLAYER_INDIVIDUAL_RESULTS


def test_event_player_cumulative_results() -> None:
    event_ = event.Event(input=TEST_EVENT_INPUT)
    result_ = event_._player_cumulative_results(TEST_PLAYER_INDIVIDUAL_RESULTS)
    assert result_ == TEST_PLAYER_CUMULATIVE_RESULTS


def test_cumulative_results_construct() -> None:
    cum_result = event.CumulativeResults(
        player_individual_results=TEST_PLAYER_INDIVIDUAL_RESULTS,
        event_type=inputs.EventType.STANDARD,
    )

    expected_complete_individual_player_results = {
        player_name: result
        for player_name, result in TEST_PLAYER_INDIVIDUAL_RESULTS.items()
        if player_name in ["Stanton Turner", "John Fratello"]
    }
    expected_incomplete_individual_player_results = {
        player_name: result
        for player_name, result in TEST_PLAYER_INDIVIDUAL_RESULTS.items()
        if player_name in ["Steve Harasym"]
    }

    assert cum_result._complete_results == expected_complete_individual_player_results
    assert cum_result._incomplete_results == expected_incomplete_individual_player_results


def test_cumulative_results_from_complete_individual_results() -> None:
    cum_result = event.CumulativeResults(
        player_individual_results=TEST_PLAYER_INDIVIDUAL_RESULTS,
        event_type=inputs.EventType.STANDARD,
    )

    expected_result = {
        name: result
        for name, result in TEST_PLAYER_CUMULATIVE_RESULTS.items()
        if name in {"Stanton Turner", "John Fratello"}
    }

    assert cum_result._cumulative_results_from_complete_individual_results() == expected_result


def test_highest_complete_results_rank() -> None:
    cum_result = event.CumulativeResults(
        player_individual_results=TEST_PLAYER_INDIVIDUAL_RESULTS,
        event_type=inputs.EventType.STANDARD,
    )

    complete_results = {
        name: result
        for name, result in TEST_PLAYER_CUMULATIVE_RESULTS.items()
        if name in {"Stanton Turner", "John Fratello"}
    }

    assert cum_result._highest_complete_results_rank(complete_results) == rank.RankValue(2)


def test_highest_complete_results_rank_no_complete_results_returns_no_rank() -> None:
    cum_result = event.CumulativeResults(
        player_individual_results=TEST_PLAYER_INDIVIDUAL_RESULTS,
        event_type=inputs.EventType.STANDARD,
    )

    empty_dict: dict[str, results.PlayerEventCumulativeResult] = {}

    assert cum_result._highest_complete_results_rank(empty_dict) == rank.NoRankValue()


def test_cumulative_results_from_incomplete_individual_results() -> None:
    cum_result = event.CumulativeResults(
        player_individual_results=TEST_PLAYER_INDIVIDUAL_RESULTS,
        event_type=inputs.EventType.STANDARD,
    )

    expected_result = {
        "Steve Harasym": results.PlayerEventCumulativeResult(
            gross_score_points=0.0,
            net_score_points=0.0,
            event_points=0.0,
            gross_score_rank=rank.NoRankValue(),
            net_score_rank=rank.NoRankValue(),
            event_rank=rank.RankValue(6),  # This value is sensitive to the higheest ranke value below.
        )
    }

    assert cum_result._cumulative_results_from_incomplete_individual_results(
        highest_event_rank_from_complete_results=rank.RankValue(5)
    ) == expected_result


def test_event_rank_for_all_incomplete_results() -> None:
    cum_result = event.CumulativeResults(
        player_individual_results=TEST_PLAYER_INDIVIDUAL_RESULTS,
        event_type=inputs.EventType.STANDARD,
    )

    assert cum_result._event_rank_for_all_incomplete_results(rank.RankValue(4)) == rank.RankValue(5)
    assert cum_result._event_rank_for_all_incomplete_results(rank.RankValue(12)) == rank.RankValue(13)
    assert cum_result._event_rank_for_all_incomplete_results(rank.RankValue(33)) == rank.RankValue(34)


def test_event_rank_for_all_incomplete_results_no_rank_value_returns_1() -> None:
    cum_result = event.CumulativeResults(
        player_individual_results=TEST_PLAYER_INDIVIDUAL_RESULTS,
        event_type=inputs.EventType.STANDARD,
    )

    assert cum_result._event_rank_for_all_incomplete_results(rank.NoRankValue()) == rank.RankValue(1)
