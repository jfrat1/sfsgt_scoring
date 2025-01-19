from typing import NamedTuple


class HandicapAllowanceOutOfRangeError(Exception):
    """Exception to be raised when a handicap allowance is not in the range 0 to 1."""


class HandicapCalculator(NamedTuple):
    course_rating: float
    course_slope: int
    course_par: int

    def course_handicap(self, player_handicap_index: float) -> int:
        course_handicap_unrounded = self._course_handicap_unrounded(player_handicap_index)
        return round(course_handicap_unrounded)

    def _course_handicap_unrounded(self, player_handicap_index: float) -> float:
        return player_handicap_index * (self.course_slope / 113) + (self.course_rating - self.course_par)

    def playing_handicap(self, player_handicap_index: float, handicap_allowance: float) -> int:
        playing_handicap_unrounded = self._course_handicap_unrounded(player_handicap_index) * handicap_allowance
        return round(playing_handicap_unrounded)

    def two_person_scramble_playing_handicap(
        self,
        player_handicap_indices: tuple[float, float],
        lower_handicap_allowance: float,
        higher_handicap_allowance: float,
    ) -> int:
        self._check_handicap_allowance(lower_handicap_allowance)
        self._check_handicap_allowance(higher_handicap_allowance)

        lower_handicap_index = min(player_handicap_indices)
        higher_handicap_index = max(player_handicap_indices)

        lower_playing_handicap = self.playing_handicap(
            player_handicap_index=lower_handicap_index,
            handicap_allowance=lower_handicap_allowance,
        )
        higher_playing_handicap = self.playing_handicap(
            player_handicap_index=higher_handicap_index,
            handicap_allowance=higher_handicap_allowance,
        )
        return lower_playing_handicap + higher_playing_handicap

    def _check_handicap_allowance(self, handicap_allowance: float) -> None:
        if handicap_allowance < 0.0 or handicap_allowance > 1.0:
            raise HandicapAllowanceOutOfRangeError(
                f"Handicap allowance must be in the range 0.0 to 1.0. Got {handicap_allowance}."
            )
