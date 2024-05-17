from . import inputs


class CourseHoleRequestError(Exception):
    """Exception to be raised when an invalid hole request is made."""


class Course():
    def __init__(self, input: inputs.CourseInput) -> None:
        self._input = input

    def player_course_handicap(self, player_handicap_index: float) -> int:
        slope = self._input.tee.slope
        rating = self._input.tee.rating
        par = self._input.hole_pars.total_par()

        course_handicap_raw = player_handicap_index * (slope / 113) + (rating - par)
        course_handicap = round(course_handicap_raw, 0)

        return int(course_handicap)

    def hole_par(self, hole_num: int) -> int:
        if hole_num not in range(1, 19):
            raise CourseHoleRequestError(
                f"Hole number must be in the range [1, 18]. Got: {hole_num}"
            )

        return self._input.hole_pars[hole_num]
