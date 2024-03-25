from typing import NamedTuple

from sfsgt_scoring.spreadsheet.google import worksheet


class LeaderboardWriteData(NamedTuple):
    players: dict[str, "PlayerLeaderboardWriteData"]


class PlayerLeaderboardWriteData(NamedTuple):
    season_points: float
    events_played: int
    birdies: int
    eagles: int
    wins: int
    top_5s: int
    top_10s: int
    # dict keys are event names - should be verified by SeasonSheet class before writing
    event_points: dict[str, int]



class LeaderboardWorksheet:
    def __init__(self, worksheet: worksheet.GoogleWorksheet, players: set[str]) -> None:
        self.worksheet = worksheet
        self.players = players

    def verify(self) -> None:
        pass
