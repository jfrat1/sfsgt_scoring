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

class SeasonViewReadPlayers(dict[str, SeasonViewReadPlayer]):
    """Collection of SeasonViewReadPlayer for each player in a season."""

    def __init__(self, players: list[SeasonViewReadPlayer]) -> None:
        """Constructs a SeasonVieReadPlayersInstance from a list of SeasonViewReadPlayer."""
        player_names = [player.name for player in players]
        dedup_player_names = set(player_names)

        if len(player_names) != len(dedup_player_names):
            duplicates = [name for name in dedup_player_names if player_names.count(name) > 1]
            raise ValueError(
                f"Duplicate player names are not allowed. Found these duplicates: {duplicates}"
                )

        players_dict = {
            player.name(): player for player in players
        }
        super().__init__(players_dict)

    @property
    def player_names(self) -> list[str]:
        return list(self.keys())

    def __getitem__(self, player_name: str) -> SeasonViewReadPlayer:
        if player_name in self.keys():
            return super().__getitem__(player_name)
        else:
            raise SeasonViewReadDataResourceNotFoundError(
                f"Can't locate player named '{player}' in Season View players."
            )


class SeasonViewReadEvent:
    def __init__(self, event_name: str, player_scorecards: dict[str, scorecard.Scorecard]) -> None:
        self.event_name = event_name
        self._player_scorecards = player_scorecards

    @property
    def player_names(self) -> list[str]:
        return list(self._player_scorecards.keys())

    def player_scorecard(self, player: str) -> scorecard.Scorecard:
        if player in self._player_scorecards.keys():
            return self._player_scorecards[player]

        else:
            raise SeasonViewReadDataResourceNotFoundError(
                f"Can't locate player '{player}' in Season View data for event {self.event_name}"
            )


class SeasonViewReadEvents(dict[str, SeasonViewReadEvent]):
    @property
    def event_names(self) -> list[str]:
        return list(self.keys())

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

    @property
    def player_names(self) -> list[str]:
        return self.players.player_names

    @property
    def event_names(self) -> list[str]:
        return self.events.event_names
