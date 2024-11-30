import pytest

from season_view.interface import hole_scores


def test_incomplete_hole_scores_is_singleton() -> None:
    score_1 = hole_scores.IncompleteHoleScores()
    score_2 = hole_scores.IncompleteHoleScores()

    assert score_1 is score_2


def create_test_hole_scores_dict(
    hole_score_values: list[int | str | None]
) -> dict[int, int | str | None]:
    num_scores = len(hole_score_values)
    return {
        hole_num: hole_score
        for hole_num, hole_score in zip(range(1, num_scores + 1), hole_score_values)
    }


def test_hole_scores_validator_with_valid_scores() -> None:
    score_values = [5, 4, 5, 6, 5, 6, 4, 4, 5, 6, 6, 5, 4, 4, 4, 4, 4, 5]
    scores = create_test_hole_scores_dict(score_values)  # type: ignore
    hole_scores.HoleScoresValidator(scores).validate()  # type: ignore


def test_hole_scores_validator_missins_some_hole_scores_raises_error() -> None:
    score_values = [5, 4, 5, 6, 5, 6, 4, 4, None, 6, 6, 5, 4, 4, 4, 4, None, 5]
    scores = create_test_hole_scores_dict(score_values)  # type: ignore
    with pytest.raises(hole_scores.HoleScoresValidationError):
        hole_scores.HoleScoresValidator(scores).validate()  # type: ignore


def test_hole_scores_validator_missing_all_hole_scores_raises_error() -> None:
    score_values = [None] * 18
    scores = create_test_hole_scores_dict(score_values)  # type: ignore
    with pytest.raises(hole_scores.HoleScoresValidationError):
        hole_scores.HoleScoresValidator(scores).validate()  # type: ignore


def test_hole_scores_validator_too_few_scores_raises_error() -> None:
    score_values = [5, 4, 5, 6, 5, 6, 4, 4, 5]
    scores = create_test_hole_scores_dict(score_values)  # type: ignore
    with pytest.raises(hole_scores.HoleScoresValidationError):
        hole_scores.HoleScoresValidator(scores).validate()  # type: ignore


def test_hole_scores_validator_too_many_scores_raises_error() -> None:
    score_values = [5, 4, 5, 6, 5, 6, 4, 4, 5, 6, 6, 5, 4, 4, 4, 4, 4, 5, 4, 6]
    scores = create_test_hole_scores_dict(score_values)  # type: ignore
    with pytest.raises(hole_scores.HoleScoresValidationError):
        hole_scores.HoleScoresValidator(scores).validate()  # type: ignore


def test_hole_scores_validator_offset_hole_numbers_raises_error() -> None:
    score_values = [5, 4, 5, 6, 5, 6, 4, 4, 5, 6, 6, 5, 4, 4, 4, 4, 4, 5]
    scores = create_test_hole_scores_dict(score_values)  # type: ignore

    scores_with_offset_hole_num = {
        hole_num + 1: hole_score for hole_num, hole_score in scores.items()
    }
    with pytest.raises(hole_scores.HoleScoresValidationError):
        hole_scores.HoleScoresValidator(scores_with_offset_hole_num).validate()  # type: ignore


def test_hole_scores_validator_string_hole_numbers_raises_error() -> None:
    score_values = [5, 4, 5, 6, 5, 6, 4, 4, 5, 6, 6, 5, 4, 4, 4, 4, 4, 5]
    scores = create_test_hole_scores_dict(score_values)  # type: ignore

    scores_ith_str_hole_num = {
        str(hole_num): hole_score for hole_num, hole_score in scores.items()
    }
    with pytest.raises(hole_scores.HoleScoresValidationError):
        hole_scores.HoleScoresValidator(scores_ith_str_hole_num).validate()  # type: ignore


def test_hole_scores_validator_string_value_raises_error() -> None:
    score_values = [5, 4, 5, 6, 5, 6, 4, 4, "5", 6, 6, 5, 4, 4, 4, 4, 4, 5, 4, 6]
    scores = create_test_hole_scores_dict(score_values)  # type: ignore
    with pytest.raises(hole_scores.HoleScoresValidationError):
        hole_scores.HoleScoresValidator(scores).validate()  # type: ignore


def test_hole_scores_validator_empty_string_value_raises_error() -> None:
    score_values = [5, 4, 5, 6, 5, 6, 4, 4, "", 6, 6, 5, 4, 4, 4, 4, 4, 5, 4, 6]
    scores = create_test_hole_scores_dict(score_values)  # type: ignore
    with pytest.raises(hole_scores.HoleScoresValidationError):
        hole_scores.HoleScoresValidator(scores).validate()  # type: ignore
