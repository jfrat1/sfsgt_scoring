import abc
from typing import Any, NamedTuple


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

    @property
    def player_names(self) -> list[str]:
        return [player.name for player in self.players]

    @property
    def num_players(self) -> int:
        return len(self.players)


class SeasonViewWritePlayerEvent(abc.ABC):
    @property
    @abc.abstractmethod
    def is_complete_event(self) -> bool:
        pass

    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def front_9_strokes(self) -> int:
        pass

    @property
    @abc.abstractmethod
    def back_9_strokes(self) -> int:
        pass

    @property
    @abc.abstractmethod
    def gross_strokes(self) -> int:
        pass

    @property
    @abc.abstractmethod
    def course_handicap(self) -> int:
        pass

    @property
    @abc.abstractmethod
    def net_strokes(self) -> int:
        pass

    @property
    @abc.abstractmethod
    def gross_rank(self) -> int:
        pass

    @property
    @abc.abstractmethod
    def net_rank(self) -> int:
        pass

    @property
    @abc.abstractmethod
    def gross_points(self) -> float:
        pass

    @property
    @abc.abstractmethod
    def net_points(self) -> float:
        pass

    @property
    @abc.abstractmethod
    def event_points(self) -> float:
        pass

    @property
    @abc.abstractmethod
    def event_rank(self) -> int:
        pass


class SeasonViewIncompleteEventAccessError(Exception):
    pass


class SeasonViewWritePlayerIncompleteEvent(SeasonViewWritePlayerEvent):
    def __init__(
        self,
        name: str,
        gross_points: float,
        net_points: float,
        event_points: float,
        event_rank: int,
    ) -> None:
        self._name = name
        self._gross_points = gross_points
        self._net_points = net_points
        self._event_points = event_points
        self._event_rank = event_rank

    @property
    def is_complete_event(self) -> bool:
        return False

    @property
    def name(self) -> str:
        return self._name

    @property
    def front_9_strokes(self) -> int:
        raise SeasonViewIncompleteEventAccessError("Acces to front_9_strokes is not allowed for incomplete events.")

    @property
    def back_9_strokes(self) -> int:
        raise SeasonViewIncompleteEventAccessError("Acces to back_9_strokes is not allowed for incomplete events.")

    @property
    def gross_strokes(self) -> int:
        raise SeasonViewIncompleteEventAccessError("Acces to gross_strokes is not allowed for incomplete events.")

    @property
    def course_handicap(self) -> int:
        raise SeasonViewIncompleteEventAccessError("Acces to course_handicap is not allowed for incomplete events.")

    @property
    def net_strokes(self) -> int:
        raise SeasonViewIncompleteEventAccessError("Acces to net_strokes is not allowed for incomplete events.")

    @property
    def gross_rank(self) -> int:
        raise SeasonViewIncompleteEventAccessError("Acces to gross_rank is not allowed for incomplete events.")

    @property
    def net_rank(self) -> int:
        raise SeasonViewIncompleteEventAccessError("Acces to net_rank is not allowed for incomplete events.")

    @property
    def gross_points(self) -> float:
        return self._gross_points

    @property
    def net_points(self) -> float:
        return self._net_points

    @property
    def event_points(self) -> float:
        return self._event_points

    @property
    def event_rank(self) -> int:
        return self._event_rank

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, SeasonViewWritePlayerIncompleteEvent):
            return NotImplemented

        return (
            self._name == other._name
            and self._gross_points == other._gross_points
            and self._net_points == other._net_points
            and self._event_points == other._event_points
            and self._event_rank == other._event_rank
        )


class SeasonViewWritePlayerCompleteEvent(SeasonViewWritePlayerEvent):
    def __init__(
        self,
        name: str,
        front_9_strokes: int,
        back_9_strokes: int,
        gross_strokes: int,
        course_handicap: int,
        net_strokes: int,
        gross_rank: int,
        net_rank: int,
        gross_points: float,
        net_points: float,
        event_points: float,
        event_rank: int,
    ) -> None:
        self._name = name
        self._front_9_strokes = front_9_strokes
        self._back_9_strokes = back_9_strokes
        self._gross_strokes = gross_strokes
        self._course_handicap = course_handicap
        self._net_strokes = net_strokes
        self._gross_rank = gross_rank
        self._net_rank = net_rank
        self._gross_points = gross_points
        self._net_points = net_points
        self._event_points = event_points
        self._event_rank = event_rank

    @property
    def is_complete_event(self) -> bool:
        return True

    @property
    def name(self) -> str:
        return self._name

    @property
    def front_9_strokes(self) -> int:
        return self._front_9_strokes

    @property
    def back_9_strokes(self) -> int:
        return self._back_9_strokes

    @property
    def gross_strokes(self) -> int:
        return self._gross_strokes

    @property
    def course_handicap(self) -> int:
        return self._course_handicap

    @property
    def net_strokes(self) -> int:
        return self._net_strokes

    @property
    def gross_rank(self) -> int:
        return self._gross_rank

    @property
    def net_rank(self) -> int:
        return self._net_rank

    @property
    def gross_points(self) -> float:
        return self._gross_points

    @property
    def net_points(self) -> float:
        return self._net_points

    @property
    def event_points(self) -> float:
        return self._event_points

    @property
    def event_rank(self) -> int:
        return self._event_rank

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, SeasonViewWritePlayerCompleteEvent):
            return NotImplemented

        return (
            self._name == other._name
            and self._front_9_strokes == other._front_9_strokes
            and self._back_9_strokes == other._back_9_strokes
            and self._gross_strokes == other._gross_strokes
            and self._course_handicap == other._course_handicap
            and self._net_strokes == other._net_strokes
            and self._gross_rank == other._gross_rank
            and self._net_rank == other._net_rank
            and self._gross_points == other._gross_points
            and self._net_points == other._net_points
            and self._event_points == other._event_points
            and self._event_rank == other._event_rank
        )


class SeasonViewWriteEvent(NamedTuple):
    name: str
    players: list[SeasonViewWritePlayerEvent]

    def get_player(self, player_name: str) -> SeasonViewWritePlayerEvent:
        for player in self.players:
            if player.name == player_name:
                return player

        raise KeyError(f"Player {player} cannot be found in write data for event {self.name}.")


class SeasonViewWriteData(NamedTuple):
    leaderboard: SeasonViewWriteLeaderboard
    events: list[SeasonViewWriteEvent]

    def get_event(self, event_name: str) -> SeasonViewWriteEvent:
        for event in self.events:
            if event.name == event_name:
                return event

        raise KeyError(f"Event {event} cannot be found in season write data.")
