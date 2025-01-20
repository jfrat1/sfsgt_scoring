from typing import Any, NamedTuple

from season_common import rank
from season_model.api.result import event_result


class SeasonModelPlayerOverallResult:
    def __init__(
        self,
        name: str,
        season_points: float,
        num_birdies: int,
        num_eagles: int,
        num_albatrosses: int,
        num_events_completed: int,
        num_net_strokes_wins: int,
        num_net_strokes_top_fives: int,
        num_net_strokes_top_tens: int,
        num_event_wins: int,
        num_event_top_fives: int,
        num_event_top_tens: int,
        season_handicap: float,
        season_rank: rank.Rank = rank.NoRankValue(),
    ) -> None:
        self._name = name
        self._season_points = season_points
        self._num_birdies = num_birdies
        self._num_eagles = num_eagles
        self._num_albatrosses = num_albatrosses
        self._num_events_completed = num_events_completed
        self._num_net_strokes_wins = num_net_strokes_wins
        self._num_net_strokes_top_fives = num_net_strokes_top_fives
        self._num_net_strokes_top_tens = num_net_strokes_top_tens
        self._num_event_wins = num_event_wins
        self._num_event_top_fives = num_event_top_fives
        self._num_event_top_tens = num_event_top_tens
        self._season_handicap = season_handicap
        self._season_rank = season_rank

    @property
    def name(self) -> str:
        return self._name

    @property
    def season_points(self) -> float:
        return self._season_points

    @property
    def season_rank(self) -> rank.Rank:
        return self._season_rank

    @property
    def num_birdies(self) -> int:
        return self._num_birdies

    @property
    def num_eagles(self) -> int:
        return self._num_eagles

    @property
    def num_albatrosses(self) -> int:
        return self._num_albatrosses

    @property
    def num_events_completed(self) -> int:
        return self._num_events_completed

    @property
    def num_net_strokes_wins(self) -> int:
        return self._num_net_strokes_wins

    @property
    def num_net_strokes_top_fives(self) -> int:
        return self._num_net_strokes_top_fives

    @property
    def num_net_strokes_top_tens(self) -> int:
        return self._num_net_strokes_top_tens

    @property
    def num_event_wins(self) -> int:
        return self._num_event_wins

    @property
    def num_event_top_fives(self) -> int:
        return self._num_event_top_fives

    @property
    def num_event_top_tens(self) -> int:
        return self._num_event_top_tens

    @property
    def season_handicap(self) -> float:
        return self._season_handicap

    def set_season_rank(self, new_rank: rank.RankValue) -> None:
        self._season_rank = new_rank

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return (
            self._season_points == other._season_points
            and self._num_birdies == other._num_birdies
            and self._num_eagles == other._num_eagles
            and self._num_albatrosses == other._num_albatrosses
            and self._num_events_completed == other._num_events_completed
            and self._num_net_strokes_wins == other._num_net_strokes_wins
            and self._num_event_wins == other._num_event_wins
            and self._num_event_top_fives == other._num_event_top_fives
            and self._num_event_top_tens == other._num_event_top_tens
            and self._season_rank == other._season_rank
        )

    def __repr__(self) -> str:
        attributes = self.__dict__
        # Attribute names need to have their prefix underscore removed.
        attributes_string = ", ".join([f"{name.lstrip("_")}: {value}" for name, value in attributes.items()])
        return f"{self.__class__.__name__}({attributes_string})"


class SeasonModelOverallResults(NamedTuple):
    players: list[SeasonModelPlayerOverallResult]

    def player_names(self) -> list[str]:
        return [player.name for player in self.players]

    def get_player(self, player_name: str) -> SeasonModelPlayerOverallResult:
        candidates = [player for player in self.players if player.name == player_name]

        num_candidates = len(candidates)
        if num_candidates == 0:
            raise KeyError(f"Couldn't find and players with name {player_name}.")
        if num_candidates > 1:
            raise KeyError(f"Found more than 1 player with name {player_name}")

        return candidates[0]


class SeasonModelResults(NamedTuple):
    events: list[event_result.SeasonModelEventResult]
    overall: SeasonModelOverallResults

    def player_names(self) -> list[str]:
        return self.overall.player_names()

    def player_overall_result(self, player_name) -> SeasonModelPlayerOverallResult:
        return self.overall.get_player(player_name)

    def player_event_points(self, player_name: str) -> dict[str, float]:
        event_points: dict[str, float] = {}
        for event in self.events:
            event_points[event.name] = event.player_result(player_name).event_points

        return event_points

    def event_names(self) -> list[str]:
        return [event.name for event in self.events]

    def event_result(self, event_name: str) -> event_result.SeasonModelEventResult:
        candidates = [event for event in self.events if event.name == event_name]

        num_candidates = len(candidates)
        if num_candidates == 0:
            raise KeyError(f"Couldn't find and events with name {event_name}.")
        if num_candidates > 1:
            raise KeyError(f"Found more than 1 event with name {event_name}")

        return candidates[0]
