import abc
import enum
from typing import Any, NamedTuple

from .. import rank


class EventResult(NamedTuple):
    players: dict[str, "PlayerEventResult"]


class PlayerEventResult:
    def __init__(
        self,
        individual_result: "IPlayerEventIndividualResult",
        cumulative_result: "PlayerEventCumulativeResult",
    ) -> None:
        self._individual_result = individual_result
        self._cumulative_result = cumulative_result

    def is_complete_result(self) -> bool:
        return isinstance(self._individual_result, PlayerEventIndividualResult)

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
    def notable_holes(self) -> "NotableHoles":
        return self._individual_result.notable_holes

    @property
    def gross_score_points(self) -> float:
        return self._cumulative_result.gross_score_points

    @property
    def net_score_points(self) -> float:
        return self._cumulative_result.net_score_points

    @property
    def event_points(self) -> float:
        return self._cumulative_result.event_points

    @property
    def gross_score_rank(self) -> rank.IRankValue:
        return self._cumulative_result.gross_score_rank

    @property
    def net_score_rank(self) -> rank.IRankValue:
        return self._cumulative_result.net_score_rank

    @property
    def event_rank(self) -> rank.IRankValue:
        return self._cumulative_result.event_rank

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
        if not isinstance(other, PlayerEventResult):
            return NotImplemented

        return (
            self._individual_result == other._individual_result
            and self._cumulative_result == other._cumulative_result
        )

    def __repr__(self) -> str:
        attributes = self.__dict__
        # Attribute names need to have their prefix underscore removed.
        attributes_string = ", ".join(
            [f"{name.lstrip("_")}: {value}" for name, value in attributes.items()]
        )
        return f"{self.__class__.__name__}({attributes_string})"


class IPlayerEventIndividualResult(abc.ABC):
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
    def notable_holes(self) -> "NotableHoles":
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


class IncompletePlayerEventIndividualResultApiCallError(Exception):
    """Exception raised when a call is made on an incomplete player event individual result."""


class IncompletePlayerEventInividualResult(IPlayerEventIndividualResult):
    def __new__(cls):
        # Implement the singleton pattern for this class because there may be many
        # instances of it and they are stateless/identical.
        if not hasattr(cls, "instance"):
            cls.instance = super(IncompletePlayerEventInividualResult, cls).__new__(cls)

        return cls.instance

    def _init__(self) -> None:
        pass

    def _disallowed_api_call_error(self) -> None:
        raise IncompletePlayerEventIndividualResultApiCallError(
            "API calls cannot be made to an incomplete player event because it does not "
            "contain any data."
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
    def notable_holes(self) -> "NotableHoles":  # type: ignore
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
        if not isinstance(other, IncompletePlayerEventInividualResult):
            return NotImplemented

        # Use 'is' because this class implements the singleton pattern
        return self is other

    def __repr__(self) -> str:
        return "IncompletePlayerEventInividualResult()"


class PlayerEventIndividualResult(IPlayerEventIndividualResult):
    def __init__(
        self,
        course_handicap: int,
        front_9_gross: int,
        back_9_gross: int,
        total_gross: int,
        total_net: int,
        notable_holes: "NotableHoles",
        score_differential: float,
    ) -> None:
        self._course_handicap = course_handicap
        self._front_9_gross = front_9_gross
        self._back_9_gross = back_9_gross
        self._total_gross = total_gross
        self._total_net = total_net
        self._notable_holes = notable_holes
        self._score_differential = score_differential

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
    def notable_holes(self) -> "NotableHoles":
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
        if not isinstance(other, PlayerEventIndividualResult):
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
        attributes_string = ", ".join(
            [f"{name.lstrip("_")}: {value}" for name, value in attributes.items()]
        )
        return f"{self.__class__.__name__}({attributes_string})"


class PlayerEventCumulativeResult(NamedTuple):
    gross_score_points: float
    net_score_points: float
    event_points: float
    gross_score_rank: rank.IRankValue
    net_score_rank: rank.IRankValue
    event_rank: rank.IRankValue


class NotableHoleDuplicationError(Exception):
    """Exception to be raised when a hole has already been set with a notable hole score type."""


class NotableHoles:
    def __init__(self) -> None:
        self._birdie_holes: list[int] = []
        self._eagle_holes: list[int] = []
        self._albatross_holes: list[int] = []
        self._over_max_holes: list[int] = []

    def birdie_holes(self) -> list[int]:
        return self._birdie_holes

    def eagle_holes(self) -> list[int]:
        return self._eagle_holes

    def albatross_holes(self) -> list[int]:
        return self._albatross_holes

    def over_max_holes(self) -> list[int]:
        return self._over_max_holes

    def num_birdies(self) -> int:
        return len(self._birdie_holes)

    def num_eagles(self) -> int:
        return len(self._eagle_holes)

    def num_albatrosses(self) -> int:
        return len(self._albatross_holes)

    def set_hole(self, hole_num: int, score_type: "NotableHoleType"):
        if self._has_hole_num_been_set(hole_num):
            raise NotableHoleDuplicationError(
                f"A notable hole score has alredy been set for hole {hole_num}"
            )

        match score_type:
            case NotableHoleType.BIRDIE:
                self._birdie_holes.append(hole_num)
            case NotableHoleType.EAGLE:
                self._eagle_holes.append(hole_num)
            case NotableHoleType.ALBATROSS:
                self._albatross_holes.append(hole_num)
            case NotableHoleType.OVER_MAX:
                self._over_max_holes.append(hole_num)
            case _:
                # This should be unreachable unless a new notable hole score type is addded.
                raise ValueError(f"Unknown notable hole score type: {score_type}")

    def _has_hole_num_been_set(self, hole_num: int):
        return hole_num in self._all_hole_nums()

    def _all_hole_nums(self) -> list[int]:
        return self._birdie_holes + self._eagle_holes + self._albatross_holes + self._over_max_holes

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, NotableHoles):
            return NotImplemented

        return (
            self._birdie_holes == other.birdie_holes()
            and self._eagle_holes == other.eagle_holes()
            and self._albatross_holes == other.albatross_holes()
            and self._over_max_holes == other.over_max_holes()
        )

    def __repr__(self) -> str:
        attributes = self.__dict__
        # Attribute names need to have their prefix underscore removed.
        attributes_string = ", ".join(
            [f"{name.lstrip("_")}: {value}" for name, value in attributes.items()]
        )
        return f"{self.__class__.__name__}({attributes_string})"


class NotableHoleType(enum.Enum):
    BIRDIE = enum.auto()
    EAGLE = enum.auto()
    ALBATROSS = enum.auto()
    OVER_MAX = enum.auto()
