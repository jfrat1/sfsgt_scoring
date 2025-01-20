from typing import NamedTuple

import courses
import season_config
import season_model
import season_view
from season_common import player, scorecard


class SeasonViewToModelDelegate(NamedTuple):
    view_read_data: season_view.SeasonViewReadData
    course_provider: courses.CourseProvider
    config: season_config.SeasonConfig

    def generate_model_input(self) -> season_model.SeasonModelInput:
        return season_model.SeasonModelInput(
            player_names=self._player_names(),
            events=self._model_event_inputs(),
        )

    def _player_names(self) -> list[str]:
        return self.view_read_data.players.player_names

    def _model_event_inputs(self) -> season_model.SeasonModelEventInputs:
        return season_model.SeasonModelEventInputs(events=self._events())

    @property
    def _event_names(self) -> list[str]:
        return self.view_read_data.events.event_names

    def _events(self) -> list[season_model.SeasonModelEventInput]:
        _events: list[season_model.SeasonModelEventInput] = []
        for event_name in self._event_names:
            _event = season_model.SeasonModelEventInput(
                event_name=event_name,
                course=self._event_course(event_name),
                tees=self._event_tees(event_name),
                event_type=self._event_type(event_name),
                players=self._event_players(event_name),
            )
            _events.append(_event)

        return _events

    def _event_course(self, event_name: str) -> courses.Course:
        course_name = self.config.get_event_config(event_name).course_name
        return self.course_provider.get_course(course_name)

    def _event_tees(self, event_name: str) -> season_model.SeasonModelEventTees:
        tee_config = self.config.get_event_config(event_name).tees
        return season_model.SeasonModelEventTees(
            mens_tee=tee_config.mens_tee,
            womens_tee=tee_config.womens_tee,
        )

    def _event_type(self, event_name: str) -> season_model.SeasonModelEventType:
        config_event_type = self.config.get_event_config(event_name).type
        return season_model.SeasonModelEventType.from_config_event_type(config_event_type)

    def _event_players(self, event_name: str) -> list[season_model.SeasonModelEventPlayerInput]:
        _players: list[season_model.SeasonModelEventPlayerInput] = []
        for player_name in self._player_names():
            _player = season_model.SeasonModelEventPlayerInput(
                handicap_index=self._event_player_handicap_index(event_name=event_name, player_name=player_name),
                player=self._event_player(player_name=player_name),
                scorecard=self._event_player_scorecard(event_name=event_name, player_name=player_name),
            )
            _players.append(_player)

        return _players

    def _event_player_handicap_index(self, event_name: str, player_name: str) -> float:
        return self.view_read_data.players[player_name].event_handicap_indices[event_name]

    def _event_player(self, player_name: str) -> player.Player:
        return self.view_read_data.players[player_name].player

    def _event_player_scorecard(self, event_name: str, player_name: str) -> scorecard.Scorecard:
        return self.view_read_data.events[event_name].player_scorecard(player_name)
