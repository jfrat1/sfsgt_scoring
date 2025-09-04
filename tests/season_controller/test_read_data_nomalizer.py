import math

import season_view
from season_common import player, scorecard
from season_controller.read_data_normalizer import SeasonReadDataNormalizer

from tests.testing_utils.score_generator import (
    ScoreGeneratorCourse,
    SimpleHoleScoreGenerator,
    SimpleHoleScoreGeneratorStrategy,
)


def build_test_player() -> player.Player:
    return player.Player(
        name="Mickey",
        gender=player.PlayerGender.MALE,
    )


def build_test_player_scorecard(course: ScoreGeneratorCourse) -> scorecard.Scorecard:
    return scorecard.CompleteScorecard(
        scores=SimpleHoleScoreGenerator(
            course=course,
            strategy=SimpleHoleScoreGeneratorStrategy.BOGIE_GOLF,
        ).generate()
    )


def build_stimulus_season_view_data() -> season_view.SeasonViewReadData:
    return season_view.SeasonViewReadData(
        players=season_view.SeasonViewReadPlayers(
            players=[
                season_view.SeasonViewReadPlayer(
                    player=build_test_player(),
                    event_handicap_indices=season_view.SeasonViewEventHandicapIndices(
                        {"Baylands": 16.0, "Presidio": math.nan}
                    ),
                ),
            ],
            are_finale_hcps_available=False,
        ),
        events=season_view.SeasonViewReadEvents(
            {
                "Baylands": season_view.SeasonViewReadEvent(
                    event_name="Baylands",
                    player_scorecards={
                        "Mickey": build_test_player_scorecard(ScoreGeneratorCourse.BAYLANDS),
                    },
                ),
                "Presidio": season_view.SeasonViewReadEvent(
                    event_name="Presidio",
                    player_scorecards={
                        "Mickey": build_test_player_scorecard(ScoreGeneratorCourse.PRESIDIO),
                    },
                ),
            },
        ),
    )


class TestSeasonViewReadDataNormalzer:
    def test_normalize_sets_scorecard_to_incomplete_for_missing_event_handicap(self) -> None:
        read_data = build_stimulus_season_view_data()

        read_data_normalized = SeasonReadDataNormalizer(read_data=read_data).normalize()

        baylands = read_data_normalized.events["Baylands"]
        assert isinstance(baylands.player_scorecard(player="Mickey"), scorecard.CompleteScorecard)

        presidio = read_data_normalized.events["Presidio"]
        assert isinstance(presidio.player_scorecard(player="Mickey"), scorecard.IncompleteScorecard)
