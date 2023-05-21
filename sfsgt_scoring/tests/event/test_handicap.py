from sfsgt_scoring import handicap


def test_calc_course_handicap() -> None:
    """Check the calc_course_handicap funtion.

    This function calculates a "course handicap" for a specific player on a specific course.
    The truth data for this test was made using the USGA course handicap calculator:
    https://www.usga.org/course-handicap-calculator.html
    """
    assert 15 == handicap.calc_course_handicap(
        handicap_index=15.6,
        par=72,
        rating=69.5,
        slope=129,
    )

    assert 3 == handicap.calc_course_handicap(
        handicap_index=5.2,
        par=72,
        rating=69.0,
        slope=131,
    )

    assert 21 == handicap.calc_course_handicap(
        handicap_index=18,
        par=72,
        rating=72.7,
        slope=125,
    )

    # This one is contrived to be just below the rounding edge at 20.5
    assert 20 == handicap.calc_course_handicap(
        handicap_index=17.8991,
        par=72,
        rating=72.7,
        slope=125,
    )
