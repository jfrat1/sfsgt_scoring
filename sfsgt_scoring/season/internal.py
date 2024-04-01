import enum
from typing import NamedTuple


class SeasonInputs(NamedTuple):
    players: "PlayersInput"
    events: "EventsInput"


PlayersInput = dict[str, "PlayerHandicapsByEvent"]


class PlayerHandicapsByEvent(NamedTuple):
    handicaps_by_event: "HandicapsByEvent"
    pass


HandicapsByEvent = dict[str, float]

# inputs.players["player"].handicaps_by_event["event"]

EventsInput = dict[str, "EventInput"]


class EventInput(NamedTuple):
    course_name: str
    tee: str
    type: "EventType"
    player_scores: dict[str, "EventScore"]


class EventType(enum.Enum):
    STANDARD = enum.auto()
    MAJOR = enum.auto()


class EventScore(NamedTuple):
    hole_scores: "HoleScores"


HoleScores = dict[str, int | None]

# inputs.events["event"].course_name
# inputs.events["event"].tee
# inputs.events["event"].type
# inputs.events["event"].player_scores["player"].hole_scores["hole"]
#
#
#   .type
#   .player_scores["player"] - TBD from here


class SeasonResults(NamedTuple):
    pass


class Season:
    def __init__(self, inputs: SeasonInputs) -> None:
        self._inputs = inputs

    def results(self) -> SeasonResults:
        pass