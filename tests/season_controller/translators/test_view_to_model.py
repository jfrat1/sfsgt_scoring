import season_model
import season_view
from season_common import player, scorecard
from tests.testing_utils import score_generator


def build_stimulus_season_view_data() -> season_view.SeasonViewReadData:
    return season_view.SeasonViewReadData(
        players=season_view.SeasonViewReadPlayers(
            {
                "Mickey": season_view.SeasonViewReadPlayer(
                    player=player.Player(
                        name="Mickey",
                        gender=player.PlayerGender.MALE,
                    ),
                    event_handicap_indices=season_view.SeasonViewEventHandicapIndices(
                        {"Baylands": 16.0}
                    ),
                )
            }
        ),
        events=season_view.SeasonViewReadEvents(
            {
                "Baylands": season_view.SeasonViewReadEvent(
                    event_name="Baylands",
                    player_scorecards={
                        "Mickey": scorecard.CompleteScorecard(
                            scores=score_generator.generate_hole_scores(
                                course=score_generator.ScoreGeneratorCourse.BAYLANDS,
                                strategy=score_generator.ScoreGeneratorStrategy.BOGIE_GOLF,
                            ),
                        )
                    },
                )
            }
        ),
    )


def build_expected_model_input_data() -> season_model.SeasonModelInput:
    return season_model.SeasonModelInput(
        players_names=["Mickey"],
        events=season_model.SeasonModelEventInputs(
            events=[
                season_model.SeasonModelEventInput(
                    event_name="Baylands",
                    course=None,  # This will need to match whatever I stub and send into the delegate for the course_db
                )
            ]
        ),
    )
    pass
