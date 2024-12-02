import abc
from typing import Any, Union

from utils import class_utils


class RankValueNotIntegerError(Exception):
    """Exception to be raised when an event rank is constructed with a non-integer value."""


class NoRankValueApiCallError(Exception):
    """Exception to be raisd when a access requests are made on a NoRank event."""


class IRankValue(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def as_str(self) -> str:
        pass

    @abc.abstractmethod
    def rank(self) -> int:
        pass

    @abc.abstractmethod
    def is_win(self) -> bool:
        pass

    @abc.abstractmethod
    def is_top_five(self) -> bool:
        pass

    @abc.abstractmethod
    def is_top_ten(self) -> bool:
        pass

    def __int__(self) -> int:
        return self.rank()

    def __add__(self, addend: Union[int, "IRankValue"]) -> "RankValue":
        new_rank = self.rank() + int(addend)
        return RankValue(new_rank)

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

    def is_win(self) -> bool:
        return self._rank == 1

    def is_top_five(self) -> bool:
        return self._rank <= 5

    def is_top_ten(self) -> bool:
        return self._rank <= 10

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, RankValue):
            return NotImplemented

        return self._rank == other._rank

    def __repr__(self) -> str:
        return f"RankValue({self.as_str()})"


class NoRankValue(IRankValue, class_utils.Singleton):
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

    def is_win(self) -> bool:
        return False

    def is_top_five(self) -> bool:
        return False

    def is_top_ten(self) -> bool:
        return False

    def __repr__(self) -> str:
        return "NoRankValue()"

