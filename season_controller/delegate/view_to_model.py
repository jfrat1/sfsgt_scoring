from typing import NamedTuple

import course_database
import season_config
import season_model
import season_view
from season_common import player, scorecard


class SeasonViewToModelDelegate(NamedTuple):
    view_read_data: season_view.SeasonViewReadData
    course_db: course_database.CourseDatabase
    config: season_config.SeasonConfig

    def generate_model_input(self) -> season_model.SeasonModelInput:
        return season_model.SeasonModelInput(
            player_names=self.player_names(),
            events=self.model_event_inputs(),
        )

    def player_names(self) -> list[str]:
        return [player.name() for player in self.view_read_data.players.values()]

    def model_event_inputs(self) -> season_model.SeasonModelEventInputs:
        return season_model.SeasonModelEventInputs(events=self.events())

    def event_names(self) -> tuple[str, ...]:
        return self.view_read_data.events.event_names()

    def events(self) -> list[season_model.SeasonModelEventInput]:
        _events: list[season_model.SeasonModelEventInput] = []
        for event_name in self.event_names():
            _event = season_model.SeasonModelEventInput(
                event_name=event_name,
                course=self.event_course(event_name),
                tees=self.event_tees(event_name),
                event_type=self.event_type(event_name),
                players=self.event_players(event_name),
            )
            _events.append(_event)

        return _events

    def event_course(self, event_name: str) -> course_database.Course:
        course_name = self.config.get_event_config(event_name).course_name
        return self.course_db.get_course(course_name)

    def event_tees(self, event_name: str) -> str:
        return self.config.get_event_config(event_name).tee

    def event_type(self, event_name: str) -> season_model.SeasonModelEventType:
        config_event_type = self.config.get_event_config(event_name).type
        return season_model.SeasonModelEventType.from_config_event_type(config_event_type)

    def event_players(self, event_name: str) -> list[season_model.SeasonModelEventPlayerInput]:
        _players: list[season_model.SeasonModelEventPlayerInput] = []
        for player_name in self.player_names():
            _player = season_model.SeasonModelEventPlayerInput(
                handicap_index=self.event_player_handicap_index(
                    event_name=event_name, player_name=player_name
                ),
                player=self.event_player(player_name=player_name),
                scorecard=self.event_player_scorecard(
                    event_name=event_name, player_name=player_name
                ),
            )
            _players.append(_player)

        return _players

    def event_player_handicap_index(self, event_name: str, player_name: str) -> float:
        return self.view_read_data.players[player_name].event_handicap_indices[event_name]

    def event_player(self, player_name: str) -> player.Player:
        return self.view_read_data.players[player_name].player

    def event_player_scorecard(self, event_name: str, player_name: str) -> scorecard.Scorecard:
        return self.view_read_data.events[event_name].player_scorecard(player_name)
