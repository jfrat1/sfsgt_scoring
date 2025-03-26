from typing import Any, NamedTuple

from . import event, rank


class SeasonInputConsistencyError(Exception):
    """Exception to be raised when inconsistencies are detected in the season input data."""


class SeasonInput:
    def __init__(self, events: "EventsInput", player_names: list[str]) -> None:
        self._events = events
        self._player_names = player_names

        self._verify_event_input_consistency()

    def _verify_event_input_consistency(self) -> None:
        for event_name, event_ in self._events.items():
            if (event_player_names := event_.player_names()) != self._player_names:
                raise SeasonInputConsistencyError(
                    f"Player names in event {event_name} do not match expectations.\n"
                    f"Expected: {self._player_names}. \nFound: {event_player_names}."
                )

    @property
    def events(self) -> "EventsInput":
        return self._events

    @property
    def player_names(self) -> list[str]:
        return self._player_names

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, SeasonInput):
            return NotImplemented

        return self._events == other._events


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


class CumulativePlayerResult:
    def __init__(
        self,
        season_points: float,
        num_birdies: int,
        num_eagles: int,
        num_albatrosses: int,
        num_events_completed: int,
        num_net_strokes_wins: int,
        num_net_strokes_top_fives: int,
        num_net_strokes_top_tens: int,
        num_event_wins: int,
        num_event_top_fives: int,
        num_event_top_tens: int,
        season_handicap: float,
    ) -> None:
        self._season_points = season_points
        self._num_birdies = num_birdies
        self._num_eagles = num_eagles
        self._num_albatrosses = num_albatrosses
        self._num_events_completed = num_events_completed
        self._num_net_strokes_wins = num_net_strokes_wins
        self._num_net_strokes_top_fives = num_net_strokes_top_fives
        self._num_net_strokes_top_tens = num_net_strokes_top_tens
        self._num_event_wins = num_event_wins
        self._num_event_top_fives = num_event_top_fives
        self._num_event_top_tens = num_event_top_tens
        self._season_handicap = season_handicap
        self._season_rank: rank.IRankValue = rank.NoRankValue()

    @property
    def season_points(self) -> float:
        return self._season_points

    @property
    def season_rank(self) -> rank.IRankValue:
        return self._season_rank

    @property
    def num_birdies(self) -> int:
        return self._num_birdies

    @property
    def num_eagles(self) -> int:
        return self._num_eagles

    @property
    def num_albatrosses(self) -> int:
        return self._num_albatrosses

    @property
    def num_events_completed(self) -> int:
        return self._num_events_completed

    @property
    def num_net_strokes_wins(self) -> int:
        return self._num_net_strokes_wins

    @property
    def num_net_strokes_top_fives(self) -> int:
        return self._num_net_strokes_top_fives

    @property
    def num_net_strokes_top_tens(self) -> int:
        return self._num_net_strokes_top_tens

    @property
    def num_event_wins(self) -> int:
        return self._num_event_wins

    @property
    def num_event_top_fives(self) -> int:
        return self._num_event_top_fives

    @property
    def num_event_top_tens(self) -> int:
        return self._num_event_top_tens

    @property
    def season_handicap(self) -> float:
        return self._season_handicap

    def set_season_rank(self, new_rank: rank.RankValue) -> None:
        self._season_rank = new_rank

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, CumulativePlayerResult):
            return NotImplemented

        return (
            self._season_points == other._season_points
            and self._num_birdies == other._num_birdies
            and self._num_eagles == other._num_eagles
            and self._num_albatrosses == other._num_albatrosses
            and self._num_events_completed == other._num_events_completed
            and self._num_net_strokes_wins == other._num_net_strokes_wins
            and self._num_event_wins == other._num_event_wins
            and self._num_event_top_fives == other._num_event_top_fives
            and self._num_event_top_tens == other._num_event_top_tens
            and self._season_rank == other._season_rank
        )

    def __repr__(self) -> str:
        attributes = self.__dict__
        # Attribute names need to have their prefix underscore removed.
        attributes_string = ", ".join([f"{name.lstrip("_")}: {value}" for name, value in attributes.items()])
        return f"{self.__class__.__name__}({attributes_string})"


class Season:
    def __init__(self, input: SeasonInput) -> None:
        self._input = input
        self._events = self._create_events()

    def _create_events(self) -> dict[str, event.Event]:
        return {event_name: self._create_event(event_input) for event_name, event_input in self._input.events.items()}

    def _create_event(self, event_input: event.EventInput) -> event.Event:
        return event.Event(input=event_input)

    def results(self) -> SeasonResults:
        event_results = self._event_results()
        cumulative_results = self._cumulative_results(event_results)

        return SeasonResults(
            events=event_results,
            cumulative=cumulative_results,
        )

    def _event_results(self) -> EventResults:
        return {event_name: event_.result() for event_name, event_ in self._events.items()}

    def _cumulative_results(self, event_results: EventResults) -> CumulativeResults:
        cumulative_player_results = self._unranked_cumulative_results(event_results)
        player_season_ranks = self._player_season_ranks(cumulative_player_results)

        for player_name, player_rank in player_season_ranks.items():
            cumulative_player_results[player_name].set_season_rank(player_rank)

        return CumulativeResults(players=cumulative_player_results)

    def _unranked_cumulative_results(self, event_results) -> dict[str, CumulativePlayerResult]:
        cumulative_player_results: dict[str, CumulativePlayerResult] = {}
        for player_name in self._input.player_names:
            cumulative_player_results[player_name] = self._player_cumulative_results(
                event_results=event_results,
                player_name=player_name,
            )

        return cumulative_player_results

    def _player_cumulative_results(self, event_results: EventResults, player_name: str) -> CumulativePlayerResult:
        season_points = 0.0
        num_birdies = 0
        num_eagles = 0
        num_albatrosses = 0
        num_events_completed = 0
        num_net_strokes_wins = 0
        num_net_strokes_top_fives = 0
        num_net_strokes_top_tens = 0
        num_event_wins = 0
        num_event_top_fives = 0
        num_event_top_tens = 0

        score_differentials: list[float] = []

        for event_result in event_results.values():
            player_event_results = event_result.players[player_name]

            season_points += player_event_results.event_points
            num_birdies += player_event_results.num_birdies
            num_eagles += player_event_results.num_eagles
            num_albatrosses += player_event_results.num_albatrosses

            if player_event_results.is_complete_result():
                num_events_completed += 1
                score_differentials.append(player_event_results.score_differential)

            num_net_strokes_wins += 1 if player_event_results.net_score_rank.is_win() else 0
            num_net_strokes_top_fives += 1 if player_event_results.net_score_rank.is_top_five() else 0
            num_net_strokes_top_tens += 1 if player_event_results.net_score_rank.is_top_ten() else 0

            num_event_wins += 1 if player_event_results.event_rank.is_win() else 0
            num_event_top_fives += 1 if player_event_results.event_rank.is_top_five() else 0
            num_event_top_tens += 1 if player_event_results.event_rank.is_top_ten() else 0

        season_handicap = calc_season_handicap(score_differentials)

        return CumulativePlayerResult(
            season_points=season_points,
            num_birdies=num_birdies,
            num_eagles=num_eagles,
            num_albatrosses=num_albatrosses,
            num_events_completed=num_events_completed,
            num_net_strokes_wins=num_net_strokes_wins,
            num_net_strokes_top_fives=num_net_strokes_top_fives,
            num_net_strokes_top_tens=num_net_strokes_top_tens,
            num_event_wins=num_event_wins,
            num_event_top_fives=num_event_top_fives,
            num_event_top_tens=num_event_top_tens,
            season_handicap=season_handicap,
        )

    def _player_season_ranks(
        self,
        cumulative_player_results: dict[str, CumulativePlayerResult],
    ) -> dict[str, rank.RankValue]:
        rank_manager = rank.Rank()
        player_season_points = {
            player_name: player_result.season_points for player_name, player_result in cumulative_player_results.items()
        }
        player_season_ranks = rank_manager.player_ranks_from_values(
            player_values=player_season_points,
            rank_order=rank.RankOrder.DESCENDING,
        )

        return player_season_ranks


def calc_season_handicap(season_score_differentials: list[float]) -> float:
    score_differentials = sorted(season_score_differentials)
    num_rounds = len(score_differentials)

    base_season_handicap = calc_base_season_handicap(
        score_differentials_sorted=score_differentials,
        num_rounds=num_rounds,
    )
    handicap_penalty = calc_season_handicap_penalty(num_rounds=num_rounds)

    return base_season_handicap - handicap_penalty


def calc_base_season_handicap(score_differentials_sorted: list[float], num_rounds: int) -> float:
    match num_rounds:
        case 0:
            return 0.0
        case 1 | 2 | 3:
            # Lowest 1 round used for season handicap
            return round(score_differentials_sorted[0], 1)
        case 4 | 5:
            # Lowest 2 rounds used for season handicap
            return round(sum(score_differentials_sorted[0:2]) / 2, 1)
        case 6:
            # Lowest 3 rounds used for season handicap
            return round(sum(score_differentials_sorted[0:3]) / 3, 1)
        case _:
            return 0.0


def calc_season_handicap_penalty(num_rounds: int) -> float:
    match num_rounds:
        case 1:
            return 1.0
        case 2:
            return 0.5
        case _:
            return 0.0
