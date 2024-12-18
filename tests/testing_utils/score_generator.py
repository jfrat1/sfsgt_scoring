import enum
from typing import NamedTuple

import courses


class ScoreGeneratorCourse(enum.Enum):
    BAYLANDS = "baylands"
    HARDING_PARK = "harding_park"
    PRESIDIO = "presidio"


class ScoreGeneratorStrategy(enum.Enum):
    EVEN_PAR = enum.auto()
    BOGIE_GOLF = enum.auto()


class HoleScoreGenerator(NamedTuple):
    course: ScoreGeneratorCourse
    strategy: ScoreGeneratorStrategy

    def generate(self) -> dict[int, int]:
        course = courses.build_default_concrete_course_provider().get_course(self.course.value)

        match self.strategy:
            case ScoreGeneratorStrategy.EVEN_PAR:
                return course.hole_pars
            case ScoreGeneratorStrategy.BOGIE_GOLF:
                return {hole_num: hole_par + 1 for hole_num, hole_par in course.hole_pars.items()}
            case _:
                return {}
