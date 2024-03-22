from typing import NamedTuple


class SeasonSheetReadData(NamedTuple):
    # dict keys are player names
    players: dict[str, "PlayerHandicapsReadData"]
    # dict keys are event names
    scoresheets: dict[str, "ScoresheetReadData"]


class PlayerHandicapsReadData(NamedTuple):
    # dict keys are event names
    handicap_index_by_event: dict[str, float]


class ScoresheetReadData(NamedTuple):
    # dict keys are player names
    players: dict[str, "PlayerScoresheetReadData"]


class PlayerScoresheetReadData(NamedTuple):
    # dict keys are holes 1-18, values are strokes
    hole_scores: dict[int, int | None]

