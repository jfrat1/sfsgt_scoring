import enum
from typing import NamedTuple, TypeVar

from season_view.interface import hole_scores

T = TypeVar("T")


class SeasonViewReadDataResourceNotFoundError(Exception):
    pass


class SeasonViewPlayerGender(enum.Enum):
    MALE = enum.auto()
    FEMALE = enum.auto()


class SeasonViewEventHandicapIndices(dict[str, float]):
    def __getitem__(self, event: str) -> float:
        if event in self.keys():
            return super().__getitem__(event)
        else:
            raise SeasonViewReadDataResourceNotFoundError(
                f"Can't locate event named '{event}' in event handicap indices."
            )


class SeasonViewReadPlayer(NamedTuple):
    name: str
    gender: SeasonViewPlayerGender
    event_handicap_indices: SeasonViewEventHandicapIndices


class SeasonViewReadPlayers(dict[str, SeasonViewReadPlayer]):
    def __getitem__(self, player: str) -> SeasonViewReadPlayer:
        if player in self.keys():
            return super().__getitem__(player)
        else:
            raise SeasonViewReadDataResourceNotFoundError(
                f"Can't locate player named '{player}' in Season View players."
            )


class SeasonViewReadEvent:
    def __init__(self, event_name: str, player_scores: dict[str, hole_scores.HoleScores]) -> None:
        self.event_name = event_name
        self._player_scores = player_scores

    def player_names(self) -> tuple[str]:
        return tuple(self._player_scores.keys())

    def player_hole_scores(self, player: str) -> hole_scores.HoleScores:
        if player in self._player_scores.keys():
            return self._player_scores[player]

        else:
            raise SeasonViewReadDataResourceNotFoundError(
                f"Can't locate player '{player}' in Season View data for event {self.event_name}"
            )


class SeasonViewReadEvents(dict[str, SeasonViewReadEvent]):
    def event_names(self) -> tuple[str]:
        return tuple(self.keys())

    def __getitem__(self, event: str) -> SeasonViewReadEvent:
        if event in self.keys():
            return super().__getitem__(event)

        else:
            raise SeasonViewReadDataResourceNotFoundError(
                f"Can't locate event namaed '{event}' in Season View events."
            )


class SeasonViewReadData(NamedTuple):
    players: SeasonViewReadPlayers
    events: SeasonViewReadEvents
