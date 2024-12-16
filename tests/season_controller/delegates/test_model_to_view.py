import season_model
import season_view
from season_common import rank
from season_controller.delegate import model_to_view


def build_test_season_model_results() -> season_model.SeasonModelResults:
    return season_model.SeasonModelResults(
        events=[
            season_model.SeasonModelEventResult(
                name="Baylands",
                players=[
                    season_model.SeasonModelEventPlayerResult(
                        name="Mickey",
                        individual_result=season_model.SeasonModelCompleteEventPlayerIndividualResult(
                            course_handicap=16,
                            front_9_gross=42,
                            back_9_gross=43,
                            total_gross=85,
                            total_net=69,
                            notable_holes=season_model.NotableHoles(),
                            score_differential=14.0,
                        ),
                        aggregate_result=season_model.SeasonModelEventPlayerAggregateResult(
                            gross_score_points=50.0,
                            net_score_points=45.0,
                            event_points=95.0,
                            gross_score_rank=rank.RankValue(1),
                            net_score_rank=rank.RankValue(1),
                            event_rank=rank.RankValue(1),
                        ),
                    )
                ],
            )
        ],
        overall=season_model.SeasonModelOverallResults(
            players=[
                season_model.SeasonModelPlayerOverallResult(
                    name="Mickey",
                    season_points=95.0,
                    season_rank=rank.RankValue(1),
                    num_birdies=1,
                    num_eagles=0,
                    num_albatrosses=0,
                    num_events_completed=1,
                    num_net_strokes_wins=1,
                    num_net_strokes_top_fives=1,
                    num_net_strokes_top_tens=1,
                    num_event_wins=1,
                    num_event_top_fives=1,
                    num_event_top_tens=1,
                    season_handicap=14.0,
                )
            ]
        ),
    )


def build_test_season_view_write_data() -> season_view.SeasonViewWriteData:
    return season_view.SeasonViewWriteData(
        leaderboard=season_view.SeasonViewWriteLeaderboard(
            players=[
                season_view.SeasonViewWriteLeaderboardPlayer(
                    name="Mickey",
                    season_points=95.0,
                    season_rank=1,
                    events_played=1,
                    birdies=1,
                    eagles=0,
                    net_strokes_wins=1,
                    net_strokes_top_fives=1,
                    net_strokes_top_tens=1,
                    event_wins=1,
                    event_top_fives=1,
                    event_top_tens=1,
                    event_points={
                        "Baylands": 95.0,
                    },
                )
            ]
        ),
        events=[
            season_view.SeasonViewWriteEvent(
                name="Baylands",
                players=[
                    season_view.SeasonViewWriteEventPlayer(
                        name="Mickey",
                        front_9_strokes=42,
                        back_9_strokes=43,
                        gross_strokes=85,
                        course_handicap=16,
                        net_strokes=69,
                        gross_rank=1,
                        net_rank=1,
                        gross_points=50.0,
                        net_points=45.0,
                        event_points=95.0,
                        event_rank=1,
                    )
                ],
            )
        ],
    )


def test_model_to_view_delegate() -> None:
    season_model_result = build_test_season_model_results()

    delegate = model_to_view.SeasonModelToViewDelegate(
        model_results=season_model_result,
    )

    view_write_data = delegate.generate_view_write_data()

    expected_view_write_data = build_test_season_view_write_data()

    assert view_write_data == expected_view_write_data
