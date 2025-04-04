import abc
from typing import Any

from utils import class_utils


class ScorecardError(Exception):
    pass


class Scorecard(abc.ABC):
    @abc.abstractmethod
    def is_complete_score(self) -> bool:
        pass

    @abc.abstractmethod
    def scores(self) -> dict[int, int]:
        pass

    @abc.abstractmethod
    def hole_strokes(self, hole_num: int) -> int:
        pass


class IncompleteScorecardCallError(Exception):
    """Exception to be raised when a disallowed call is made to an IncompleteScorecard."""


class IncompleteScorecard(Scorecard, class_utils.Singleton):
    def __init__(self):
        pass

    def is_complete_score(self):
        return False

    def scores(self) -> dict[int, int]:
        raise IncompleteScorecardCallError("Scores cannot be retrieved from incomplete scorecards.")

    def hole_strokes(self, hole_num: int):
        raise IncompleteScorecardCallError("Scores cannot be retrieved from incomplete scorecards.")


class CompleteScorecard(Scorecard):
    def __init__(self, scores: dict[int, int]):
        ScorecardValidator(scores).validate()
        self._scores = scores

    def is_complete_score(self):
        return True

    def scores(self) -> dict[int, int]:
        return self._scores

    def hole_strokes(self, hole_num):
        try:
            return self._scores[hole_num]
        except KeyError:
            raise ScorecardError(f"Hole number {hole_num} does not exist in scorecard.")

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, CompleteScorecard):
            return NotImplemented

        return self._scores == other._scores


class ScorecardValidationError(Exception):
    """Exception to be raised when hole scores do not pass validation."""


class ScorecardValidator:
    def __init__(self, hole_scores: dict[int, int]) -> None:
        self.hole_scores = hole_scores

    def validate(self) -> None:
        self._validate_keys()
        self._validate_values()

    def _validate_keys(self) -> None:
        expected_keys = [hole for hole in range(1, 19)]
        actual_keys = list(self.hole_scores.keys())
        if expected_keys != actual_keys:
            raise ScorecardValidationError(
                "Keys in the HoleScores dictionary must be integers containing hole numbers 1 "
                f"through 18. \nExpected: {expected_keys} \nFound: {actual_keys}"
            )

    def _validate_values(self) -> None:
        values = self.hole_scores.values()
        are_all_values_positive_ints = all(isinstance(value, int) and value >= 1 for value in values)

        if not are_all_values_positive_ints:
            raise ScorecardValidationError(
                f"Values in the HoleScores dictionary must be positive integers. Found: {values}"
            )


def scorecard_factory(hole_scores: dict[int, int]) -> Scorecard:
    try:
        ScorecardValidator(hole_scores).validate()
        return CompleteScorecard(hole_scores)

    except ScorecardValidationError:
        return IncompleteScorecard()
