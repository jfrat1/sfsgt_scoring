from typing import NamedTuple


class SeasonSheetWriteData(NamedTuple):
    leaderboard: "LeaderboardWriteData"
    # dict keys are event names - should be verified by SeasonSheet class before writing
    scoresheets: dict[str, "ScoresheetWriteData"]


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


class ScoresheetWriteData(NamedTuple):
    players: dict[str, "PlayerScoresheetWriteData"]
    birdies: list["PlayerHole"]
    eagles: list["PlayerHole"]
    hole_scores_over_max: list["PlayerHole"]


class PlayerScoresheetWriteData(NamedTuple):
    front_9_strokes: int
    back_9_strokes: int
    gross_strokes: int
    net_strokes: int
    gross_rank: int
    net_rank: int
    gross_points: float
    net_points: float
    event_points: float
    event_rank: int


class PlayerHole(NamedTuple):
    player: str
    hole: int




