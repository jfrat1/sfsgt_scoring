from typing import NamedTuple

from season_common import player, scorecard


class SeasonViewReadDataResourceNotFoundError(Exception):
    pass


class SeasonViewEventHandicapIndices(dict[str, float]):
    """Collection of handicaps for a single player each event in a season."""

    def __getitem__(self, event: str) -> float:
        if event in self.keys():
            return super().__getitem__(event)
        else:
            raise SeasonViewReadDataResourceNotFoundError(
                f"Can't locate event named '{event}' in event handicap indices."
            )


class SeasonViewReadPlayer(NamedTuple):
    player: player.Player
    event_handicap_indices: SeasonViewEventHandicapIndices

    def name(self) -> str:
        return self.player.name


# TODO: Consider making this a list instead of a dict. The player names are duplicated
# in the keys and in the SeasonViewReadPlayer instances
class SeasonViewReadPlayers(dict[str, SeasonViewReadPlayer]):
    """Collection of SeasonViewReadPlayer for each player in a season."""

    def player_names(self) -> tuple[str, ...]:
        return tuple(_player.name() for _player in self.values())

    def __getitem__(self, player: str) -> SeasonViewReadPlayer:
        if player in self.keys():
            return super().__getitem__(player)
        else:
            raise SeasonViewReadDataResourceNotFoundError(
                f"Can't locate player named '{player}' in Season View players."
            )


class SeasonViewReadEvent:
    def __init__(self, event_name: str, player_scorecards: dict[str, scorecard.Scorecard]) -> None:
        self.event_name = event_name
        self._player_scorecards = player_scorecards

    def player_names(self) -> tuple[str, ...]:
        return tuple(self._player_scorecards.keys())

    def player_scorecard(self, player: str) -> scorecard.Scorecard:
        if player in self._player_scorecards.keys():
            return self._player_scorecards[player]

        else:
            raise SeasonViewReadDataResourceNotFoundError(
                f"Can't locate player '{player}' in Season View data for event {self.event_name}"
            )


class SeasonViewReadEvents(dict[str, SeasonViewReadEvent]):
    def event_names(self) -> tuple[str, ...]:
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
