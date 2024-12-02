import abc

from season_view.view_api import read_data, write_data


class SeasonView(abc.ABC):
    @abc.abstractmethod
    def read(self) -> read_data.SeasonViewReadData:
        pass

    @abc.abstractmethod
    def write(self, data: write_data.SeasonViewWriteData) -> None:
        pass
