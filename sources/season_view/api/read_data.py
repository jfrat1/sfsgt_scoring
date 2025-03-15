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

    def event_handicap_index(self, event_name: str) -> float:
        try:
            return self.event_handicap_indices[event_name]

        except KeyError:
            raise SeasonViewReadDataResourceNotFoundError(
                f"Event handicap for event {event_name} cannot be found for {self.player}."
            )


class SeasonViewReadPlayers(dict[str, SeasonViewReadPlayer]):
    """Collection of SeasonViewReadPlayer for each player in a season."""

    def __init__(
        self,
        players: list[SeasonViewReadPlayer],
        are_finale_hcps_available: bool,
    ) -> None:
        """Constructs a SeasonVieReadPlayersInstance from a list of SeasonViewReadPlayer."""
        self._are_finale_hcps_available = are_finale_hcps_available

        player_names = [player.name for player in players]
        dedup_player_names = set(player_names)

        if len(player_names) != len(dedup_player_names):
            duplicates = [name for name in dedup_player_names if player_names.count(name) > 1]
            raise ValueError(f"Duplicate player names are not allowed. Found these duplicates: {duplicates}")

        players_dict = {player.name(): player for player in players}
        super().__init__(players_dict)

    @property
    def are_finale_hcps_available(self) -> bool:
        return self._are_finale_hcps_available

    @property
    def player_names(self) -> list[str]:
        return list(self.keys())

    def finale_handicaps_by_player(self) -> dict[str, float]:
        if not self.are_finale_hcps_available:
            raise SeasonViewReadDataResourceNotFoundError("Finale handicaps are not available.")

        return {player_name: player.event_handicap_index("Finale") for player_name, player in self.items()}

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
            raise SeasonViewReadDataResourceNotFoundError(f"Can't locate event namaed '{event}' in Season View events.")


class SeasonViewReadData(NamedTuple):
    players: SeasonViewReadPlayers
    events: SeasonViewReadEvents

    @property
    def player_names(self) -> list[str]:
        return self.players.player_names

    @property
    def event_names(self) -> list[str]:
        return self.events.event_names

    @property
    def are_finale_hcps_available(self) -> bool:
        return self.players.are_finale_hcps_available

    def finale_handicaps_by_player(self) -> dict[str, float]:
        return self.players.finale_handicaps_by_player()
