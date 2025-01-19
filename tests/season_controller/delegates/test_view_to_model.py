from unittest import mock

import courses
import season_config
import season_model
import season_view
from season_common import player, scorecard
from season_controller.delegate import view_to_model
from tests.testing_utils import score_generator


def build_test_player() -> player.Player:
    return player.Player(
        name="Mickey",
        gender=player.PlayerGender.MALE,
    )


def build_test_player_scorecard() -> scorecard.Scorecard:
    return scorecard.CompleteScorecard(
        scores=score_generator.HoleScoreGenerator(
            course=score_generator.ScoreGeneratorCourse.BAYLANDS,
            strategy=score_generator.ScoreGeneratorStrategy.BOGIE_GOLF,
        ).generate()
    )


def build_stub_course() -> mock.MagicMock:
    """Simple stub as this shouldn't be called from any tests in this file."""
    stub_course = mock.MagicMock(spec=courses.Course)
    stub_course.name = "Baylands"
    return stub_course


def build_test_course_provider(stub_course: mock.MagicMock) -> courses.CourseProvider:
    return courses.ConcreteCourseProvider(
        courses=[
            stub_course,
        ]
    )


def build_test_season_config() -> season_config.SeasonConfig:
    return season_config.SeasonConfig(
        name="Test Season",
        sheet_id="",
        players_sheet_name="",
        leaderboard_sheet_name="",
        finale_handicaps_sheet=season_config.FinaleSheetConfig(
            enabled=False,
            sheet_name="",
        ),
        events={
            1: season_config.EventConfig(
                event_name="Baylands",
                sheet_name="",
                course_name="Baylands",
                tees=season_config.EventTeeConfig(
                    mens_tee="white",
                    womens_tee="red",
                ),
                type=season_config.EventType.STANDARD,
                scorecard_sheet_start_cell="",
            )
        },
    )


def build_stimulus_season_view_data() -> season_view.SeasonViewReadData:
    return season_view.SeasonViewReadData(
        players=season_view.SeasonViewReadPlayers(
            [
                season_view.SeasonViewReadPlayer(
                    player=build_test_player(),
                    event_handicap_indices=season_view.SeasonViewEventHandicapIndices({"Baylands": 16.0}),
                ),
            ]
        ),
        events=season_view.SeasonViewReadEvents(
            {
                "Baylands": season_view.SeasonViewReadEvent(
                    event_name="Baylands",
                    player_scorecards={
                        "Mickey": build_test_player_scorecard(),
                    },
                )
            }
        ),
    )


def build_expected_model_input_data(stub_course: mock.MagicMock) -> season_model.SeasonModelInput:
    return season_model.SeasonModelInput(
        player_names=["Mickey"],
        events=season_model.SeasonModelEventInputs(
            events=[
                season_model.SeasonModelEventInput(
                    event_name="Baylands",
                    course=stub_course,
                    tees="white",
                    event_type=season_model.SeasonModelEventType.STANDARD,
                    players=[
                        season_model.SeasonModelEventPlayerInput(
                            handicap_index=16.0,
                            player=build_test_player(),
                            scorecard=build_test_player_scorecard(),
                        )
                    ],
                )
            ]
        ),
    )


def test_view_to_model_delegate() -> None:
    view_read_data = build_stimulus_season_view_data()
    stub_course = build_stub_course()
    course_provider = build_test_course_provider(stub_course)
    config = build_test_season_config()

    delegate = view_to_model.SeasonViewToModelDelegate(
        view_read_data=view_read_data,
        course_provider=course_provider,
        config=config,
    )

    model_input = delegate.generate_model_input()

    expected_model_input = build_expected_model_input_data(stub_course)

    assert model_input == expected_model_input
