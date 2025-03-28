from tests.testing_utils.score_generator import (
    ScoreGeneratorCourse,
    SmartHoleScoreGenerator,
    SmartHoleScoreGeneratorConfig,
)


def test_smart_score_generator() -> None:
    config = SmartHoleScoreGeneratorConfig(
        playing_handicap=0,
        net_score_over_par=0,
    )
    generator = SmartHoleScoreGenerator(
        course=ScoreGeneratorCourse.BAYLANDS,
        config=config,
    )

    scores = generator.generate()

    assert sum(scores.values()) == 72


def test_smart_score_generator_bogie_golfer_net_even() -> None:
    config = SmartHoleScoreGeneratorConfig(
        playing_handicap=18,
        net_score_over_par=0,
    )
    generator = SmartHoleScoreGenerator(
        course=ScoreGeneratorCourse.BAYLANDS,
        config=config,
    )

    scores = generator.generate()

    assert sum(scores.values()) == 90


def test_smart_score_generator_12_hcp_net_4_over() -> None:
    config = SmartHoleScoreGeneratorConfig(
        playing_handicap=12,
        net_score_over_par=4,
    )
    generator = SmartHoleScoreGenerator(
        course=ScoreGeneratorCourse.BAYLANDS,
        config=config,
    )

    scores = generator.generate()

    assert sum(scores.values()) == 88


def test_smart_score_generator_bogie_golfer_with_under_par_holes() -> None:
    config = SmartHoleScoreGeneratorConfig(
        playing_handicap=18,
        net_score_over_par=0,
        birdie_holes=[2],
        eagle_holes=[9],
        albatross_holes=[13],
    )
    generator = SmartHoleScoreGenerator(
        course=ScoreGeneratorCourse.BAYLANDS,
        config=config,
    )

    scores = generator.generate()

    # Use a helper function from the generator to get a course object for assertions
    course = generator.get_course(ScoreGeneratorCourse.BAYLANDS)
    assert sum(scores.values()) == 90
    assert scores[2] == course.hole_par(2) - 1
    assert scores[9] == course.hole_par(9) - 2
    assert scores[13] == course.hole_par(13) - 3


def test_smart_score_generator_bogie_golfer_with_over_max_holes() -> None:
    config = SmartHoleScoreGeneratorConfig(
        playing_handicap=18,
        net_score_over_par=0,
        over_max_holes=[2],
    )
    generator = SmartHoleScoreGenerator(
        course=ScoreGeneratorCourse.BAYLANDS,
        config=config,
    )

    scores = generator.generate()

    # Use a helper function from the generator to get a course object for assertions
    course = generator.get_course(ScoreGeneratorCourse.BAYLANDS)
    assert sum(scores.values()) == 90
    # An over max score is double-par plus 3
    assert scores[2] == course.hole_par(2) * 2 + 3
