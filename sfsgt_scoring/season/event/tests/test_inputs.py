import pytest

from .. import inputs


def test_course_tee_data_construct_nominal() -> None:
    tee_data = inputs.CourseTeeData(
        name="tee_name",
        rating=72.0,
        slope=113,
    )

    assert tee_data.name == "tee_name"
    assert tee_data.rating == 72.0
    assert tee_data.slope == 113


def test_course_tee_data_rating_too_low_raises_error() -> None:
    with pytest.raises(inputs.CourseDataVerificationError):
        inputs.CourseTeeData(
            name="tee name",
            rating=59.0,
            slope=113,
        )


def test_course_tee_data_rating_too_high_raises_error() -> None:
    with pytest.raises(inputs.CourseDataVerificationError):
        inputs.CourseTeeData(
            name="tee name",
            rating=81.0,
            slope=113,
        )


def test_course_tee_data_slope_too_low_raises_error() -> None:
    with pytest.raises(inputs.CourseDataVerificationError):
        inputs.CourseTeeData(
            name="tee name",
            rating=72.0,
            slope=54,
        )


def test_course_tee_data_slope_too_high_raises_error() -> None:
    with pytest.raises(inputs.CourseDataVerificationError):
        inputs.CourseTeeData(
            name="tee name",
            rating=72.0,
            slope=156,
        )


def test_course_hole_pars_construct_nominal() -> None:
    hole_pars = inputs.CourseHolePars({
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
    })

    # A couple of spot checks to show how data is accessed
    assert hole_pars[1] == 4
    assert hole_pars[9] == 5
    assert hole_pars[17] == 3


def test_course_hole_pars_construct_missing_holes_raises_error() -> None:
    with pytest.raises(inputs.CourseDataVerificationError):
        inputs.CourseHolePars({
            1: 4,
            2: 4,
            3: 3,
            4: 5,
            5: 4,
            6: 4,
            7: 4,
            8: 3,
            9: 5,
        })


def test_course_hole_pars_construct_extra_holes_raises_error() -> None:
    with pytest.raises(inputs.CourseDataVerificationError):
        inputs.CourseHolePars({
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
            19: 4,
        })


def test_course_hole_pars_construct_hole_par_values_too_high_raises_error() -> None:
    with pytest.raises(inputs.CourseDataVerificationError):
        inputs.CourseHolePars({
            1: 6,  # This is the violating value, should be one of 3, 4, or 5.
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
        })


def test_course_hole_pars_construct_hole_par_values_too_low_raises_error() -> None:
    with pytest.raises(inputs.CourseDataVerificationError):
        inputs.CourseHolePars({
            1: 2,  # This is the violating value, should be one of 3, 4, or 5.
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
        })


def test_course_hole_pars_total_par() -> None:
    hole_pars = inputs.CourseHolePars({
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
    })

    assert hole_pars.total_par() == 72


def test_holes_scores_construct() -> None:
    inputs.Scorecard(
        strokes_per_hole={1: 5, 2: 7, 3: 6, 4: 3, 5: 5, 6: 6, 7: 3, 8: 5, 9: 6, 10: 7, 11: 6, 12: 4, 13: 3, 14: 5, 15: 3, 16: 4, 17: 5, 18: 6},  # noqa: E501
    )


def test_hole_scores_get_scores() -> None:
    scores = {1: 5, 2: 7, 3: 6, 4: 3, 5: 5, 6: 6, 7: 3, 8: 5, 9: 6, 10: 7, 11: 6, 12: 4, 13: 3, 14: 5, 15: 3, 16: 4, 17: 5, 18: 6}  # noqa: E501

    hole_scores = inputs.Scorecard(strokes_per_hole=scores)

    assert hole_scores.strokes_per_hole() == scores
