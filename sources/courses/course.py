import pathlib

import pydantic
import pydantic_yaml
from season_common import player


class CourseError(Exception):
    """Exception to be raised when a course file cannot be loaded."""


MIN_COURSE_RATING = 60.0
MAX_COURSE_RATING = 80.0
MIN_COURSE_SLOPE = 55
MAX_COURSE_SLOPE = 155


class TeeInfo(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True, extra="forbid", strict=True)

    rating: float = pydantic.Field(ge=MIN_COURSE_RATING, le=MAX_COURSE_RATING)
    slope: int = pydantic.Field(ge=MIN_COURSE_SLOPE, le=MAX_COURSE_SLOPE)


class Course(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True, extra="forbid", strict=True)

    name: str
    # TODO: The hole pars and tees need to be gender-specific. It probably calls for an intermediate
    # class to hold the hole pars and tees by gender.
    hole_pars_: list[int] = pydantic.Field(alias="hole_pars")
    mens_tees_: dict[str, TeeInfo] = pydantic.Field(alias="mens_tees")
    womens_tees_: dict[str, TeeInfo] = pydantic.Field(alias="womens_tees")

    @property
    def par(self) -> int:
        return sum(self.hole_pars_)

    @property
    def hole_pars(self) -> dict[int, int]:
        return {idx + 1: par for idx, par in enumerate(self.hole_pars_)}

    def tees(self, player_gender: player.PlayerGender) -> dict[str, TeeInfo]:
        match player_gender:
            case player.PlayerGender.FEMALE:
                return self.womens_tees_
            case player.PlayerGender.MALE:
                return self.mens_tees_
            case _:
                raise CourseError(f"Tees are not defined for player gender: {player_gender}.")

    def hole_par(self, hole_num: int) -> int:
        try:
            hole_idx = hole_num - 1
            return self.hole_pars_[hole_idx]
        except KeyError:
            raise CourseError(f"Hole number {hole_num} does not exist for course {self.name}")

    def get_tee_info(self, tee_name: str, player_gender: player.PlayerGender = player.PlayerGender.MALE) -> TeeInfo:
        try:
            return self.tees(player_gender=player_gender)[tee_name]
        except KeyError as exc:
            available_tees = list(self.tees(player_gender=player_gender).keys())
            raise KeyError(
                f"Tee named '{tee_name}' not found for course: {self.name}. Available tees: {available_tees}"
            ) from exc

    def course_handicap(self, tee: str, player_hcp_index: float, player_gender: player.PlayerGender) -> int:
        course_hcp_raw = self._course_handicap_unrounded(
            tee=tee, player_hcp_index=player_hcp_index, player_gender=player_gender
        )
        return int(round(course_hcp_raw, 0))

    def _course_handicap_unrounded(
        self,
        tee: str,
        player_hcp_index: float,
        player_gender: player.PlayerGender,
    ) -> float:
        tee_info = self.get_tee_info(tee_name=tee, player_gender=player_gender)
        return player_hcp_index * (tee_info.slope / 113) + (tee_info.rating - self.par)

    def playing_handicap(
        self,
        tee: str,
        player_hcp_index: float,
        player_gender: player.PlayerGender,
        handicap_allowance: float,
    ) -> int:
        if 0.0 > handicap_allowance > 1.0:
            raise CourseError("Handicap allowances must be a float value between 0.0 and 1.0")

        course_hcp_raw = self._course_handicap_unrounded(
            tee=tee, player_hcp_index=player_hcp_index, player_gender=player_gender
        )
        return int(round(course_hcp_raw * handicap_allowance, 0))

    def scoring_differential(self, tee: str, gross_strokes: int, player_gender: player.PlayerGender) -> float:
        """Handicap score differential based on 18 hole strokes and tees."""
        tee_info = self.get_tee_info(tee_name=tee, player_gender=player_gender)
        return round((113 / tee_info.slope) * (gross_strokes - tee_info.rating), 1)

    @pydantic.field_validator("hole_pars_")
    @classmethod
    def check_hole_pars_(cls, hole_pars: list[int]) -> list[int]:
        if num_holes := len(hole_pars) != 18:
            raise ValueError(f"There must be exactly 18 hole pars defined in a course. Found {num_holes}.")

        for idx, par in enumerate(hole_pars):
            if par not in (3, 4, 5):
                raise ValueError(f"Par values must be one of 3, 4, or 5. Found {par} for hole {idx + 1}")

        return hole_pars


def load_course_file(file_path: pathlib.Path) -> Course:
    try:
        return pydantic_yaml.parse_yaml_file_as(Course, file_path)

    except ValueError as exc:
        raise CourseError(f"Unable to load course file at {file_path}.") from exc
