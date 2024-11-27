import pathlib

import pydantic
import pydantic_yaml


class CourseLoadError(Exception):
    """Exception to be raised when a course file cannot be loaded."""


def load_course_file(file_path: pathlib.Path) -> "Course":
    try:
        return pydantic_yaml.parse_yaml_file_as(Course, file_path)

    except ValueError as exc:
        raise CourseLoadError(f"Unable to load course file at {file_path}.") from exc


class Course(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True, extra="forbid", strict=True)

    name: str
    hole_pars: dict[int, int]
    tees: dict[str, "TeeInfo"]

    @property
    def par(self) -> int:
        return sum(self.hole_pars.values())

    def get_tee_info(self, tee_name: str) -> "TeeInfo":
        try:
            return self.tees[tee_name]
        except KeyError as exc:
            available_tees = list(self.tees.keys())
            raise KeyError(
                f"Tee named '{tee_name}' not found for course: {self.name}. Available "
                f"tees: {available_tees}"
            ) from exc

    @pydantic.field_validator("hole_pars")
    @classmethod
    def check_hole_pars(cls, hole_pars: dict[int, int]) -> dict[int, int]:
        hole_numbers = list(hole_pars.keys())
        expected_hole_numbers = list(range(1, 19))
        if hole_numbers != expected_hole_numbers:
            raise ValueError("Keys in hole_pars dict must be hole numbers 1 through 18.")

        for hole, par in hole_pars.items():
            if par not in (3, 4, 5):
                raise ValueError(
                    f"Par values must be one of 3, 4, or 5. Found {par} for hole {hole}"
                )

        return hole_pars


class TeeInfo(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True, extra="forbid", strict=True)

    rating: float
    slope: int
    distance: int
