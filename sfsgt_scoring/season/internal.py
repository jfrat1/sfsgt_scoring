from typing import NamedTuple


class SeasonInputs(NamedTuple):
    pass


class PlayersInput(NamedTuple):
    pass


class EventsInput(NamedTuple):
    pass


class SeasonResults(NamedTuple):
    pass


class Season:
    def __init__(self, inputs: SeasonInputs) -> None:
        self._inputs = inputs

    def results(self) -> SeasonResults:
        pass