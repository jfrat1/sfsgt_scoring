import abc

from season_view.api import read_data, write_data


class SeasonView(abc.ABC):
    @abc.abstractmethod
    def read_season(self) -> read_data.SeasonViewReadData:
        pass

    @abc.abstractmethod
    def write_season(self, data: write_data.SeasonViewWriteData) -> None:
        pass
