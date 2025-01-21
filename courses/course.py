import pathlib

import pydantic
import pydantic_yaml


class CourseError(Exception):
    """Exception to be raised when a course file cannot be loaded."""


def load_course_file(file_path: pathlib.Path) -> "Course":
    try:
        return pydantic_yaml.parse_yaml_file_as(Course, file_path)

    except ValueError as exc:
        raise CourseError(f"Unable to load course file at {file_path}.") from exc


class Course(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True, extra="forbid", strict=True)

    name: str
    hole_pars: dict[int, int]
    tees: dict[str, "TeeInfo"]

    @property
    def par(self) -> int:
        return sum(self.hole_pars.values())

    def hole_par(self, hole_num: int) -> int:
        try:
            return self.hole_pars[hole_num]
        except KeyError:
            raise CourseError(f"Hole number {hole_num} does not exist for course {self.name}")

    def get_tee_info(self, tee_name: str) -> "TeeInfo":
        try:
            return self.tees[tee_name]
        except KeyError as exc:
            available_tees = list(self.tees.keys())
            raise KeyError(
                f"Tee named '{tee_name}' not found for course: {self.name}. Available " f"tees: {available_tees}"
            ) from exc

    def course_handicap(self, tee: str, player_hcp_index: float) -> int:
        course_hcp_raw = self._course_handicap_unrounded(tee=tee, player_hcp_index=player_hcp_index)
        return int(round(course_hcp_raw, 0))

    def _course_handicap_unrounded(self, tee: str, player_hcp_index: float) -> float:
        tee_info = self.get_tee_info(tee_name=tee)
        return player_hcp_index * (tee_info.slope / 113) + (tee_info.rating - self.par)

    def playing_handicap(self, tee: str, player_hcp_index: float, handicap_allowance: float) -> int:
        if 0.0 > handicap_allowance > 1.0:
            raise CourseError("Handicap allowances must be a float value between 0.0 and 1.0")

        course_hcp_raw = self._course_handicap_unrounded(tee=tee, player_hcp_index=player_hcp_index)
        return int(round(course_hcp_raw * handicap_allowance, 0))

    def scoring_differential(self, tee: str, gross_strokes: int) -> float:
        """Handicap score differential based on 18 hole strokes and tees."""
        tee_info = self.get_tee_info(tee_name=tee)
        return round((113 / tee_info.slope) * (gross_strokes - tee_info.rating), 1)

    @pydantic.field_validator("hole_pars")
    @classmethod
    def check_hole_pars(cls, hole_pars: dict[int, int]) -> dict[int, int]:
        hole_numbers = list(hole_pars.keys())
        expected_hole_numbers = list(range(1, 19))
        if hole_numbers != expected_hole_numbers:
            raise ValueError("Keys in hole_pars dict must be hole numbers 1 through 18.")

        for hole, par in hole_pars.items():
            if par not in (3, 4, 5):
                raise ValueError(f"Par values must be one of 3, 4, or 5. Found {par} for hole {hole}")

        return hole_pars


MIN_COURSE_RATING = 60.0
MAX_COURSE_RATING = 80.0
MIN_COURSE_SLOPE = 55
MAX_COURSE_SLOPE = 155


class TeeInfo(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True, extra="forbid", strict=True)

    rating: float = pydantic.Field(ge=MIN_COURSE_RATING, le=MAX_COURSE_RATING)
    slope: int = pydantic.Field(ge=MIN_COURSE_SLOPE, le=MAX_COURSE_SLOPE)
