import pandas as pd
import pytest

from sfsgt_scoring_2023 import event


def test_constructor() -> None:
    hole_scores = pd.Series(
        data=[4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
        index=[str(hole) for hole in range(1, 19)],
    )
    event.PlayerScore(
        course_handicap=15,
        hole_scores=hole_scores,
    )


def test_constructor_hole_scores_missing_indices() -> None:
    hole_scores = pd.Series(
        data=[
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
        ],
        index=[str(hole) for hole in range(1, 18)],
    )
    with pytest.raises(
        event.PlayerScoreHoleScoresException,
        match="Malformed hole scores series. The index of the series should be strings 1 through 18",  # noqa: E501
    ):
        event.PlayerScore(
            course_handicap=15,
            hole_scores=hole_scores,
        )


def test_get_result() -> None:
    hole_scores = pd.Series(
        data=[4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5],
        index=[str(hole) for hole in range(1, 19)],
    )
    player_score = event.PlayerScore(
        course_handicap=15,
        hole_scores=hole_scores,
    )

    results = player_score.get_results()

    assert set(results.index) == {"Out", "In", "Gross", "Net"}
    assert all(results == pd.Series({"Out": 36, "In": 45, "Gross": 81, "Net": 66}))
