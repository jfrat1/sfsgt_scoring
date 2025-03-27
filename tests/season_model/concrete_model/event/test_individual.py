from courses.course import Course, TeeInfo
from season_common.player import Player, PlayerGender
from season_common.scorecard import CompleteScorecard, IncompleteScorecard
from season_model.api.input import SeasonModelEventPlayerInput
from season_model.api.result import (
    SeasonModelCompleteEventPlayerIndividualResult,
    SeasonModelIncompleteEventPlayerInividualResult,
)
from season_model.api.result.notable_holes import NotableHoles, NotableHoleType
from season_model.concrete_model.event.individual import (
    PlayerIndividualResultGenerator,
)

STUB_PLAYER_HOLE_SCORES = {
    1: 5,
    2: 2,
    3: 6,
    4: 3,
    5: 5,
    6: 6,
    7: 3,
    8: 5,
    9: 3,
    10: 4,
    11: 6,
    12: 11,
    13: 3,
    14: 5,
    15: 3,
    16: 4,
    17: 5,
    18: 6,
}
STUB_COURSE_HOLE_PARS = [
    4,
    5,
    4,
    3,
    4,
    4,
    3,
    4,
    5,
    5,
    4,
    4,
    3,
    4,
    3,
    4,
    4,
    5,
]
STUB_PLAYER_HOLE_SCORES_WITH_MAX_STROKES_LIMIT = {
    1: 5,
    2: 2,
    3: 6,
    4: 3,
    5: 5,
    6: 6,
    7: 3,
    8: 5,
    9: 3,
    10: 4,
    11: 6,
    12: 10,
    13: 3,
    14: 5,
    15: 3,
    16: 4,
    17: 5,
    18: 6,
}

# This data is sensitive to changes in either the player hole scores or course hole pars
EXPECTED_NOTABLE_HOLES = NotableHoles()
EXPECTED_NOTABLE_HOLES.set_hole(2, NotableHoleType.ALBATROSS)
EXPECTED_NOTABLE_HOLES.set_hole(9, NotableHoleType.EAGLE)
EXPECTED_NOTABLE_HOLES.set_hole(10, NotableHoleType.BIRDIE)
EXPECTED_NOTABLE_HOLES.set_hole(12, NotableHoleType.OVER_MAX)

STUB_PLAYER = Player(
    name="Jane Doe",
    gender=PlayerGender.FEMALE,
)
STUB_PLAYER_INPUT = SeasonModelEventPlayerInput(
    handicap_index=16.0,
    scorecard=CompleteScorecard(scores=STUB_PLAYER_HOLE_SCORES),
    player=STUB_PLAYER,
)

STUB_COURSE_TEE = "white"
STUB_COURSE = Course(
    name="Presidio",
    mens_tees={},
    womens_tees={
        STUB_COURSE_TEE: TeeInfo(
            rating=69.5,
            slope=129,
        ),
    },
    hole_pars=STUB_COURSE_HOLE_PARS,
)

STUB_COURSE_HANDICAP = 16


def test_result_generator_class_constants() -> None:
    assert PlayerIndividualResultGenerator._FRONT_9_HOLES == (1, 2, 3, 4, 5, 6, 7, 8, 9)
    assert PlayerIndividualResultGenerator._BACK_9_HOLES == (10, 11, 12, 13, 14, 15, 16, 17, 18)
    assert PlayerIndividualResultGenerator._ALL_HOLES == (
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
    )


def test_result_generator_adjust_strokes_for_hole_max() -> None:
    generator = PlayerIndividualResultGenerator(input=STUB_PLAYER_INPUT, course=STUB_COURSE, tee=STUB_COURSE_TEE)

    assert generator._adjust_scorecard_for_max_hole_strokes() == CompleteScorecard(
        scores=STUB_PLAYER_HOLE_SCORES_WITH_MAX_STROKES_LIMIT
    )
    assert generator._notable_holes.over_max_holes() == [12]


def test_result_generator_note_below_par_holes() -> None:
    generator = PlayerIndividualResultGenerator(input=STUB_PLAYER_INPUT, course=STUB_COURSE, tee=STUB_COURSE_TEE)

    adjusted_strokes = CompleteScorecard(scores=STUB_PLAYER_HOLE_SCORES_WITH_MAX_STROKES_LIMIT)

    generator._note_below_par_holes(adjusted_strokes)
    notable_holes = generator._notable_holes

    assert notable_holes.birdie_holes() == EXPECTED_NOTABLE_HOLES.birdie_holes()
    assert notable_holes.eagle_holes() == EXPECTED_NOTABLE_HOLES.eagle_holes()
    assert notable_holes.albatross_holes() == EXPECTED_NOTABLE_HOLES.albatross_holes()


def test_result_generator_individual_result_with_no_holes_scores_returns_incomplete_result() -> None:
    incomplete_input = SeasonModelEventPlayerInput(
        handicap_index=0.0,
        scorecard=IncompleteScorecard(),
        player=STUB_PLAYER,
    )
    generator = PlayerIndividualResultGenerator(input=incomplete_input, course=STUB_COURSE, tee=STUB_COURSE_TEE)

    assert generator.generate() is SeasonModelIncompleteEventPlayerInividualResult()


def test_result_generator_individual_result() -> None:
    generator = PlayerIndividualResultGenerator(input=STUB_PLAYER_INPUT, course=STUB_COURSE, tee=STUB_COURSE_TEE)

    out_strokes = sum(
        strokes
        for hole_num, strokes in STUB_PLAYER_HOLE_SCORES_WITH_MAX_STROKES_LIMIT.items()
        if hole_num in range(0, 10)
    )
    in_strokes = sum(
        strokes
        for hole_num, strokes in STUB_PLAYER_HOLE_SCORES_WITH_MAX_STROKES_LIMIT.items()
        if hole_num in range(10, 19)
    )
    gross_strokes = out_strokes + in_strokes
    net_strokes = gross_strokes - STUB_COURSE_HANDICAP

    expected_result = SeasonModelCompleteEventPlayerIndividualResult(
        course_handicap=STUB_COURSE_HANDICAP,
        front_9_gross=out_strokes,
        back_9_gross=in_strokes,
        total_gross=gross_strokes,
        total_net=net_strokes,
        notable_holes=EXPECTED_NOTABLE_HOLES,
        score_differential=12.7,
    )

    assert generator.generate() == expected_result
