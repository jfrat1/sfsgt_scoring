import abc
from typing import Any


class EventRankNotIntegerError(Exception):
    """Exception to be raised when an event rank is constructed with a non-integer value."""


class NoRankAccessError(Exception):
    """Exception to be raisd when a access requests are made on a NoRank event."""


class IEventRank(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def as_str(self) -> str: pass


class EventRank(IEventRank):
    def __init__(self, rank: int) -> None:
        if not isinstance(rank, int):
            raise EventRankNotIntegerError(f"Event rank value must be an integer. Got: {rank}")
        self._rank = rank

    def as_str(self) -> str:
        return str(self._rank)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, EventRank):
            return NotImplemented

        return self._rank == other._rank


class NoRank(IEventRank):
    def __new__(cls):
        # Implement the singleton pattern for this class because there may be many
        # instances of it and they are stateless/identical.
        if not hasattr(cls, 'instance'):
            cls.instance = super(NoRank, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        pass

    def as_str(self) -> str:
        raise NoRankAccessError(
            "API calls are not allowed on NoRank objects becuase they don't contain any data."
        )
