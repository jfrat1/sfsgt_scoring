import enum
from typing import NamedTuple

import course_database


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
        course_db = course_database.load_default_database()
        course_data = course_db.get_course(self.course.value)

        match self.strategy:
            case ScoreGeneratorStrategy.EVEN_PAR:
                return course_data.hole_pars
            case ScoreGeneratorStrategy.BOGIE_GOLF:
                return {hole_num: hole_par + 1 for hole_num, hole_par in course_data.hole_pars.items()}
            case _:
                return {}
