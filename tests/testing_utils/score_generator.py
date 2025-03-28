import abc
import enum
import math

import courses


class ScoreGeneratorCourse(enum.Enum):
    BAYLANDS = "baylands"
    HARDING_PARK = "harding_park"
    PRESIDIO = "presidio"


class SimpleHoleScoreGeneratorStrategy(enum.Enum):
    EVEN_PAR = enum.auto()
    BOGIE_GOLF = enum.auto()


class HoleScoreGenerator(abc.ABC):
    @abc.abstractmethod
    def generate(self) -> dict[int, int]:
        pass

    def get_course(self, course: ScoreGeneratorCourse) -> courses.Course:
        """Get a Course object for a ScoreGeneratorCourse."""
        return courses.build_default_concrete_course_provider().get_course(course.value)


class SimpleHoleScoreGenerator(HoleScoreGenerator):
    def __init__(
        self,
        course: ScoreGeneratorCourse,
        strategy: SimpleHoleScoreGeneratorStrategy,
    ) -> None:
        self.course = course
        self.strategy = strategy

    def generate(self) -> dict[int, int]:
        course = self.get_course(self.course)

        match self.strategy:
            case SimpleHoleScoreGeneratorStrategy.EVEN_PAR:
                return course.hole_pars
            case SimpleHoleScoreGeneratorStrategy.BOGIE_GOLF:
                return {hole_num: hole_par + 1 for hole_num, hole_par in course.hole_pars.items()}
            case _:
                return {}


class MaxScoreType(enum.Enum):
    DOUBLE_PAR_PLUS_TWO = enum.auto()


class SmartHoleScoreGeneratorConfig:
    def __init__(
        self,
        playing_handicap: int,
        net_score_over_par: int,
        max_score_type: MaxScoreType = MaxScoreType.DOUBLE_PAR_PLUS_TWO,
        birdie_holes: list[int] = [],
        eagle_holes: list[int] = [],
        albatross_holes: list[int] = [],
        over_max_holes: list[int] = [],
    ) -> None:
        self.playing_handicap = playing_handicap
        self.net_score_to_par = net_score_over_par
        self.max_score_type = max_score_type
        self.birdie_holes = birdie_holes
        self.eagle_holes = eagle_holes
        self.albatross_holes = albatross_holes
        self.over_max_holes = over_max_holes

        self._verify_hole_config(holes=self.birdie_holes, config_name="birdie_holes")
        self._verify_hole_config(holes=self.eagle_holes, config_name="eagle_holes")
        self._verify_hole_config(holes=self.albatross_holes, config_name="albatross_holes")
        self._verify_hole_config(holes=self.over_max_holes, config_name="over_max_holes")
        self._verify_hole_configs_are_unique()

    def _verify_hole_config(self, holes: list[int], config_name: str) -> None:
        for hole in holes:
            if hole < 1 or hole > 18:
                raise ValueError(f"{config_name} config is invalid. Holes must be between 1 and 18, got {hole}.")

    def _verify_hole_configs_are_unique(self) -> None:
        seen = set()
        duplicates = set()

        all_holes = self.birdie_holes + self.eagle_holes + self.albatross_holes + self.over_max_holes
        for hole in all_holes:
            if hole not in seen:
                seen.add(hole)
            else:
                duplicates.add(hole)

        if not len(duplicates) == 0:
            raise ValueError(f"Duplicate hole configs found. Holes {duplicates} exist in more than 1 config.")


class SmartHoleScoreGenerator(HoleScoreGenerator):
    def __init__(
        self,
        course: ScoreGeneratorCourse,
        config: SmartHoleScoreGeneratorConfig,
    ) -> None:
        self.course = course
        self.config = config

    def generate(self) -> dict[int, int]:
        course = self.get_course(self.course)

        core = SmartHoleScoreGeneratorCore(course, self.config)
        return core.generate()


class SmartHoleScoreGeneratorError(Exception):
    pass


class SmartHoleScoreGeneratorCore:
    def __init__(self, course: courses.Course, verified_config: SmartHoleScoreGeneratorConfig) -> None:
        self.course = course
        self.config = verified_config

        self.defined_scores: dict[int, int] = {}
        self.has_generate_run = False

    def generate(self) -> dict[int, int]:
        if self.has_generate_run:
            self_name = self.__class__.__name__
            raise SmartHoleScoreGeneratorError(f"{self_name} generation can only be performed once.")

        self.has_generate_run = True

        self._set_predefined_holes()
        remaining_score_over_par = self._strokes_over_par_remaining()
        remaining_holes = self._num_holes_remaining()

        base_score_to_par_all_holes = math.floor(remaining_score_over_par / remaining_holes)
        num_holes_needing_additional_stroke = remaining_score_over_par % remaining_holes

        # TODO: Figure out how to make this blow up if an unsolvable config is provided
        num_holes_given_additional_stroke = 0
        for hole in range(1, 19):
            if hole not in self.defined_scores:
                score_to_par = 0
                if num_holes_given_additional_stroke < num_holes_needing_additional_stroke:
                    score_to_par = base_score_to_par_all_holes + 1
                    num_holes_given_additional_stroke += 1
                else:
                    score_to_par = base_score_to_par_all_holes

                self.defined_scores[hole] = self.course.hole_par(hole) + score_to_par

        undefined_holes = set(range(1, 19)).difference(set(self.defined_scores.keys()))
        if not len(undefined_holes) == 0:
            raise SmartHoleScoreGeneratorError(
                f"An unknown error occured. Some holes were not distributed: {undefined_holes}"
            )

        return self.defined_scores

    def _set_predefined_holes(self) -> None:
        for hole in self.config.birdie_holes:
            self.defined_scores[hole] = self._hole_score(hole=hole, score_to_par=-1)

        for hole in self.config.eagle_holes:
            self.defined_scores[hole] = self._hole_score(hole=hole, score_to_par=-2)

        for hole in self.config.albatross_holes:
            self.defined_scores[hole] = self._hole_score(hole=hole, score_to_par=-3)

        for hole in self.config.over_max_holes:
            self.defined_scores[hole] = self._over_max_hole_score(hole=hole)

    def _hole_score(self, hole: int, score_to_par: int) -> int:
        hole_par = self.course.hole_par(hole)
        return hole_par + score_to_par

    def _over_max_hole_score(self, hole: int) -> int:
        hole_par = self.course.hole_par(hole)
        match self.config.max_score_type:
            case MaxScoreType.DOUBLE_PAR_PLUS_TWO:
                # Add 3 so that score is over max
                return hole_par * 2 + 3
            case _:
                raise NotImplementedError(f"Max score type {self.config.max_score_type} is not fully implemented.")

    def _strokes_over_par_remaining(self) -> int:
        defined_score_to_par = 0
        for hole, score in self.defined_scores.items():
            hole_score_to_par = score - self.course.hole_par(hole)
            defined_score_to_par += hole_score_to_par

        target_score_to_par = self.config.playing_handicap + self.config.net_score_to_par
        return target_score_to_par - defined_score_to_par

    def _num_holes_remaining(self) -> int:
        num_holes_defined = len(self.defined_scores)
        return 18 - num_holes_defined
