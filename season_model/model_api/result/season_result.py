from typing import Any, NamedTuple

from season_common import rank
from season_model.model_api.result import event_result


class SeasonModelPlayerOverallResult:
    def __init__(
        self,
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
    ) -> None:
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
        self._season_rank: rank.IRankValue = rank.NoRankValue()

    @property
    def season_points(self) -> float:
        return self._season_points

    @property
    def season_rank(self) -> rank.IRankValue:
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
        attributes_string = ", ".join(
            [f"{name.lstrip("_")}: {value}" for name, value in attributes.items()]
        )
        return f"{self.__class__.__name__}({attributes_string})"


class SeasonModelPlayerOverallResults(NamedTuple):
    players: list[SeasonModelPlayerOverallResult]


class SeasonModelResults(NamedTuple):
    events: event_result.SeasonModelEventResults
    overall: SeasonModelPlayerOverallResults
