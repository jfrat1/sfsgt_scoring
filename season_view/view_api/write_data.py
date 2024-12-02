from typing import NamedTuple


class SeasonViewWriteLeaderboardPlayer(NamedTuple):
    player_name: str
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
        return [player.player_name for player in self.players]


class SeasonViewWriteEventPlayer(NamedTuple):
    player_name: str
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
    players: list[SeasonViewWriteEventPlayer]


class SeasonViewWriteEvents(NamedTuple):
    events: list[SeasonViewWriteEvent]


class SeasonViewWriteFinaleHandicapPlayer(NamedTuple):
    ghin_handicap: float
    season_handicap: float
    finale_handicap: float
    finale_course_handicap: float


class SeasonViewWriteFinaleHandicaps(NamedTuple):
    players: list[SeasonViewWriteFinaleHandicapPlayer]


class SeasonViewWriteData(NamedTuple):
    leaderboard: SeasonViewWriteLeaderboard
    events: SeasonViewWriteEvents
    finale_handicaps: SeasonViewWriteFinaleHandicaps
