from dataclasses import dataclass

from ..src import handicap

def test_scoring_differential():
    @dataclass
    class TestCase():
        adjusted_gross_score: int
        course_rating: float
        course_slope: int
        scoring_diff: float

    test_cases= [
        TestCase(
            adjusted_gross_score=90,
            course_rating=70,
            course_slope=130,
            scoring_diff=17.4,
        ),
        TestCase(
            adjusted_gross_score=86,
            course_rating=68.7,
            course_slope=124,
            scoring_diff=15.8,
        ),
        TestCase(
            adjusted_gross_score=89,
            course_rating=71.5,
            course_slope=138,
            scoring_diff=14.3,
        ),
    ]
    
    for test_case in test_cases:
        score_diff = handicap.scoring_differential(
            adjusted_gross_score=test_case.adjusted_gross_score,
            course_rating=test_case.course_rating,
            course_slope=test_case.course_slope,
        )

        assert isinstance(score_diff, float)
        assert score_diff == test_case.scoring_diff

def test_course_handicap():
    @dataclass
    class TestCase():
        handicap_index: float
        course_rating: float
        course_slope: int
        course_par: int
        course_handicap: int

    test_cases = [
        TestCase(
            handicap_index=15.2,
            course_rating=69.7,
            course_slope=128,
            course_par=72,
            course_handicap=15,
        ),
        TestCase(
            handicap_index=21.2,
            course_rating=71.2,
            course_slope=124,
            course_par=72,
            course_handicap=22,
        ),
        TestCase(
            handicap_index=8.4,
            course_rating=71.1,
            course_slope=135,
            course_par=70,
            course_handicap=11,
        ),
    ]

    for test_case in test_cases:
        course_handicap = handicap.course_handicap(
            handicap_index=test_case.handicap_index,
            course_rating=test_case.course_rating,
            course_slope=test_case.course_slope,
            course_par=test_case.course_par,
        )

        assert isinstance(course_handicap, int)
        assert course_handicap == test_case.course_handicap