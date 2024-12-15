import abc
from typing import NamedTuple

from season_model.model_api import result


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



class ConcreteFinaleData(FinaleData):
    """TODO: implement this class."""

    pass


class FinaleDataGenerator(abc.ABC):
    @abc.abstractmethod
    def generate(self) -> FinaleData:
        pass

# Ignore mypy misc check to allow NamedTuple and interface base class together
class ConcreteFinaleDataGenerator(FinaleDataGenerator, NamedTuple):  # type: ignore[misc]
    season_results: result.SeasonModelResults

    def generate(self) -> FinaleData:
        pass
