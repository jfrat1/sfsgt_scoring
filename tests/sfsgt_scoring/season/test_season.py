import copy

from sfsgt_scoring.season import event, rank, season
from sfsgt_scoring.season.event import results as event_results

SEASON_INPUT = season.SeasonInput(
    events={
        "Standard Event": event.EventInput(
            course=event.CourseInput(
                name="course_a",
                tee=event.CourseTeeData(
                    name="white",
                    rating=72.2,
                    slope=130,
                ),
                hole_pars=event.CourseHolePars(
                    {
                        1: 4,
                        2: 4,
                        3: 3,
                        4: 5,
                        5: 4,
                        6: 4,
                        7: 4,
                        8: 3,
                        9: 5,
                        10: 5,
                        11: 3,
                        12: 5,
                        13: 4,
                        14: 4,
                        15: 4,
                        16: 4,
                        17: 3,
                        18: 4,
                    }
                ),
            ),
            type=event.EventType.STANDARD,
            players={
                "Stanton Turner": event.EventPlayerInput(
                    handicap_index=12.0,
                    scorecard=event.Scorecard(
                        strokes_per_hole={
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
                ),
                "John Fratello": event.EventPlayerInput(
                    handicap_index=16.4,
                    scorecard=event.Scorecard(
                        strokes_per_hole={
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
                ),
            },
        ),
        "Major Event": event.EventInput(
            course=event.CourseInput(
                name="course_b",
                tee=event.CourseTeeData(
                    name="blue",
                    rating=72.8,
                    slope=138,
                ),
                hole_pars=event.CourseHolePars(
                    {
                        1: 4,
                        2: 4,
                        3: 3,
                        4: 5,
                        5: 4,
                        6: 4,
                        7: 4,
                        8: 3,
                        9: 5,
                        10: 5,
                        11: 3,
                        12: 5,
                        13: 4,
                        14: 4,
                        15: 4,
                        16: 4,
                        17: 3,
                        18: 4,
                    }
                ),
            ),
            type=event.EventType.MAJOR,
            players={
                "Stanton Turner": event.EventPlayerInput(
                    handicap_index=12.0,
                    scorecard=event.Scorecard(
                        strokes_per_hole={
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
                ),
                "John Fratello": event.EventPlayerInput(
                    handicap_index=16.4,
                    scorecard=event.Scorecard(
                        strokes_per_hole={
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
                ),
            },
        ),
    },
    player_names=["Stanton Turner", "John Fratello"],
)

STANTON_NOTABLE_HOLES = event_results.NotableHoles()

# The same sets of notable holes apply to both events
JOHN_NOTABLE_HOLES = event_results.NotableHoles()
JOHN_NOTABLE_HOLES.set_hole(4, event_results.NotableHoleType.EAGLE)
JOHN_NOTABLE_HOLES.set_hole(7, event_results.NotableHoleType.BIRDIE)
JOHN_NOTABLE_HOLES.set_hole(12, event_results.NotableHoleType.BIRDIE)
JOHN_NOTABLE_HOLES.set_hole(13, event_results.NotableHoleType.BIRDIE)
JOHN_NOTABLE_HOLES.set_hole(15, event_results.NotableHoleType.BIRDIE)

STANDARD_EVENT_RESULT = event_results.EventResult(
    players={
        "Stanton Turner": event_results.PlayerEventResult(
            individual_result=event_results.PlayerEventIndividualResult(
                course_handicap=14,
                front_9_gross=44,
                back_9_gross=42,
                total_gross=86,
                total_net=72,
                notable_holes=STANTON_NOTABLE_HOLES,
                score_differential=12.0,
            ),
            cumulative_result=event_results.PlayerEventCumulativeResult(
                gross_score_points=50.0,
                net_score_points=45.0,
                event_points=95.0,
                gross_score_rank=rank.RankValue(1),
                net_score_rank=rank.RankValue(2),
                event_rank=rank.RankValue(1),
            ),
        ),
        "John Fratello": event_results.PlayerEventResult(
            individual_result=event_results.PlayerEventIndividualResult(
                course_handicap=19,
                front_9_gross=46,
                back_9_gross=43,
                total_gross=89,
                total_net=70,
                notable_holes=JOHN_NOTABLE_HOLES,
                score_differential=14.6,
            ),
            cumulative_result=event_results.PlayerEventCumulativeResult(
                gross_score_points=45.0,
                net_score_points=50.0,
                event_points=95.0,
                gross_score_rank=rank.RankValue(2),
                net_score_rank=rank.RankValue(1),
                event_rank=rank.RankValue(1),
            ),
        ),
    }
)

MAJOR_EVENT_RESULT = event_results.EventResult(
    players={
        "Stanton Turner": event_results.PlayerEventResult(
            individual_result=event_results.PlayerEventIndividualResult(
                course_handicap=15,
                front_9_gross=44,
                back_9_gross=42,
                total_gross=86,
                total_net=71,
                notable_holes=STANTON_NOTABLE_HOLES,
                score_differential=10.8,
            ),
            cumulative_result=event_results.PlayerEventCumulativeResult(
                gross_score_points=100.0,
                net_score_points=90.0,
                event_points=190.0,
                gross_score_rank=rank.RankValue(1),
                net_score_rank=rank.RankValue(2),
                event_rank=rank.RankValue(1),
            ),
        ),
        "John Fratello": event_results.PlayerEventResult(
            individual_result=event_results.PlayerEventIndividualResult(
                course_handicap=21,
                front_9_gross=46,
                back_9_gross=43,
                total_gross=89,
                total_net=68,
                notable_holes=JOHN_NOTABLE_HOLES,
                score_differential=13.3,
            ),
            cumulative_result=event_results.PlayerEventCumulativeResult(
                gross_score_points=90.0,
                net_score_points=100.0,
                event_points=190.0,
                gross_score_rank=rank.RankValue(2),
                net_score_rank=rank.RankValue(1),
                event_rank=rank.RankValue(1),
            ),
        ),
    }
)

EVENT_RESULTS = {
    "Standard Event": STANDARD_EVENT_RESULT,
    "Major Event": MAJOR_EVENT_RESULT,
}

STANTON_CUMULATIVE_RESULTS_UNRANKED = season.CumulativePlayerResult(
    season_points=285.0,
    num_birdies=0,
    num_eagles=0,
    num_albatrosses=0,
    num_events_completed=2,
    num_net_strokes_wins=0,
    num_net_strokes_top_fives=2,
    num_net_strokes_top_tens=2,
    num_event_wins=2,
    num_event_top_fives=2,
    num_event_top_tens=2,
    season_handicap=15.2,
)
STANTON_CUMULATIVE_RESULTS_RANKED = copy.deepcopy(STANTON_CUMULATIVE_RESULTS_UNRANKED)
STANTON_CUMULATIVE_RESULTS_RANKED.set_season_rank(rank.RankValue(1))

JOHN_CUMULATIVE_RESULTS_UNRANKED = season.CumulativePlayerResult(
    season_points=285.0,
    num_birdies=8,
    num_eagles=2,
    num_albatrosses=0,
    num_events_completed=2,
    num_net_strokes_wins=2,
    num_net_strokes_top_fives=2,
    num_net_strokes_top_tens=2,
    num_event_wins=2,
    num_event_top_fives=2,
    num_event_top_tens=2,
    season_handicap=17.7,
)
JOHN_CUMULATIVE_RESULTS_RANKED = copy.deepcopy(JOHN_CUMULATIVE_RESULTS_UNRANKED)
JOHN_CUMULATIVE_RESULTS_RANKED.set_season_rank(rank.RankValue(1))

CUMULATIVE_RESULTS_UNRANKED = {
    "Stanton Turner": STANTON_CUMULATIVE_RESULTS_UNRANKED,
    "John Fratello": JOHN_CUMULATIVE_RESULTS_UNRANKED,
}

CUMULATIVE_RESULTS_RANKED = season.CumulativeResults(
    players={
        "Stanton Turner": STANTON_CUMULATIVE_RESULTS_RANKED,
        "John Fratello": JOHN_CUMULATIVE_RESULTS_RANKED,
    }
)


def test_season_construct() -> None:
    season_ = season.Season(SEASON_INPUT)

    assert season_._input == SEASON_INPUT

    assert list(season_._events.keys()) == ["Standard Event", "Major Event"]


def test_season_results() -> None:
    season_ = season.Season(SEASON_INPUT)

    season_results = season_.results()

    assert season_results == season.SeasonResults(
        events=EVENT_RESULTS,
        cumulative=CUMULATIVE_RESULTS_RANKED,
    )


def test_event_results() -> None:
    season_ = season.Season(SEASON_INPUT)

    season_event_results = season_._event_results()
    assert season_event_results == EVENT_RESULTS


def test_cumulative_results() -> None:
    season_ = season.Season(SEASON_INPUT)

    season_cumulative_results = season_._cumulative_results(EVENT_RESULTS)
    assert season_cumulative_results == CUMULATIVE_RESULTS_RANKED


def test_cumulative_results_unranked() -> None:
    season_ = season.Season(SEASON_INPUT)

    unranked_results = season_._unranked_cumulative_results(EVENT_RESULTS)

    assert unranked_results == CUMULATIVE_RESULTS_UNRANKED


def test_player_cumulative_results() -> None:
    season_ = season.Season(SEASON_INPUT)

    assert (
        season_._player_cumulative_results(
            event_results=EVENT_RESULTS,
            player_name="Stanton Turner",
        )
        == STANTON_CUMULATIVE_RESULTS_UNRANKED
    )

    assert (
        season_._player_cumulative_results(
            event_results=EVENT_RESULTS,
            player_name="John Fratello",
        )
        == JOHN_CUMULATIVE_RESULTS_UNRANKED
    )


def test_player_season_ranks() -> None:
    def make_player_result(season_points: float) -> season.CumulativePlayerResult:
        return season.CumulativePlayerResult(
            season_points=season_points,
            num_albatrosses=0,
            num_birdies=0,
            num_eagles=0,
            num_events_completed=0,
            num_net_strokes_wins=0,
            num_net_strokes_top_fives=0,
            num_net_strokes_top_tens=0,
            num_event_wins=0,
            num_event_top_fives=0,
            num_event_top_tens=0,
            season_handicap=0.0,
        )

    cumulative_player_results = {
        "Player1": make_player_result(season_points=100),
        "Player2": make_player_result(season_points=100),
        "Player3": make_player_result(season_points=105),
        "Player4": make_player_result(season_points=110),
        "Player5": make_player_result(season_points=120),
        "Player6": make_player_result(season_points=110),
    }

    season_ = season.Season(SEASON_INPUT)

    player_ranks = season_._player_season_ranks(cumulative_player_results)

    assert player_ranks == {
        "Player1": rank.RankValue(5),
        "Player2": rank.RankValue(5),
        "Player3": rank.RankValue(4),
        "Player4": rank.RankValue(2),
        "Player5": rank.RankValue(1),
        "Player6": rank.RankValue(2),
    }
