from typing import NamedTuple

import season_model
import season_view


class SeasonModelToViewDelegate(NamedTuple):
    model_results: season_model.SeasonModelResults

    def generate_view_write_data(self) -> season_view.SeasonViewWriteData:
        event_names = self.model_results.event_names()
        return season_view.SeasonViewWriteData(
            leaderboard=self._leaderboard(),
            events=[self._event(event_name) for event_name in event_names],
        )

    def _leaderboard(self) -> season_view.SeasonViewWriteLeaderboard:
        return season_view.SeasonViewWriteLeaderboard(
            players=[self._leaderboard_player(player_name) for player_name in self._player_names()]
        )

    def _player_names(self) -> list[str]:
        return self.model_results.player_names()

    def _leaderboard_player(self, player_name: str) -> season_view.SeasonViewWriteLeaderboardPlayer:
        overall_result = self.model_results.player_overall_result(player_name)
        event_points = self.model_results.player_event_points(player_name)

        return season_view.SeasonViewWriteLeaderboardPlayer(
            name=player_name,
            season_points=overall_result.season_points,
            season_rank=overall_result.season_rank.rank(),
            events_played=overall_result.num_events_completed,
            birdies=overall_result.num_birdies,
            eagles=overall_result.num_eagles,
            net_strokes_wins=overall_result.num_net_strokes_wins,
            net_strokes_top_fives=overall_result.num_net_strokes_top_fives,
            net_strokes_top_tens=overall_result.num_net_strokes_top_tens,
            event_wins=overall_result.num_event_wins,
            event_top_fives=overall_result.num_event_top_fives,
            event_top_tens=overall_result.num_event_top_tens,
            event_points=event_points,
        )

    def _event(self, event_name: str) -> season_view.SeasonViewWriteEvent:
        event_results = self.model_results.event_result(event_name)
        player_names = self._player_names()
        return season_view.SeasonViewWriteEvent(
            name=event_name,
            players=[
                self._event_player(event_results=event_results, player_name=player_name)
                for player_name in player_names
            ],
        )

    def _event_player(
        self,
        event_results: season_model.SeasonModelEventResult,
        player_name: str,
    ) -> season_view.SeasonViewWriteEventPlayer:
        event_player_result = event_results.player_result(player_name)

        return season_view.SeasonViewWriteEventPlayer(
            name=player_name,
            front_9_strokes=event_player_result.front_9_gross,
            back_9_strokes=event_player_result.back_9_gross,
            gross_strokes=event_player_result.total_gross,
            course_handicap=event_player_result.course_handicap,
            net_strokes=event_player_result.total_net,
            gross_rank=event_player_result.gross_score_rank.rank(),
            net_rank=event_player_result.net_score_rank.rank(),
            gross_points=event_player_result.gross_score_points,
            net_points=event_player_result.net_score_points,
            event_points=event_player_result.event_points,
            event_rank=event_player_result.event_rank.rank(),
        )
