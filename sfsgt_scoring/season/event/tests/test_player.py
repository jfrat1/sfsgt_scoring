from .. import course, inputs, player, results

TEST_PLAYER_HOLE_SCORES = {
    1: 5, 2: 2, 3: 6, 4: 3, 5: 5, 6: 6, 7: 3, 8: 5, 9: 3, 10: 4, 11: 6, 12: 11, 13: 3, 14: 5, 15: 3, 16: 4, 17: 5, 18: 6
}
TEST_COURSE_HOLE_PARS = {
    1: 4, 2: 5, 3: 4, 4: 3, 5: 4, 6: 4, 7: 3, 8: 4, 9: 5, 10: 5, 11: 4, 12: 4, 13: 3, 14: 4, 15: 3, 16: 4, 17: 4, 18: 5
}
TEST_PLAYER_HOLE_SCORES_WITH_MAX_STROKES_LIMIT = {
    1: 5, 2: 2, 3: 6, 4: 3, 5: 5, 6: 6, 7: 3, 8: 5, 9: 3, 10: 4, 11: 6, 12: 10, 13: 3, 14: 5, 15: 3, 16: 4, 17: 5, 18: 6
}

# This data is sensitive to changes in either the player hole scores or course hole pars
EXPECTED_NOTABLE_HOLES = results.NotableHoles()
EXPECTED_NOTABLE_HOLES.set_hole(2, results.NotableHoleType.ALBATROSS)
EXPECTED_NOTABLE_HOLES.set_hole(9, results.NotableHoleType.EAGLE)
EXPECTED_NOTABLE_HOLES.set_hole(10, results.NotableHoleType.BIRDIE)
EXPECTED_NOTABLE_HOLES.set_hole(12, results.NotableHoleType.OVER_MAX)

TEST_PLAYER_INPUT = inputs.EventPlayerInput(
    handicap_index=16.0,
    scorecard=inputs.Scorecard(strokes_per_hole=TEST_PLAYER_HOLE_SCORES),
)

TEST_COURSE_INPUT = inputs.CourseInput(
    name="Presidio",
    tee=inputs.CourseTeeData(
        name="blue",
        rating=69.5,
        slope=129,
    ),
    hole_pars=inputs.CourseHolePars(TEST_COURSE_HOLE_PARS),
)

TEST_COURSE_HANDICAP = 16

TEST_COURSE = course.Course(input=TEST_COURSE_INPUT)


def test_player_construct() -> None:
    player.EventPlayer(input=TEST_PLAYER_INPUT, course_=TEST_COURSE)


def test_player_class_constants() -> None:
    assert player.EventPlayer._FRONT_9_HOLES == (1, 2, 3, 4, 5, 6, 7, 8 ,9)
    assert player.EventPlayer._BACK_9_HOLES == (10, 11, 12, 13, 14, 15, 16, 17, 18)
    assert player.EventPlayer._ALL_HOLES == (
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18
    )


def test_player_adjust_strokes_for_hole_max() -> None:
    player_ = player.EventPlayer(input=TEST_PLAYER_INPUT, course_=TEST_COURSE)

    assert player_._adjust_scorecard_for_max_hole_strokes() == inputs.Scorecard(
        strokes_per_hole=TEST_PLAYER_HOLE_SCORES_WITH_MAX_STROKES_LIMIT
    )
    assert player_._notable_holes.over_max_holes() == [12]


def test_player_note_below_par_holes() -> None:
    player_ = player.EventPlayer(input=TEST_PLAYER_INPUT, course_=TEST_COURSE)

    adjusted_strokes = inputs.Scorecard(
        strokes_per_hole=TEST_PLAYER_HOLE_SCORES_WITH_MAX_STROKES_LIMIT
    )

    player_._note_below_par_holes(adjusted_strokes)
    notable_holes = player_._notable_holes

    assert notable_holes._birdie_holes == EXPECTED_NOTABLE_HOLES._birdie_holes
    assert notable_holes._eagle_holes == EXPECTED_NOTABLE_HOLES._eagle_holes
    assert notable_holes._albatross_holes == EXPECTED_NOTABLE_HOLES._albatross_holes


def test_player_individual_result_with_no_holes_scores_returns_incomplete_player_event() -> None:
    player_input = inputs.EventPlayerInput(
        handicap_index=0.0,
        scorecard=inputs.IncompleteScorecard(),
    )

    player_ = player.EventPlayer(input=player_input, course_=TEST_COURSE)
    assert player_.individual_result() == results.IncompletePlayerEventInividualResult()


def test_player_individual_result() -> None:
    player_ = player.EventPlayer(input=TEST_PLAYER_INPUT, course_=TEST_COURSE)

    out_strokes = sum(
        strokes
        for hole_num, strokes in TEST_PLAYER_HOLE_SCORES_WITH_MAX_STROKES_LIMIT.items()
        if hole_num in range(0, 10)
    )
    in_strokes = sum(
        strokes
        for hole_num, strokes in TEST_PLAYER_HOLE_SCORES_WITH_MAX_STROKES_LIMIT.items()
        if hole_num in range(10, 19)
    )
    gross_strokes = out_strokes + in_strokes
    net_strokes = gross_strokes - TEST_COURSE_HANDICAP

    expected_result = results.PlayerEventIndividualResult(
        course_handicap=TEST_COURSE_HANDICAP,
        front_9_gross=out_strokes,
        back_9_gross=in_strokes,
        total_gross=gross_strokes,
        total_net=net_strokes,
        notable_holes=EXPECTED_NOTABLE_HOLES,
    )

    assert player_.individual_result() == expected_result
