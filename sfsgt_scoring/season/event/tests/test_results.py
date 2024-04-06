import pytest

from .. import results


def test_event_player_result_construct() -> None:
    result = results.EventPlayerResult(
        course_handicap=18,
        front_9_gross=36,
        back_9_gross=36,
        total_gross=72,
        total_net=64,
        below_par_holes=results.BelowParHoles(),
    )

    # Check singleton implementation of NoRank type
    # TODO: move into a test on the rank.py module directly.
    assert result.event_rank is result.gross_score_rank is result.net_score_rank

    assert 0.0 == result.event_points == result.gross_score_points == result.net_score_points


def test_below_par_holes_set_hole() -> None:
    below_par_holes = results.BelowParHoles()

    below_par_holes.set_hole(hole_num=3, score_type=results.BelowParScoreType.BIRDIE)
    below_par_holes.set_hole(hole_num=5, score_type=results.BelowParScoreType.BIRDIE)
    below_par_holes.set_hole(hole_num=7, score_type=results.BelowParScoreType.EAGLE)
    below_par_holes.set_hole(hole_num=9, score_type=results.BelowParScoreType.ALBATROSS)

    assert below_par_holes._birdie_holes == {3, 5}
    assert below_par_holes._eagle_holes == {7}
    assert below_par_holes._albatross_holes == {9}


def test_below_par_holes_birdie_holes() -> None:
    below_par_holes = results.BelowParHoles()
    below_par_holes._birdie_holes = {3}

    assert below_par_holes.birdie_holes() == {3}


def test_below_par_holes_eagle_holes() -> None:
    below_par_holes = results.BelowParHoles()
    below_par_holes._eagle_holes = {3}

    assert below_par_holes.eagle_holes() == {3}


def test_below_par_holes_albatross_holes() -> None:
    below_par_holes = results.BelowParHoles()
    below_par_holes._albatross_holes = {3}

    assert below_par_holes.albatross_holes() == {3}


def test_below_par_holes_setting_duplicate_hole_raises_error() -> None:
    below_par_holes = results.BelowParHoles()

    below_par_holes.set_hole(hole_num=3, score_type=results.BelowParScoreType.BIRDIE)
    with pytest.raises(results.BelowParHoleDuplicationError):
        below_par_holes.set_hole(hole_num=3, score_type=results.BelowParScoreType.EAGLE)


def test_below_par_holes_has_hole_num_been_set_true() -> None:
    below_par_holes = results.BelowParHoles()

    below_par_holes._birdie_holes = {1, 6}
    below_par_holes._eagle_holes = {4}
    below_par_holes._albatross_holes = {12}

    assert below_par_holes._has_hole_num_been_set(4)


def test_below_par_holes_has_hole_num_been_set_false() -> None:
    below_par_holes = results.BelowParHoles()

    below_par_holes._birdie_holes = {1, 6}
    below_par_holes._eagle_holes = {4}
    below_par_holes._albatross_holes = {12}

    assert not below_par_holes._has_hole_num_been_set(7)


def test_below_par_holes_all_hole_nums() -> None:
    below_par_holes = results.BelowParHoles()

    below_par_holes._birdie_holes = {1, 6}
    below_par_holes._eagle_holes = {4}
    below_par_holes._albatross_holes = {12}

    assert below_par_holes._all_hole_nums() == {1, 4, 6, 12}
