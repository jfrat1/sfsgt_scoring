import abc
from typing import NamedTuple


class FinalePlayerDescriptor(NamedTuple):
    name: str
    ghin_handicap: float
    season_handicap: float
    finale_handicap: float
    # Course handicap
    finale_course_handicap: int


class FinalePlayers(dict[str, FinalePlayerDescriptor]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)



class FinaleData(abc.ABC):
    @abc.abstractmethod
    def is_active(self) -> bool:
        pass

    @abc.abstractmethod
    def players(self) -> FinalePlayers:
        pass


class InactiveFinaleDataError(Exception):
    pass

class InactiveFinaleData(FinaleData):
    def is_active(self) -> bool:
        return False

    def players(self) -> FinalePlayers:
        raise InactiveFinaleDataError(
            "Calls to the 'players' method of an InactiveFinaleData instance are not allowed."
        )


class ActiveFinaleData(FinaleData):
    """TODO: implement this class."""
    pass


class FinaleDataGenerator(abc.ABC):
    @abc.abstractmethod
    def calculate(self) -> FinaleData:
        pass
