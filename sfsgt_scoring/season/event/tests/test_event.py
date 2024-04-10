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
    }
)

STANTON_NOTABLE_HOLES = results.NotableHoles()
STANTON_NOTABLE_HOLES.set_hole(14, results.NotableHoleType.BIRDIE)
STANTON_NOTABLE_HOLES.set_hole(17, results.NotableHoleType.BIRDIE)

JOHN_NOTABLE_HOLES = results.NotableHoles()
JOHN_NOTABLE_HOLES.set_hole(4, results.NotableHoleType.BIRDIE)
JOHN_NOTABLE_HOLES.set_hole(13, results.NotableHoleType.BIRDIE)
JOHN_NOTABLE_HOLES.set_hole(15, results.NotableHoleType.BIRDIE)

TEST_PLAYER_INDIVIDUAL_RESULTS = {
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
}


def test_event_construct() -> None:
    event.Event(input=TEST_EVENT_INPUT)


def test_event_player_individual_results() -> None:
    event_ = event.Event(input=TEST_EVENT_INPUT)
    result_ = event_._player_individual_results()
    assert result_ == TEST_PLAYER_INDIVIDUAL_RESULTS



