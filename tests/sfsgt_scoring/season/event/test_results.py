import pytest

from sfsgt_scoring.season import rank
from sfsgt_scoring.season.event import results


def test_incomplete_player_event_result_singleton_implementation() -> None:
    result_1 = results.IncompletePlayerEventInividualResult()
    result_2 = results.IncompletePlayerEventInividualResult()

    assert result_1 is result_2


def test_player_event_result_is_complete_result_false() -> None:
    result_ = results.PlayerEventResult(
        individual_result=results.IncompletePlayerEventInividualResult(),
        cumulative_result=results.PlayerEventCumulativeResult(
            gross_score_points=100.0,
            net_score_points=100.0,
            event_points=200.0,
            gross_score_rank=rank.RankValue(3),
            net_score_rank=rank.RankValue(5),
            event_rank=rank.RankValue(4),
        ),
    )

    assert not result_.is_complete_result()


def test_player_event_result_is_complete_result_true() -> None:
    result_ = results.PlayerEventResult(
        individual_result=results.PlayerEventIndividualResult(
            course_handicap=16,
            front_9_gross=39,
            back_9_gross=49,
            total_gross=88,
            total_net=72,
            notable_holes=results.NotableHoles(),
            score_differential=16,
        ),
        cumulative_result=results.PlayerEventCumulativeResult(
            gross_score_points=100.0,
            net_score_points=100.0,
            event_points=200.0,
            gross_score_rank=rank.RankValue(3),
            net_score_rank=rank.RankValue(5),
            event_rank=rank.RankValue(4),
        ),
    )

    assert result_.is_complete_result()


def test_player_event_result_complete_result_property_getters() -> None:
    notable_holes = results.NotableHoles()
    notable_holes.set_hole(hole_num=1, score_type=results.NotableHoleType.BIRDIE)

    result_ = results.PlayerEventResult(
        individual_result=results.PlayerEventIndividualResult(
            course_handicap=16,
            front_9_gross=39,
            back_9_gross=49,
            total_gross=88,
            total_net=72,
            notable_holes=notable_holes,
            score_differential=16,
        ),
        cumulative_result=results.PlayerEventCumulativeResult(
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
    result_ = results.IncompletePlayerEventInividualResult()

    with pytest.raises(results.IncompletePlayerEventIndividualResultApiCallError):
        result_.course_handicap

    with pytest.raises(results.IncompletePlayerEventIndividualResultApiCallError):
        result_.front_9_gross

    with pytest.raises(results.IncompletePlayerEventIndividualResultApiCallError):
        result_.back_9_gross

    with pytest.raises(results.IncompletePlayerEventIndividualResultApiCallError):
        result_.total_gross

    with pytest.raises(results.IncompletePlayerEventIndividualResultApiCallError):
        result_.total_net

    with pytest.raises(results.IncompletePlayerEventIndividualResultApiCallError):
        result_.notable_holes


def test_individual_player_event_result_property_getters() -> None:
    notable_holes = results.NotableHoles()
    notable_holes.set_hole(hole_num=1, score_type=results.NotableHoleType.BIRDIE)

    result_ = results.PlayerEventIndividualResult(
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
    results.PlayerEventCumulativeResult(
        gross_score_points=100.0,
        net_score_points=100.0,
        event_points=200.0,
        gross_score_rank=rank.RankValue(3),
        net_score_rank=rank.RankValue(5),
        event_rank=rank.RankValue(4),
    )


def test_notable_holes_set_hole() -> None:
    notable_holes = results.NotableHoles()

    notable_holes.set_hole(hole_num=3, score_type=results.NotableHoleType.BIRDIE)
    notable_holes.set_hole(hole_num=5, score_type=results.NotableHoleType.BIRDIE)
    notable_holes.set_hole(hole_num=7, score_type=results.NotableHoleType.EAGLE)
    notable_holes.set_hole(hole_num=9, score_type=results.NotableHoleType.ALBATROSS)
    notable_holes.set_hole(hole_num=11, score_type=results.NotableHoleType.OVER_MAX)

    assert notable_holes._birdie_holes == [3, 5]
    assert notable_holes._eagle_holes == [7]
    assert notable_holes._albatross_holes == [9]
    assert notable_holes._over_max_holes == [11]


def test_notable_holes_birdie_holes() -> None:
    notable_holes = results.NotableHoles()
    notable_holes._birdie_holes = [3]

    assert notable_holes.birdie_holes() == [3]


def test_notable_holes_eagle_holes() -> None:
    notable_holes = results.NotableHoles()
    notable_holes._eagle_holes = [3]

    assert notable_holes.eagle_holes() == [3]


def test_notable_holes_albatross_holes() -> None:
    notable_holes = results.NotableHoles()
    notable_holes._albatross_holes = [3]

    assert notable_holes.albatross_holes() == [3]


def test_notable_holes_over_max_holes() -> None:
    notable_holes = results.NotableHoles()
    notable_holes._over_max_holes = [3]

    assert notable_holes.over_max_holes() == [3]


def test_notable_holes_setting_duplicate_hole_raises_error() -> None:
    notable_holes = results.NotableHoles()

    notable_holes.set_hole(hole_num=3, score_type=results.NotableHoleType.BIRDIE)
    with pytest.raises(results.NotableHoleDuplicationError):
        notable_holes.set_hole(hole_num=3, score_type=results.NotableHoleType.EAGLE)


def test_notable_holes_has_hole_num_been_set_true() -> None:
    notable_holes = results.NotableHoles()

    notable_holes._birdie_holes = [1, 6]
    notable_holes._eagle_holes = [4]
    notable_holes._albatross_holes = [12]
    notable_holes._over_max_holes = [16]

    assert notable_holes._has_hole_num_been_set(4)


def test_notable_holes_has_hole_num_been_set_false() -> None:
    notable_holes = results.NotableHoles()

    notable_holes._birdie_holes = [1, 6]
    notable_holes._eagle_holes = [4]
    notable_holes._albatross_holes = [12]
    notable_holes._over_max_holes = [16]

    assert not notable_holes._has_hole_num_been_set(7)


def test_notable_holes_all_hole_nums() -> None:
    notable_holes = results.NotableHoles()

    notable_holes._birdie_holes = [1, 6]
    notable_holes._eagle_holes = [4]
    notable_holes._albatross_holes = [12]
    notable_holes._over_max_holes = [16]

    assert notable_holes._all_hole_nums() == [1, 6, 4, 12, 16]
