import pytest

from season_model.model_api.result import notable_holes


def test_notable_holes_set_hole() -> None:
    notable_hls = notable_holes.NotableHoles()

    notable_hls.set_hole(hole_num=3, hole_type=notable_holes.NotableHoleType.BIRDIE)
    notable_hls.set_hole(hole_num=5, hole_type=notable_holes.NotableHoleType.BIRDIE)
    notable_hls.set_hole(hole_num=7, hole_type=notable_holes.NotableHoleType.EAGLE)
    notable_hls.set_hole(hole_num=9, hole_type=notable_holes.NotableHoleType.ALBATROSS)
    notable_hls.set_hole(hole_num=11, hole_type=notable_holes.NotableHoleType.OVER_MAX)

    assert notable_hls._holes[3] == notable_holes.NotableHoleType.BIRDIE
    assert notable_hls._holes[5] == notable_holes.NotableHoleType.BIRDIE
    assert notable_hls._holes[7] == notable_holes.NotableHoleType.EAGLE
    assert notable_hls._holes[9] == notable_holes.NotableHoleType.ALBATROSS
    assert notable_hls._holes[11] == notable_holes.NotableHoleType.OVER_MAX


def test_notable_holes_birdie_holes() -> None:
    notable_hls = notable_holes.NotableHoles()
    notable_hls.set_hole(hole_num=3, hole_type=notable_holes.NotableHoleType.BIRDIE)

    assert notable_hls.birdie_holes() == [3]


def test_notable_holes_eagle_holes() -> None:
    notable_hls = notable_holes.NotableHoles()
    notable_hls.set_hole(hole_num=3, hole_type=notable_holes.NotableHoleType.EAGLE)

    assert notable_hls.eagle_holes() == [3]


def test_notable_holes_albatross_holes() -> None:
    notable_hls = notable_holes.NotableHoles()
    notable_hls.set_hole(hole_num=3, hole_type=notable_holes.NotableHoleType.ALBATROSS)

    assert notable_hls.albatross_holes() == [3]


def test_notable_holes_over_max_holes() -> None:
    notable_hls = notable_holes.NotableHoles()
    notable_hls.set_hole(hole_num=3, hole_type=notable_holes.NotableHoleType.OVER_MAX)

    assert notable_hls.over_max_holes() == [3]


def test_notable_holes_setting_duplicate_hole_raises_error() -> None:
    notable_hls = notable_holes.NotableHoles()

    notable_hls.set_hole(hole_num=3, hole_type=notable_holes.NotableHoleType.BIRDIE)

    with pytest.raises(notable_holes.NotableHoleDuplicationError):
        notable_hls.set_hole(hole_num=3, hole_type=notable_holes.NotableHoleType.EAGLE)


def test_notable_holes_has_hole_num_been_set_true() -> None:
    notable_hls = notable_holes.NotableHoles()
    notable_hls.set_hole(hole_num=4, hole_type=notable_holes.NotableHoleType.BIRDIE)

    assert notable_hls._has_hole_num_been_set(4)


def test_notable_holes_has_hole_num_been_set_false() -> None:
    notable_hls = notable_holes.NotableHoles()
    notable_hls.set_hole(hole_num=4, hole_type=notable_holes.NotableHoleType.BIRDIE)

    assert not notable_hls._has_hole_num_been_set(7)


def test_notable_holes_all_hole_nums() -> None:
    notable_hls = notable_holes.NotableHoles()

    notable_hls.set_hole(hole_num=1, hole_type=notable_holes.NotableHoleType.BIRDIE)
    notable_hls.set_hole(hole_num=4, hole_type=notable_holes.NotableHoleType.EAGLE)
    notable_hls.set_hole(hole_num=6, hole_type=notable_holes.NotableHoleType.BIRDIE)
    notable_hls.set_hole(hole_num=12, hole_type=notable_holes.NotableHoleType.ALBATROSS)
    notable_hls.set_hole(hole_num=16, hole_type=notable_holes.NotableHoleType.OVER_MAX)

    assert notable_hls._all_hole_nums() == [1, 4, 6, 12, 16]


def test_notable_holes_set_hole_number_out_of_range_raises_error() -> None:
    notable_hls = notable_holes.NotableHoles()

    with pytest.raises(notable_holes.UnknownHoleNumberError):
        notable_hls.set_hole(hole_num=19, hole_type=notable_holes.NotableHoleType.BIRDIE)

    with pytest.raises(notable_holes.UnknownHoleNumberError):
        notable_hls.set_hole(hole_num=0, hole_type=notable_holes.NotableHoleType.BIRDIE)