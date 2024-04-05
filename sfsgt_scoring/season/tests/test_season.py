from .. import season
from ..event import event


TEST_SEASON_INPUT = season.SeasonInput(
    events={
        "Standard Event": event.EventInput(
            course=event.CourseData(
                name="course_a",
                tee=event.CourseTeeData(
                    name="white",
                    rating=72.2,
                    slope=130,
                ),
                hole_pars=event.CourseHolePars({
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
                }),
            ),
            type=event.EventType.STANDARD,
            players={
                "Stanton Turner": event.EventPlayerInput(
                    handicap_index=12.0,
                    hole_scores={
                        '1': 5, '2': 4, '3': 5, '4': 6, '5': 5, '6': 6, '7': 4, '8': 4, '9': 5, '10': 6, '11': 6, '12': 5, '13': 4, '14': 4, '15': 4, '16': 4, '17': 4, '18': 5
                    },
                ),
                "John Fratello": event.EventPlayerInput(
                    handicap_index=16.4,
                    hole_scores={
                        '1': 5, '2': 7, '3': 6, '4': 3, '5': 5, '6': 6, '7': 3, '8': 5, '9': 6, '10': 7, '11': 6, '12': 4, '13': 3, '14': 5, '15': 3, '16': 4, '17': 5, '18': 6
                    },
                ),
            }
        ),
        "Major Event": event.EventInput(
            course=event.CourseData(
                name="course_b",
                tee=event.CourseTeeData(
                    name="blue",
                    rating=72.8,
                    slope=138,
                ),
                hole_pars=event.CourseHolePars({
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
                }),
            ),
            type=event.EventType.MAJOR,
            players={
                "Stanton Turner": event.EventPlayerInput(
                    handicap_index=12.0,
                    hole_scores={
                        '1': 5, '2': 4, '3': 5, '4': 6, '5': 5, '6': 6, '7': 4, '8': 4, '9': 5, '10': 6, '11': 6, '12': 5, '13': 4, '14': 4, '15': 4, '16': 4, '17': 4, '18': 5
                    },
                ),
                "John Fratello": event.EventPlayerInput(
                    handicap_index=16.4,
                    hole_scores={
                        '1': 5, '2': 7, '3': 6, '4': 3, '5': 5, '6': 6, '7': 3, '8': 5, '9': 6, '10': 7, '11': 6, '12': 4, '13': 3, '14': 5, '15': 3, '16': 4, '17': 5, '18': 6
                    },
                ),
            }
        )
    }
)


def test_season_construct() -> None:
    season_ = season.Season(TEST_SEASON_INPUT)
    assert season_._input == TEST_SEASON_INPUT
