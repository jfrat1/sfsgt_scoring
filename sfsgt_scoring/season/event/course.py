from . import inputs


class CourseHoleRequestError(Exception):
    """Exception to be raised when an invalid hole request is made."""


class Course:
    def __init__(self, input: inputs.CourseInput) -> None:
        self._slope = input.tee.slope
        self._rating = input.tee.rating
        self._hole_pars = input.hole_pars
        self._strokes_for_par = input.hole_pars.total_par()

    def player_course_handicap(self, player_handicap_index: float) -> int:
        course_handicap_raw = player_handicap_index * (self._slope / 113) + (
            self._rating - self._strokes_for_par
        )
        course_handicap = round(course_handicap_raw, 0)

        return int(course_handicap)

    def scoring_differential(self, player_18_hole_strokes: int) -> float:
        """Handicap score differential based on 18 hole strokes and tees."""
        return round((113 / self._slope) * (player_18_hole_strokes - self._rating), 1)

    def hole_par(self, hole_num: int) -> int:
        if hole_num not in range(1, 19):
            raise CourseHoleRequestError(
                f"Hole number must be in the range [1, 18]. Got: {hole_num}"
            )

        return self._hole_pars[hole_num]
