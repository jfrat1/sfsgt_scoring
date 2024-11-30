import abc

from utils import class_utils


class HoleScores(abc.ABC):
    @abc.abstractmethod
    def is_complete_score(self) -> bool:
        pass

    @abc.abstractmethod
    def scores(self) -> dict[int, int]:
        pass


class IncompleteHoleScores(HoleScores, class_utils.Singleton):
    def __init__(self):
        pass

    def is_complete_score(self):
        return False

    def scores(self) -> dict[int, int]:
        return {}


class CompleteHoleScores(HoleScores):
    def __init__(self, scores: dict[int, int]):
        HoleScoresValidator(scores).validate()
        self._scores = scores

    def is_complete_score(self):
        return True

    def scores(self) -> dict[int, int]:
        return self._scores


class HoleScoresValidationError(Exception):
    pass


class HoleScoresValidator:
    def __init__(self, hole_scores: dict[int, int]) -> None:
        self.hole_scores = hole_scores

    def validate(self) -> None:
        self._validate_keys()
        self._validate_values()

    def _validate_keys(self) -> None:
        expected_keys = [hole for hole in range(1, 19)]
        actual_keys = list(self.hole_scores.keys())
        if expected_keys != actual_keys:
            raise HoleScoresValidationError(
                "Keys in the HoleScores dictionary must be integers containing hole numbers 1 "
                f"through 18. \nExpected: {expected_keys} \nFound: {actual_keys}"
            )

    def _validate_values(self) -> None:
        values = self.hole_scores.values()
        are_all_values_positive_ints = all(
            isinstance(value, int) and value >= 1
            for value in values
        )

        if not are_all_values_positive_ints:
            raise HoleScoresValidationError(
                f"Values in the HoleScores dictionary must be positive integers. Found: {values}"
            )


def hole_scores_factory(hole_scores: dict[int, int]) -> HoleScores:
    try:
        HoleScoresValidator(hole_scores).validate()
        return CompleteHoleScores(hole_scores)

    except HoleScoresValidationError:
        return IncompleteHoleScores()