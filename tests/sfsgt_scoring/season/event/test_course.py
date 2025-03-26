import pytest
from sfsgt_scoring.season.event import course, inputs

TEST_COURSE_INPUT = inputs.CourseInput(
    name="Presidio",
    tee=inputs.CourseTeeData(
        name="blue",
        rating=69.5,
        slope=129,
    ),
    hole_pars=inputs.CourseHolePars(
        {
            1: 4,
            2: 5,
            3: 4,
            4: 3,
            5: 4,
            6: 4,
            7: 3,
            8: 4,
            9: 5,
            10: 5,
            11: 4,
            12: 4,
            13: 3,
            14: 4,
            15: 3,
            16: 4,
            17: 4,
            18: 5,
        },  # noqa: E501
    ),
)


def test_course_construct() -> None:
    course.Course(input=TEST_COURSE_INPUT)


def test_player_course_handicap() -> None:
    course_ = course.Course(input=TEST_COURSE_INPUT)

    assert course_.player_course_handicap(player_handicap_index=16.4) == 16
    assert course_.player_course_handicap(player_handicap_index=0.7) == -2


def test_hole_par() -> None:
    course_ = course.Course(input=TEST_COURSE_INPUT)

    assert course_.hole_par(1) == 4
    assert course_.hole_par(9) == 5


def test_hole_par_invalid_hole_raises_error() -> None:
    course_ = course.Course(input=TEST_COURSE_INPUT)

    with pytest.raises(course.CourseHoleRequestError):
        course_.hole_par(0)

    with pytest.raises(course.CourseHoleRequestError):
        course_.hole_par(19)
