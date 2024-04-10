import abc
import enum
from typing import Any, Literal, Union

import pandas as pd


class RankOrder(enum.Enum):
    # The lowest input value is assigned rank 1
    ASCENDING = enum.auto()
    # The highest input value is assigned rank 1
    DESCENDING = enum.auto()

    def is_ascending(self) -> bool:
        return self == RankOrder.ASCENDING


AllowedPandasRankMethods = Literal["min", "max"]


class RankTieMethod(enum.Enum):
    # Lowest rank in the group is used for tie.
    MIN = enum.auto()
    # Highest rank in the group is used for tie.
    MAX = enum.auto()

    def as_pandas_rank_method(self) -> AllowedPandasRankMethods:
        match self:
            case RankTieMethod.MIN:
                return "min"

            case RankTieMethod.MAX:
                return "max"


class Rank:
    _rank_tie_method = RankTieMethod.MIN

    def __init__(self):
        pass

    def player_ranks_from_values(
        self,
        player_values: dict[str, int] | dict[str, float],
        rank_order: RankOrder,
    ) -> dict[str, "RankValue"]:
        ranks_ser = pd.Series(player_values).rank(
            ascending=rank_order.is_ascending(),
            method=self._rank_tie_method.as_pandas_rank_method(),
        )
        players_ranks_raw: dict[str, int] = ranks_ser.astype(int).to_dict()

        return {player: RankValue(rank) for player, rank in players_ranks_raw.items()}


class RankValueNotIntegerError(Exception):
    """Exception to be raised when an event rank is constructed with a non-integer value."""


class NoRankValueApiCallError(Exception):
    """Exception to be raisd when a access requests are made on a NoRank event."""


class IRankValue(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def as_str(self) -> str: pass

    @abc.abstractmethod
    def rank(self) -> int: pass

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, IRankValue):
            return NotImplemented

        return self.rank() < other.rank()


class RankValue(IRankValue):
    def __init__(self, rank: int) -> None:
        if not isinstance(rank, int):
            raise RankValueNotIntegerError(f"Event rank value must be an integer. Got: {rank}")
        self._rank = rank

    def as_str(self) -> str:
        return str(self._rank)

    def rank(self) -> int:
        return self._rank

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, RankValue):
            return NotImplemented

        return self._rank == other._rank

    def __repr__(self) -> str:
        return f"RankValue({self.as_str()})"

    def __int__(self) -> int:
        return self._rank

    def __add__(self, addend: Union[int, "RankValue"]) -> "RankValue":
        new_rank = self._rank + int(addend)
        return RankValue(new_rank)


class NoRankValue(IRankValue):
    def __new__(cls):
        # Implement the singleton pattern for this class because there may be many
        # instances of it and they are stateless/identical.
        if not hasattr(cls, 'instance'):
            cls.instance = super(NoRankValue, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        pass

    def as_str(self) -> str:
        raise NoRankValueApiCallError(
            "API calls are not allowed on NoRank objects becuase they don't contain any data."
        )

    def rank(self) -> int:
        raise NoRankValueApiCallError(
            "API calls are not allowed on NoRank objects becuase they don't contain any data."
        )

    def __repr__(self) -> str:
        return "NoRankValue()"