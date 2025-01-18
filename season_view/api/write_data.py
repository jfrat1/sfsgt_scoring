from typing import NamedTuple


class SeasonViewWriteLeaderboardPlayer(NamedTuple):
    name: str
    season_points: float
    season_rank: int
    events_played: int
    birdies: int
    eagles: int
    net_strokes_wins: int
    net_strokes_top_fives: int
    net_strokes_top_tens: int
    event_wins: int
    event_top_fives: int
    event_top_tens: int
    # Keys are event names
    event_points: dict[str, float]


class SeasonViewWriteLeaderboard(NamedTuple):
    players: list[SeasonViewWriteLeaderboardPlayer]

    def players_rank_sorted(self) -> list[SeasonViewWriteLeaderboardPlayer]:
        return sorted(self.players, key=lambda player: player.season_rank)

    def player_names(self) -> list[str]:
        return [player.name for player in self.players]


class SeasonViewWriteEventPlayer(NamedTuple):
    name: str
    front_9_strokes: int
    back_9_strokes: int
    gross_strokes: int
    course_handicap: int
    net_strokes: int
    gross_rank: int
    net_rank: int
    gross_points: float
    net_points: float
    event_points: float
    event_rank: int


class SeasonViewWriteEvent(NamedTuple):
    name: str
    players: list[SeasonViewWriteEventPlayer]


class SeasonViewWriteData(NamedTuple):
    leaderboard: SeasonViewWriteLeaderboard
    events: list[SeasonViewWriteEvent]
