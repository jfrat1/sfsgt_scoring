import abc
from typing import Any, NamedTuple

from season_common import rank
from season_model.api.result import notable_holes
from utils import class_utils


class SeasonModelEventPlayerIndividualResult(abc.ABC):
    @abc.abstractmethod
    def is_complete_result(self) -> bool:
        pass

    @property
    @abc.abstractmethod
    def course_handicap(self) -> int:
        pass

    @property
    @abc.abstractmethod
    def front_9_gross(self) -> int:
        pass

    @property
    @abc.abstractmethod
    def back_9_gross(self) -> int:
        pass

    @property
    @abc.abstractmethod
    def total_gross(self) -> int:
        pass

    @property
    @abc.abstractmethod
    def total_net(self) -> int:
        pass

    @property
    @abc.abstractmethod
    def notable_holes(self) -> notable_holes.NotableHoles:
        pass

    @property
    @abc.abstractmethod
    def num_birdies(self) -> int:
        pass

    @property
    @abc.abstractmethod
    def num_eagles(self) -> int:
        pass

    @property
    @abc.abstractmethod
    def num_albatrosses(self) -> int:
        pass

    @property
    @abc.abstractmethod
    def score_differential(self) -> float:
        pass


class DisallowedApiCallError(Exception):
    """Exception raised when a call is made on an incomplete player event individual result."""


class SeasonModelIncompleteEventPlayerInividualResult(SeasonModelEventPlayerIndividualResult, class_utils.Singleton):
    def _init__(self) -> None:
        pass

    def is_complete_result(self):
        return False

    def _disallowed_api_call_error(self) -> None:
        raise DisallowedApiCallError(
            "API calls cannot be made to an incomplete player event because it does not " "contain any data."
        )

    @property
    def course_handicap(self) -> int:  # type: ignore
        self._disallowed_api_call_error()

    @property
    def front_9_gross(self) -> int:  # type: ignore
        self._disallowed_api_call_error()

    @property
    def back_9_gross(self) -> int:  # type: ignore
        self._disallowed_api_call_error()

    @property
    def total_gross(self) -> int:  # type: ignore
        self._disallowed_api_call_error()

    @property
    def total_net(self) -> int:  # type: ignore
        self._disallowed_api_call_error()

    @property
    def notable_holes(self) -> notable_holes.NotableHoles:  # type: ignore
        self._disallowed_api_call_error()

    @property
    def num_birdies(self) -> int:
        return 0

    @property
    def num_eagles(self) -> int:
        return 0

    @property
    def num_albatrosses(self) -> int:
        return 0

    @property
    def score_differential(self) -> float:
        return 0.0

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        # Use 'is' because this class implements the singleton pattern
        return self is other

    def __repr__(self) -> str:
        return "IncompletePlayerEventInividualResult()"


class SeasonModelCompleteEventPlayerIndividualResult(SeasonModelEventPlayerIndividualResult):
    def __init__(
        self,
        course_handicap: int,
        front_9_gross: int,
        back_9_gross: int,
        total_gross: int,
        total_net: int,
        notable_holes: notable_holes.NotableHoles,
        score_differential: float,
    ) -> None:
        self._course_handicap = course_handicap
        self._front_9_gross = front_9_gross
        self._back_9_gross = back_9_gross
        self._total_gross = total_gross
        self._total_net = total_net
        self._notable_holes = notable_holes
        self._score_differential = score_differential

    def is_complete_result(self):
        return True

    @property
    def course_handicap(self) -> int:
        return self._course_handicap

    @property
    def front_9_gross(self) -> int:
        return self._front_9_gross

    @property
    def back_9_gross(self) -> int:
        return self._back_9_gross

    @property
    def total_gross(self) -> int:
        return self._total_gross

    @property
    def total_net(self) -> int:
        return self._total_net

    @property
    def notable_holes(self) -> notable_holes.NotableHoles:
        return self._notable_holes

    @property
    def num_birdies(self) -> int:
        return self._notable_holes.num_birdies()

    @property
    def num_eagles(self) -> int:
        return self._notable_holes.num_eagles()

    @property
    def num_albatrosses(self) -> int:
        return self._notable_holes.num_albatrosses()

    @property
    def score_differential(self) -> float:
        return self._score_differential

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return (
            self._course_handicap == other._course_handicap
            and self._front_9_gross == other.front_9_gross
            and self._back_9_gross == other.back_9_gross
            and self._total_gross == other.total_gross
            and self._total_net == other.total_net
            and self._notable_holes == other.notable_holes
            and self._score_differential == other._score_differential
        )

    def __repr__(self) -> str:
        attributes = self.__dict__
        # Attribute names need to have their prefix underscore removed.
        attributes_string = ", ".join([f"{name.lstrip("_")}: {value}" for name, value in attributes.items()])
        return f"{self.__class__.__name__}({attributes_string})"


class SeasonModelEventPlayerAggregateResult(NamedTuple):
    gross_score_points: float
    net_score_points: float
    event_points: float
    gross_score_rank: rank.Rank
    net_score_rank: rank.Rank
    event_rank: rank.Rank


class SeasonModelEventPlayerResult:
    def __init__(
        self,
        name: str,
        individual_result: SeasonModelEventPlayerIndividualResult,
        aggregate_result: SeasonModelEventPlayerAggregateResult,
    ) -> None:
        self._name = name
        self._individual_result = individual_result
        self._aggregate_result = aggregate_result

    @property
    def is_complete_result(self) -> bool:
        return self._individual_result.is_complete_result()

    @property
    def name(self) -> str:
        return self._name

    @property
    def course_handicap(self) -> int:
        return self._individual_result.course_handicap

    @property
    def front_9_gross(self) -> int:
        return self._individual_result.front_9_gross

    @property
    def back_9_gross(self) -> int:
        return self._individual_result.back_9_gross

    @property
    def total_gross(self) -> int:
        return self._individual_result.total_gross

    @property
    def total_net(self) -> int:
        return self._individual_result.total_net

    @property
    def notable_holes(self) -> notable_holes.NotableHoles:
        return self._individual_result.notable_holes

    @property
    def gross_score_points(self) -> float:
        return self._aggregate_result.gross_score_points

    @property
    def net_score_points(self) -> float:
        return self._aggregate_result.net_score_points

    @property
    def event_points(self) -> float:
        return self._aggregate_result.event_points

    @property
    def gross_score_rank(self) -> rank.Rank:
        return self._aggregate_result.gross_score_rank

    @property
    def net_score_rank(self) -> rank.Rank:
        return self._aggregate_result.net_score_rank

    @property
    def event_rank(self) -> rank.Rank:
        return self._aggregate_result.event_rank

    @property
    def num_birdies(self) -> int:
        return self._individual_result.num_birdies

    @property
    def num_eagles(self) -> int:
        return self._individual_result.num_eagles

    @property
    def num_albatrosses(self) -> int:
        return self._individual_result.num_albatrosses

    @property
    def score_differential(self) -> float:
        return self._individual_result.score_differential

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self._individual_result == other._individual_result and self._aggregate_result == other._aggregate_result

    def __repr__(self) -> str:
        attributes = self.__dict__
        # Attribute names need to have their prefix underscore removed.
        attributes_string = ", ".join([f"{name.lstrip("_")}: {value}" for name, value in attributes.items()])
        return f"{self.__class__.__name__}({attributes_string})"


class SeasonModelEventResult(NamedTuple):
    """Results for a single event in a season."""

    name: str
    players: list[SeasonModelEventPlayerResult]

    def player_names(self) -> list[str]:
        return [player.name for player in self.players]

    def player_result(self, player_name: str) -> SeasonModelEventPlayerResult:
        candidates = [player for player in self.players if player.name == player_name]

        num_candidates = len(candidates)
        if num_candidates == 0:
            raise KeyError(f"Couldn't find and players with name {player_name}.")
        if num_candidates > 1:
            raise KeyError(f"Found more than 1 player with name {player_name}")

        return candidates[0]
