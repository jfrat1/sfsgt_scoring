
from typing import NamedTuple

from .event import event


class SeasonInput(NamedTuple):
    events: "EventsInput"


class PlayerHandicapsByEvent(NamedTuple):
    handicaps_by_event: "HandicapsByEvent"


HandicapsByEvent = dict[str, float]

EventsInput = dict[str, event.EventInput]


class SeasonResults(NamedTuple):
    events: "EventResults"
    cumulative: "CumulativeResults"


EventResults = dict[str, event.EventResult]


class CumulativeResults(NamedTuple):
    players: dict[str, "CumulativePlayerResult"]


class CumulativePlayerResult(NamedTuple):
    season_points: float
    season_rank: int
    num_birdies: int
    num_eagles: int
    num_albatrosses: int


class Season:
    def __init__(self, input: SeasonInput) -> None:
        self._input = input
        # self._events = self._create_events()
        # load scoring config (TBD, haven't defined this yet)
        # configure events
        #  - load course info from database and combine with player score data
        #  - make this a unique class

    def _create_events(self) -> dict[str, event.Event]:
        # TODO - test needed
        return {
            event_name: self._create_event(event_input)
            for event_name, event_input in self._input.events.items()
        }

    def _create_event(self, event_input: event.EventInput) -> event.Event:
        # TODO - test needed
        return event.Event(input=event_input)

    def results(self) -> SeasonResults:
        # Calculate results of each event
        # - by player
        #    - front 9 gross
        #    - back 9 gross
        #    - 18 gross
        #    - course handicap
        #    - 18 net
        #    - gross score rank
        #    - net score rank
        #    - event points
        #    - event rank
        #    - under par holes (birdie, eagle, albatross listed separately)
        #
        # Calculate season-wide results
        #  - by player
        #    - points per event (consider just leveraging the data above rather than duplicating here)
        #    - total season points
        #    - season rank
        #    - # of below par scores (birdie, eagle, albatross listed separately)
        return None

